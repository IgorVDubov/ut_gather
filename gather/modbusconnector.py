import asyncio
from abc import ABC, abstractmethod
from pymodbus.client.tcp import AsyncModbusTcpClient, ModbusClientProtocol 
from typing import Callable

import bpacker 

from . import myexceptions
from .consts import ValTypes, Formats, ModbusFuncs
from .defaults import  FLOAT_ACCURACY, DEFAULT_4_BYTES_ORDER, DEFAULT_2_BYTES_ORDER
from .logger import logger

class AsyncBaseModbusClient(ABC):
    ip: str = None
    port: int = None
    connection = None

    def start():...
    @property
    def connected(self)->bool:...
    async def readInputRegisters_F4(address: int, regCount:int, unit:int):...
    async def readHoldingRegisters_F3(address: int, regCount:int, unit:int):...
    async def readDiscreteInputs_F2(address: int, regCount:int, unit:int):...
    async def writeCoil_F5(address: int, value:bool, unit:int):...
    async def writeWord_F6(address: int, value:int, unit:int):...

class AsyncModbusClient(AsyncBaseModbusClient):
    def __init__(self,ip,port,loop=None):
        self.ip=ip
        self.port=port
        # self.loop=loop
        self.connection = AsyncModbusTcpClient(self.ip, self.port)
    

    async def start(self):
            await self.connection.connect()
            logger.info(f'Client ip={self.ip}:{self.port} starts? Connection {self.connection.connected}')
    
    async def close(self):
            await self.connection.close()
            logger.info(f'Client ip={self.ip}:{self.port} starts? Connection {self.connection.connected}')
       

    @property
    def connected(self):
        if self.connection:
            return self.connection.connected
    async def readInputRegisters_F4(self, address:int, regCount:int, unit:int):
        return await self.connection.read_input_registers(address, regCount, self.unit)
    async def readHoldingRegisters_F3(address: int, regCount: int, unit: int):...
    async def readDiscreteInputs_F2(address: int, regCount: int, unit: int):...
    async def writeCoil_F5(address: int, value: bool, unit: int):...
    async def writeWord_F6(address: int, value: int, unit: int):...
   
    
