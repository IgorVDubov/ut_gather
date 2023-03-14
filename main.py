#!/usr/bin/env python

import asyncio
import sys
from loguru import logger

import logger as loggerLib

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  #Если запускаем из под win    


import config
import settings
import scadaconfig as scada_config
import web.handlers as project_webserver_handlers
try:
    import init as project_init
except ModuleNotFoundError:
    project_init=None

from gather import db_interface
from gather.channels.channelbase import channel_base_init
from gather.exchangeserver import MBServerAdrMapInit, ModbusExchangeServer
from gather.mainloop import MainLoop
from gather.mutualcls import ChannelSubscriptionsList, DataContainer, EList, SubscriptChannelArg, WSClient
from gather.sourcepool import SourcePool
from gather.webserver.webconnector import setHTTPServer



def init():
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if len(modules:=scada_config.module_list):
        source_pool=SourcePool(modules,loop)
    else:
        source_pool=None 
    channel_base=channel_base_init(scada_config.channels_config)
    if project_init:
        project_init.init(channel_base)
    exchange_bindings = MBServerAdrMapInit(channel_base, scada_config.mb_server_addr_map)
    modbus_exchange_server=ModbusExchangeServer(
                    scada_config.mb_server_addr_map, 
                    channel_base, 
                    exchange_bindings,
                    config.modbus_server_params['host'], 
                    config.modbus_server_params['port'],
                    loop=loop)
    http_params=config.http_server_params
    http_params.update(settings.web_server_path_params)

 # type: ignore    
    subscrptions:ChannelSubscriptionsList[SubscriptChannelArg]=ChannelSubscriptionsList()
    ws_clients:EList=EList()
    http_server=setHTTPServer(  http_params, 
                                project_webserver_handlers.handlers,
                                DataContainer(
                                        config.users,
                                        channel_base, 
                                        subscrptions, 
                                        ws_clients)
                            )
    DBInterface=db_interface.DBInterface(config.DB_TYPE, config.DB_PARAMS)
    #HTTPServer=None
    print ('Sources')
    print (source_pool)
    print ('Channels:')
    print(channel_base)
    # import json
    # print(json.dumps([channel_base.nodesToDictFull()], sort_keys=True, indent=4))
    print(f'Modbus Exchange Server: {config.modbus_server_params["host"]}, {config.modbus_server_params["port"]}')
    print('ExchangeBindings')
    print(exchange_bindings)
    print('HTTPServer:')
    print(f"host:{http_params.get('host')}:{http_params.get('port')}, wsserver:{http_params.get('wsserver')}, " if http_server else None )
    
    main_loop=MainLoop( loop, 
                        source_pool, 
                        channel_base, 
                        modbus_exchange_server, 
                        http_server, 
                        DBInterface)
    logger.info ('init done')
    return main_loop


def main():
    loggerLib.loggerInit('ERROR')
    logger.info('Starting........')
    main_loop=init()
    main_loop.start()
    

if __name__=='__main__':
    main()
    # test_component()
    