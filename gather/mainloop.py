import asyncio
import json
from datetime import datetime
from time import time
from typing import Any, List, Optional


from . import defaults
from .channels import channels
from .channels.channelbase import ChannelsBase
from .consts import DbNames
# from .interfaces.db import dbinterface
from  gather.interfaces.db.dbinterface import DBCommandProcessor
from .exchangeserver import ExchangeServer
from loguru import logger

from .mutualcls import SubscriptChannelArg
from .sourcepool import SourcePool
from .webserver.webconnector import CURR_HTTP_SERVER_TYPE


class MainLoop():
    loop: asyncio.AbstractEventLoop
    source_pool: SourcePool | None
    channel_base: ChannelsBase
    exchange_server: ExchangeServer | None
    HTTP_server: CURR_HTTP_SERVER_TYPE | None
    # db_interface:dbinterface.DBInterface|None
    db_processor: DBCommandProcessor | None
    db_quie: asyncio.Queue
    subsriptions: Any
    ws_clients: Any
    
    def __init__(self,  loop: asyncio.AbstractEventLoop,
                 source_pool: SourcePool | None,
                 channel_base: ChannelsBase,
                 exchange_server: ExchangeServer | None = None,
                 HTTP_server: CURR_HTTP_SERVER_TYPE | None = None,
                 # db_interface:(dbinterface.DBInterface|None)=None):
                 db_processor: DBCommandProcessor | None = None):
        '''
        source_pool: source pool
        channeBlase: channe Blase
        exchange_server:  ModBus exchange server
        HTTP_server: web server
        db_interface: database interface
        '''
        self.loop = loop
        self.cancelEvent = asyncio.Event()
        self.source_pool = source_pool
        self.channel_base = channel_base
        if self.source_pool:
            self.source_pool.readAllOneTime()                    # TODO проверить как работает если нет доступа к source
                                                                 #      или заполнять Null чтобы первый раз сработало по изменению
            for node in (channel for channel in self.channel_base.channels
                         if isinstance(channel, channels.Node)):
                for source in self.source_pool.sources:
                    if source.id == node.sourceId:
                        node.source = source
                        break
        # for node in (channel for channel in self.channel_base.channels if isinstance(channel,classes.Node)):
        #     if node.source==None and node.sourceId!=None :          # если указан sourceId, но не привязан source выключаем из базы каналов
        #         print(f'!!!!!!!!!!Cant find source {node.sourceId} for node {node.id}, remove from pool')
        #         self.channel_base.channels.pop(self.channel_base.channels.index(node))

        #self.cancelEvent=asyncio.Event()
        self.exchange_server = exchange_server
        if exchange_server is not None:
            self.exchange_bindings = exchange_server.exchange_bindings if exchange_server.exchange_bindings is not None else {}
        self.HTTP_server = HTTP_server
        if HTTP_server is not None:
            self.subsriptions = HTTP_server.request_callback.data.subsriptions  # TODO для tornado проверить или переместить для других
            self.ws_clients = HTTP_server.request_callback.data.ws_clients      # TODO для tornado проверить или переместить для других
        else:
            self.subsriptions = []
            self.ws_clients = []
        self.db_quie = channel_base.db_quie
        # self.db_interface=db_interface
        self.db_processor = db_processor
        self.set_tasks()
            
    
    def start(self):   
        if self.exchange_server:
            self.exchange_server.start()
        self.start_loop()

    def start_loop(self):
        try:
            logger.info ('start main loop')
            self.loop.run_forever()
            print ('stop main loop')
        except KeyboardInterrupt:
            logger.info ('************* KeyboardInterrupt *******************')
            self.cancelEvent.set()
            for task in asyncio.all_tasks(loop=self.loop):
                print(f'Task {task.get_name()} cancelled')
                task.cancel()
            
        finally:
            if self.HTTP_server:
                print('HTTP_server stop')
                self.HTTP_server.stop()
                asyncio.run(self.HTTP_server.close_all_connections())
                if self.source_pool:
                    print('Moddbus close_sources')
                    asyncio.run(self.source_pool.close_sources())
                    # self.loop.run_until_complete(self.source_pool.close_sources())
            self.loop.stop()
            print ('************* main loop close *******************')

    def set_tasks(self):
            self.loop.create_task(self.calc_channel_base_loop(), name='reader')
            # if self.db_interface:
            if self.db_processor:
                self.loop.create_task(self.db_requester_loop(), name='db_requester_loop')
    
    async def db_requester_loop(self):
        while True:
            while not self.db_quie.empty():
                # querry=self.db_quie.get_nowait()
                querry_command=self.db_quie.get_nowait()
                logger.info(f'db_quie:{querry_command}')
                # getattr(self.db_interface, querry['func'].__name__)(querry['sql'], querry['params'])
                self.db_processor.call(querry_command)
                # match querry:
                #     case {'type':DbNames.INSERT, 'sql':sql_txt,'params':sql_params}:
                #         logger.info (f'write to bd here:{sql_txt=}, {sql_params=} ')
                #         # self.db_interface.execSQL(req.get('questType'),req.get('sql'),req.get('params'))
                #     case {'type':DbNames.DBC, 'querry_func':querry_func,'params':querry_params}:
                #         logger.info(f'write to bd here:{querry_func}, {querry_params=} ')
                #         self.db_interface.exec_querry_func(querry_func, querry_params)
                #     case _: raise ValueError(f'invalid db_quie type:{querry}')
            await asyncio.sleep(defaults.DB_PERIOD)

    async def calc_channel_base_loop(self):
        # print ('start results Reader')
        # try:
            while True:
                change_subscriptions = []
                before = time()
                for channel in self.channel_base.channels:                          #calc Channels
                    channel()
                    if subscr_channel := next((s_channel for s_channel in self.subsriptions if s_channel.channel == channel), None):
                        arg_value = subscr_channel.channel.get_arg(subscr_channel.argument)
                        if arg_value != subscr_channel.prev_value:
                            change_subscriptions.append(subscr_channel)
                            subscr_channel.prev_value = arg_value

                                    
                for channelAttr, binding in self.exchange_bindings.items():           #set vaues for Modbus Excange Server
                    self.exchange_server.setValue(channelAttr, binding.value)
                
                # if len(self.HTTP_server.request_callback.wsClients):
                #     for wsClient in self.HTTP_server.request_callback.wsClients:
                #         wsClient.write_message(json.dumps(self.channel_base.toDict(), default=str))

                delay=defaults.CHANNELBASE_CALC_PERIOD - (time()-before)
                if delay<=0:
                    logger.warning(f'Not enough time for channels calc loop, {len(self.channel_base.channels)} channels ')
                # print(f'in mail loop:{self.subscrptions}')
                # print(f'{change_subscriptions=}')
                for ws_client in self.ws_clients:
                    for_send=[]
                    for subscr in ws_client.subscriptions:
                        if subscr in change_subscriptions:
                            send_data=subscr.to_dict()
                            send_data.update({'time':(datetime.now()).strftime('%Y-%m-%dT%H:%M:%S')})
                            for_send.append(send_data)
                    if len(for_send):
                        print(f'!!!!!!!!!!!!!!!!!!!{for_send}')
                        ws_client.client.write_message(json.dumps(for_send, default=str))
                await asyncio.sleep(delay)

        
        # except asyncio.CancelledError:
        #     print('CancelledEvent in calc_channel_base_loop')
        # except Exception as e:
        #     logger.error(e)
        # finally:
        #     print('calc_channel_base_loop stops by exception ')
        #     return

        
