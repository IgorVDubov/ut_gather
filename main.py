#!/usr/bin/env python
import sys

from gathercore.app import app_builder
from gathercore.mylib import logger as loggerLib
from loguru import logger

if sys.platform == "win32":  # Если запускаем из под win
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
sys.path.append("/gathercore")

import config
import scadaconfig as scada_config
import settings
import web.handlers as project_webserver_handlers
from gathercore.interfaces.db import create_db_interface
from init import init_args

# project_init_func - функция инициализации проекта,
# которая запускается после формирования
# базы каналов и databus перед стартом основного цикла,
# параметром в функцию передается databus

try:
    from init import init as project_init_func
except ModuleNotFoundError | ImportError:
    project_init_func = None


def main():
    loggerLib.loggerInit("DEBUG", "error", ("PROG",))
    logger.info("Starting........")
    # создаем интерфейс к базе данных
    db_interface = create_db_interface("db_interface", config.DB_TYPE, config.DB_PARAMS)
    # создаем приложение
    app = app_builder(
        interfaces=scada_config.interfaces,
        source_list=scada_config.source_list,
        channels_config=scada_config.channels_config,
        modbus_server_params=config.modbus_server_params,
        mb_server_addr_map=scada_config.mb_server_addr_map,
        project_webserver_params=config.http_server_params,
        project_webserver_handlers=project_webserver_handlers.handlers,
        project_web_users=settings.users,
        project_init_func=project_init_func,
        databus_objects=[db_interface],
    )
    # добавляем словарь websocket клиентов для панелей оператора на станках
    # {machine_id: web_socket_client}
    app.databus.add_object("machine_WS_client", dict())
    # Инициализация необходимых аргументов через БД settings
    init_args(
        app.databus.get_object("db_interface"), app.channel_base, settings.PROJECTS_IDS
    )
    # запуск app
    app.start()


if __name__ == "__main__":
    main()
    # test_component()
