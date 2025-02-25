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
import settings
import scadaconfig_V as scada_config
from gathercore.interfaces.db import create_db_interface
import web.handlers as project_webserver_handlers
from init import init_args

try:
    from init import init as project_init_func
except (ModuleNotFoundError | ImportError):
    project_init_func = None

def main():
    loggerLib.loggerInit('DEBUG', 'error', ('PROG',))
    logger.info('Starting........')
    db_interface = create_db_interface('db_interface',
                                       config.DB_TYPE,
                                       config.DB_PARAMS
                                       )
    app = app_builder(
                source_list=scada_config.source_list,
                channels_config=scada_config.channels_config,
                mb_server_addr_map=scada_config.mb_server_addr_map,
                modbus_server_params=config.modbus_server_params,
                project_webserver_params=config.http_server_params,
                project_webserver_handlers=project_webserver_handlers.handlers,
                project_web_users=settings.users,
                project_init_func=project_init_func,
                databus_objects=[db_interface]
                )
    app.databus.add_object('machine_WS_client', dict()) # {machine_id: web_socket_client}
    init_args(
        app.databus.get_object('db_interface'),
        app.channel_base
        )
    app.start()


if __name__ == '__main__':
    main()
    # test_component()

