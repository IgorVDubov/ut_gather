import asyncio

from . import aclient
from ...consts import Formats
from ...myexceptions import ModbusException


class AModbusConnection():
    """
    AsyncModbusClient 
    inits AsyncModbusConnection
    metod: readInputs fuction 3 and 4
    format: AI=1 return float / DI=2 return [bitsArr]
    """

    client: aclient.ABaseModbusClient
    addr_pool: Formats
    address: int
    reg_count: int
    unit: int
    bytes_order: Formats | None

    def __init__(self,
                 client: aclient.ABaseModbusClient,
                 addr_pool: Formats,
                 address: int,
                 reg_count: int,
                 unit: int,
                 bytes_order=None):
        self.client = client
        self.addr_pool = addr_pool
        self.address = address
        self.reg_count = reg_count
        self.unit = unit
        self.format = format
        if bytes_order is None:
            self.bytes_order = None
        else:
            self.bytes_order = bytes_order

        self.error = None
        # logger.debug(f"Client ip:{ self.ip}, addr:{address} connection:{self.connection.connected} ")

    def __str__(self):
        return f'''ip:{self.client.ip}, port:{self.client.port}, unit:{self.unit}, {["", "CO", "DI", "HR", "IR"][self.addr_pool]}:address:{self.address}, regCount:{self.reg_count}'''

    @property
    def connected(self) -> bool:
        return self.client.connected

    async def start(self):
        await self.client.start()

    async def close(self):
        await self.client.close()
        
    def _format_result(self, result):
        raise NotImplemented
    
    async def read(self) -> list[int] | list[bool] | None:
        result = []
        try:
            if self.client.connected is not None:
                result = None
                match self.addr_pool:
                    case Formats.CO:
                        result = await self.client.read_co(self.address, self.reg_count, self.unit)
                    case Formats.DI:
                        result = await self.client.read_di(self.address, self.reg_count, self.unit)
                    case Formats.HR:
                        result = await self.client.read_hr(self.address, self.reg_count, self.unit)
                    case Formats.IR:
                        result = await self.client.read_ir(self.address, self.reg_count, self.unit)
                # if self.bytes_order is not None:
                #     result = self._format_result(result)
        
        except ModbusException as e:
            self.error = 'Mobus read Error '
            print(f'Mobus Error reading {self.client.ip}:{self.client.port}, addr={self.address}: {e}')
            result = None
        except TimeoutError as e:
            self.error = 'Timeout Error '
            print(f'Timeout Error reading {self.client.ip}:{self.client.port}, addr={self.address}: {e}')
            result = None
        except AttributeError:
            self.error = 'Connection error'
            result = None
        
        return result

    async def writeRegister(self, value): 
        try:
            if self.client.connected is not None:
                # if self.bytes_order is None:          # добавить обработку bytes_order в обычном клиенте
                match self.addr_pool:
                    case Formats.CO:
                        await self.client.write_co(self.address, value, self.unit)
                    case Formats.DI:
                        raise ModbusException('cant write DI register')
                    case Formats.HR:
                        await self.client.write_hr(self.address, value, self.unit)
                    case Formats.IR:
                        raise ModbusException('cant write Input Register')
        except ModbusException as e:
            self.error = 'Mobus write Error '
            print(f'Mobus Error writing {self.client.ip}:{self.client.port}, addr={self.address}: {e}')

    async def write_many(self, value_list: list[bool | int]):
        raise NotImplemented
    