class AsyncModbusConnection():
    """
    AsyncModbusClient 
    inits AsyncModbusConnection
    metod: readInputs fuction 3 and 4
    format: AI=1 return float / DI=2 return [bitsArr]
    """
    
    client: AsyncModbusClient
    unit: int
    address: str
    count: int
    format: ValTypes
    bytes_order: Formats | None
    function: Callable | None 
    
    def __init__(self, client: AsyncModbusClient, unit: int, address: str,
                 count: int, format: ValTypes, bytes_order: Formats | None,
                 function: Callable | None = None):
        self.address = address
        self.unit = unit
        if function is not None:
            self.function = function
        else:
            raise myexceptions.ConfigException(f'No read/write function for {AsyncModbusClient} ')
        match self.function:
            case ModbusFuncs.READ_CO:
                count = 1
                format = ValTypes.BIT
            case ModbusFuncs.READ_DI:
                if count is None:
                    count = 1
                    format = ValTypes.DI
            case ModbusFuncs.READ_HR:
                if format in (ValTypes.INT32, ValTypes.FLOAT):
                    count = 2
                elif format in (ValTypes.INT16, None):
                    count = 1
            case ModbusFuncs.READ_IR:
                if format in (ValTypes.INT32, ValTypes.FLOAT):
                    count = 2
                elif format in (ValTypes.INT16, None):
                    count = 1
            
        self.regCount = count
        self.format = format
        if bytes_order is None:
            if format in (ValTypes.INT, ValTypes.DI, ValTypes.LIST):
                self.bytes_order = DEFAULT_2_BYTES_ORDER
            elif format in (ValTypes.FLOAT, ValTypes.AI):
                self.bytes_order = DEFAULT_4_BYTES_ORDER
        else:
            self.bytes_order = bytes_order
        self.client = client

        self.error = None
        self.connection: AsyncModbusTcpClient = client.connection
        #logger.debug(f"Client ip:{ self.ip}, addr:{address} connection:{self.connection.connected} ")

    def __str__(self):
        return f'ip:{self.client.ip}, port:{self.client.port}, unit:{self.unit}, address:{self.address}, regCount:{self.regCount}, function:{self.function}'
    
    @property
    def connected(self) -> bool:
        return self.connection.connected
    
    async def start(self):
        await self.connection.connect()
        
    async def close(self):
        await self.connection.close()
    
    def _format_result(self, result_list: list[int | bool]) -> list[int] | list[float] | list[bool]:
        result = result_list
        
        if self.format == ValTypes.BIT:
            result = result_list
        elif self.format == ValTypes.LIST:
            if self.bytes_order == Formats.BA and self.regCount == 1:
                result = result_list[::-1]
            elif self.bytes_order == Formats.CDAB and self.regCount == 2:
                A, B, C, D = result_list
                result: list[int] = [C, D, A, B]
            else:
                result = result_list
        elif self.format == ValTypes.DI:
            if self.function == ModbusFuncs.READ_DI:
                result = result_list
            else:
                if self.bytes_order == Formats.BA and self.regCount == 2:
                    result = bpacker.int_2_bit_list(1) + bpacker.int_2_bit_list(0)
                else:
                    result: list[int] = list()
                    for i in result_list:
                        result.extend(bpacker.int_2_bit_list(i))
        elif self.format == ValTypes.INT16:
            if self.bytes_order == Formats.BA:
                result = [bpacker.convert_int_AB2BA(result_list[0])]
            else:
                result: list[int] = result_list[0]
        elif self.format in (ValTypes.FLOAT, ValTypes.FLOAT):
            if self.bytes_order is None:
                self.bytes_order = DEFAULT_4_BYTES_ORDER
            if self.bytes_order == Formats.CDAB:
                result = [bpacker.CDAB_unpack_2_float(result_list, FLOAT_ACCURACY)]
            elif self.bytes_order == Formats.ABCD:
                result = [bpacker.ABCD_unpack_2_float(result_list, FLOAT_ACCURACY)]
        return result
    
    def _get_reader_result(self, read_result, function: int) -> list[bool | int]:
        if read_result is not None and read_result.isError() == False:
            if function in (3, 4):
                return read_result.registers
            if function in (2,):
                return read_result.bits
        else:
            self.error = read_result
            raise myexceptions.ModbusException(read_result)
    
    
    async def read(self) -> list[int] | list[float] | list[bool] | None:
        connection: ModbusClientProtocol | None = self.connection.protocol
        result = []
        try:
            if connection is not None:
                read_result = None
                if self.function == 4:
                    read_result = await connection.read_input_registers(self.address, self.regCount, self.unit)
                elif self.function == 3:
                    read_result = await connection.read_holding_registers(self.address, self.regCount, self.unit)
                elif self.function == 2:
                    read_result = await connection.read_discrete_inputs(self.address, self.regCount, self.unit)
                result = self._get_reader_result(read_result, self.function)
                result = self._format_result(result)
                
                
            
        except TimeoutError:
            self.error = 'Timeout Error '
            print(f'Timeout Error reading {self.client.ip}:{self.client.port}, addr={self.address}')
            result = None
        except AttributeError:
            self.error = 'Connection error'
            result = None
            # raise ModbusExceptions.ConnectionException(result)
        # print(f'from reader: {result}')
        lock = asyncio.Lock()
        async with lock:
            self.result = result
        
        return result

    async def writeRegister(self, reg:int, value):
        ...


#-----------------------  trsting ------------------------------------

async def run():
    # import logging
    # FORMAT = ('%(asctime)-15s %(threadName)-15s'
    #         ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
    # logging.basicConfig(format=FORMAT)
    # log = logging.getLogger()
    # log.setLevel(logging.DEBUG)
    from time import time
    from pymodbus.constants import Defaults
    Defaults.Timeout = 10
    begin=time()
    r=100
    с=AsyncModbusClient('192.168.1.200',503)
    client1= AsyncModbusConnection(с,0x0,1,2,ValTypes.AI,function=3)
    client3= AsyncModbusConnection(с,0x0,2,1,ValTypes.DI,function=3)
    print (client1)
    await client1.start()
    print (client1.connected)
    client2= AsyncModbusConnection(AsyncModbusClient('192.168.1.200',502),0x1,1,1,DI,function=3)
    print (client2)
    await client2.start()
    print (client2.connected)
    for _ in range(r):
        try:
            print(await client1.read())
            print(await client2.read())
            print(await client3.read())
        except Exception as e:
            print(e)
    # finally:
    print ('closing client')
    await client1.connection.close()
    await client2.connection.close()
    end1=time()-begin

    
    print(f'{end1=}, ')

if __name__ == '__main__':
    asyncio.run(run(), debug=True)    