#!/usr/bin/env python
import sys
from platform import python_version

from gathercore.app import app_builder
from gathercore.consts import Direction, InterfaceTypes, ModbusFuncs, ValTypes
from gathercore.defaults import default_params
from gathercore.models import ModbusSourceParams, ModbusTCPInterfaceParams
from gathercore.mylib import logger as loggerLib
from loguru import logger

if sys.platform == "win32":  # Если запускаем из под win
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
sys.path.append("d:/projects/gathercore/gathercore/")

print(f"{python_version()=}")


interfaces = [
    {
        "name": "sinthepon_cs3102",
        "type": InterfaceTypes.MODBUS_TCP,
        "params": ModbusTCPInterfaceParams(ip="127.0.0.1", port=502),
    },
]

sources = [
    {
        "name": "synth_counters_reset_out",
        "interface": "sinthepon_cs3102",
        "params": ModbusSourceParams(
            direction=Direction.WRITE,
            unit=0x1,
            address=0,
            function=ModbusFuncs.WRITE_CO,
            count=1,
            format=ValTypes.BIT,
        ),
    },
    {
        "name": "synth_counters_reset_in",
        "interface": "sinthepon_cs3102",
        "params": ModbusSourceParams(
            direction=Direction.READ,
            unit=0x1,
            address=0,
            function=ModbusFuncs.READ_CO,
            count=1,
            format=ValTypes.BIT,
        ),
    },
]


def handler(vars):
    if vars.write:
        print("reset write")
        vars.write = False


channels = [
    {
        "name": "out",  # Линия Синтепона запись сигнала сброса счетчиков выхода продукции
        "source": "synth_counters_reset_out",
        "handler": handler,
        "args": {"in": "in.result", "result": "out.result", "write": "write.result_in"},
    },
    {
        "name": "in",  # Линия Синтепона чтение сигнала сброса счетчиков выхода продукции
        "source": "synth_counters_reset_in",
    },
    {
        "name": "write",  # Линия Синтепона чтение сигнала сброса счетчиков выхода продукции
    },
]


def main():
    app_params = default_params
    app_params.debug_state = True
    loggerLib.loggerInit("DEBUG", "error", ("PROG",))
    logger.info("Starting........")
    # создаем приложение
    app = app_builder(
        interfaces=interfaces,
        source_list=sources,
        channels_config=channels,
        default_params=app_params,
    )
    app.start()


if __name__ == "__main__":
    main()
