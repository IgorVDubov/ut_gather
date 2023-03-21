#!/usr/bin/env python

import asyncio
import os.path
import sys
import importlib
from loguru import logger

import logger as loggerLib

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  #Если запускаем из под win    


import defaults

scada_config=importlib.import_module('projects.'+defaults.PROJECT['path']+'.scadaconfig')
try:
    project_init=importlib.import_module('projects.'+defaults.PROJECT['path']+'.init1')
except ModuleNotFoundError:
    project_init=None
import channels.channels
import db_interface
from channels.channelbase import channel_base_init
from exchangeserver import MBServerAdrMapInit, ModbusExchangeServer
from mainloop import MainLoop
from mutualcls import (ChannelSubscriptionsList, Data, EList,
                       SubscriptChannelArg, WSClient)
from sourcepool import SourcePool
from webserver.webconnector import setHTTPServer
project_webserver_settings=importlib.import_module('projects.'+defaults.PROJECT['path']+'.web.server_config')
project_webserver_handlers=importlib.import_module('projects.'+defaults.PROJECT['path']+'.web.handlers')


def init():
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    db_quie=asyncio.Queue()
    if len(modules:=scada_config.module_list):
        source_pool=SourcePool(modules,loop)
    else:
        source_pool=None 
    channel_base=channel_base_init(scada_config.channels_config, db_quie)
    if project_init:
        project_init.init(channel_base)
    exchange_bindings = MBServerAdrMapInit(channel_base,scada_config.mb_server_addr_map)
    modbus_exchange_server=ModbusExchangeServer(
                    scada_config.mb_server_addr_map, 
                    channel_base, defaults.modbus_server_params['host'], 
                    defaults.modbus_server_params['port'],
                    loop=loop)
    http_params=defaults.http_server_params
    # http_params.update({'path':os.path.join(os.path.dirname(__file__),'webserver', 'webdata')})
    http_params.update({'path':defaults.PATH_TO_PROJECT})
    web_settings = project_webserver_settings.get_config(http_params)
    web_handlers=project_webserver_handlers.handlers

    sbscrptions:ChannelSubscriptionsList[SubscriptChannelArg]=ChannelSubscriptionsList()
    ws_clients:EList(WSClient)=EList()
    http_server=setHTTPServer(  http_params, 
                                web_settings,
                                web_handlers,
                                Data(defaults.users,
                                    channel_base, 
                                    sbscrptions, 
                                    ws_clients))
    DBInterface=db_interface.DBInterface(defaults.DB_TYPE, defaults.DB_PARAMS)
    #HTTPServer=None
    print ('Sources')
    print (source_pool)
    print ('Channels:')
    print(channel_base)
    # import json
    # print(json.dumps([channel_base.nodesToDictFull()], sort_keys=True, indent=4))
    print(f'Modbus Exchange Server: {defaults.modbus_server_params["host"]}, {defaults.modbus_server_params["port"]}')
    print('ExchangeBindings')
    print(exchange_bindings)
    print('HTTPServer:')
    print(f"host:{http_params.get('host')}:{http_params.get('port')}, wsserver:{http_params.get('wsserver')}, " if http_server else None )
    
    main_loop=MainLoop( loop, 
                        source_pool, 
                        channel_base, 
                        sbscrptions, 
                        ws_clients,
                        modbus_exchange_server, 
                        exchange_bindings, 
                        http_server, 
                        db_quie, 
                        DBInterface)
    logger.info ('init done')
    return main_loop

def test_component():               #TODO dev, убрать
    loop=asyncio.get_event_loop()
    loggerLib.loggerInit('ERROR')
    logger.info('Starting........')
    httpParams=defaults.http_server_params
    channel_base=None
    http_server=setHTTPServer(httpParams, channels.Data(defaults.users,channel_base))
    loop.run_forever()

def main():
    loggerLib.loggerInit('ERROR')
    logger.info('Starting........')
    main_loop=init()
    main_loop.start()
    

if __name__=='__main__':
    main()
    # test_component()
    