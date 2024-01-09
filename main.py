#!/usr/bin/env python


from gathercore.app import app_builder

from gathercore.mylib import logger as loggerLib
from loguru import logger

import sys
if sys.platform == 'win32':                 # Если запускаем из под win
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
sys.path.append("/gathercore")

import config
import scadaconfig as scada_config
import web.handlers as project_webserver_handlers

try:
    from init import init as project_init_func
except (ModuleNotFoundError | ImportError):
    project_init_func = None

def main():
    loggerLib.loggerInit('ERROR')
    logger.info('Starting........')
    app = app_builder(
                module_list=scada_config.module_list,
                channels_config=scada_config.channels_config,
                mb_server_addr_map=scada_config.mb_server_addr_map,
                modbus_server_host=config.modbus_server_params['host'],
                modbus_server_port=config.modbus_server_params['port'],
                project_webserver_params=config.http_server_params,
                project_webserver_handlers=project_webserver_handlers.handlers,
                project_web_users=config.users,
                project_init_func=project_init_func,
                core_webadmin_params=config.core_webadmin_params,
                db_type=config.DB_TYPE,
                db_params=config.DB_PARAMS
                )
    app.start()


if __name__ == '__main__':
    main()
    # test_component()

