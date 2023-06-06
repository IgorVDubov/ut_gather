from loguru import logger
from abc import ABC
from pymodbus.client.tcp import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse

from ... import myexceptions

class ABaseModbusClient(ABC):
    ip: str
    port: int

    def start(self): ...
    def close(self): ...
    @property
    def connected(self) -> bool: ...
    async def read_co(self, address: int, reg_count: int, unit: int): ...
    async def read_di(self, address: int, reg_count: int, unit: int): ...
    async def read_ir(self, address: int, reg_count: int, unit: int): ...
    async def read_hr(self, address: int, reg_count: int, unit: int): ...
    async def write_co(self, address: int, value: bool, unit: int): ...
    async def write_hr(self, address: int, value: int, unit: int): ...


class AsyncModbusClient(ABaseModbusClient):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connection = AsyncModbusTcpClient(self.ip, self.port)

    def __str__(self) -> str:
        return f'AsyncModbusClient:{self.ip}:{self.port}, status:{"OPEN" if self.connected else "CLOSE"}'
    
    async def start(self):
        await self.connection.connect()
        logger.info(
            f'Client ip={self.ip}:{self.port} connection {self.connection.connected}')

    async def close(self):
        await self.connection.close()
        logger.info(
            f'Client ip={self.ip}:{self.port} connection {self.connection.connected}')

    @property
    def connected(self):
        if self.connection:
            return self.connection.connected

    @staticmethod
    async def _async_template_call(read_func, args):
        """async modbus call, with exceptions process"""
        try:
            read_result = await read_func(*args)
        except ModbusException as exc:
            raise myexceptions.ModbusException(exc)
        if read_result.isError():
            raise myexceptions.ModbusException(
                "ERROR: pymodbus returned an error!")
        if isinstance(read_result, ExceptionResponse):
            raise myexceptions.ModbusException(
                "ERROR: received exception from device {rr}!")
        return read_result

    async def read_co(self, address: int, reg_count: int, unit: int):
        result = await self._async_template_call(self.connection.read_coils,
                                               (address, reg_count, unit))
        return result.bits

    async def read_di(self, address: int, reg_count: int, unit: int):
        result = await self._async_template_call(self.connection.read_discrete_inputs,
                                               (address, reg_count, unit))
        return result.bits

    async def read_ir(self, address: int, reg_count: int, unit: int):
        result = await self._async_template_call(self.connection.read_input_registers,
                                               (address, reg_count, unit))
        return result.registers
    async def read_hr(self, address: int, reg_count: int, unit: int):
        result = await self._async_template_call(self.connection.read_holding_registers,
                                               (address, reg_count, unit))
        return result.registers
    
    async def write_co(self, address: int, value: bool | list, unit: int):
        if isinstance(value, list):
            shift = 0
            for val in value:
                await self._async_template_call(self.connection.write_coil,
                                                (address + shift, val, unit))
                shift += 1
        elif isinstance(value, bool):        
            await self._async_template_call(self.connection.write_coil,
                                            (address, value, unit))

    async def write_hr(self, address: int, value: list | int, unit: int):
        if isinstance(value, list):
            shift = 0
            for val in value:
                await self._async_template_call(self.connection.write_register,
                                                (address + shift, val, unit))
                shift += 1
        elif isinstance(value, int):        
            await self._async_template_call(self.connection.write_register,
                                            (address, value, unit))
