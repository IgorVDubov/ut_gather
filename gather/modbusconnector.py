import asyncio
from abc import ABC, abstractmethod
from pymodbus.client.tcp import AsyncModbusTcpClient 

from bpacker import unpackCDABToFloat, unpackABCDToFloat

from . import myexceptions
from .consts import ValTypes 
from .logger import logger

class AsyncBaseModbusClient(ABC):
    ip = None
    port = None
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
        self.loop=loop
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
        return await self.connection.read_input_registers(address, regCount, unit=self.unit)
    async def readHoldingRegisters_F3(address:int, regCount:int, unit:int):...
    async def readDiscreteInputs_F2(address:int, regCount:int, unit:int):...
    async def writeCoil_F5(address:int, value:bool, unit:int):...
    async def writeWord_F6(address:int, value:int, unit:int):...
    
class AsyncModbusConnection(AsyncModbusClient):
    """
    AsyncModbusClient 
    inits AsyncModbusConnection
    metod: readInputs fuction 3 and 4
    format: AI=1 return float / DI=2 return [bitsArr]
    """
    AI=1
    DI=2
    LIST=0
    
    def __init__(self,client,unit,address,count,format,function=None,loop=None):
        self.address=address
        self.regCount=count
        self.unit=unit
        if format==ValTypes.AI:
            self.format=self.AI
        elif format==ValTypes.DI:
            self.format=self.DI
        elif format==ValTypes.LIST:
            self.format=self.LIST
        self.client=client
        self.function=function

        self.error=None
        self.connection=client.connection
        #logger.debug(f"Client ip:{ self.ip}, addr:{address} connection:{self.connection.connected} ")

    def __str__(self):
        return f'ip:{self.client.ip}, port:{self.client.port}, unit:{self.unit}, address:{self.address}, regCount:{self.regCount}, function:{self.function}'
    
    async def start(self):
        await self.connection.connect()
        
    async def close(self):
        await self.connection.close()

    async def read(self):
        connection=self.connection.protocol
        result=[]
        try:
            if self.function==4:
                readResult = await connection.read_input_registers(self.address, self.regCount, self.unit)
                if not(readResult.isError()):
                    if self.format==self.LIST:
                        result=readResult.registers
                    if self.format==self.DI:
                        result=[reg for reg in readResult.registers]
                    elif self.format==self.AI:
                        result=[unpackCDABToFloat (readResult.registers,2)]
                else:
                    # print ('*'*20,f'raise error:{readResult}')
                    self.error=readResult
                    raise myexceptions.ModbusException(readResult)
            elif self.function==3:
                readResult = await connection.read_holding_registers(self.address, self.regCount, self.unit)
                if not(readResult.isError()):
                    if self.format==self.LIST:
                        result=readResult.registers
                    if self.format==self.DI:
                        result=[reg for reg in readResult.registers]
                    if self.format==self.AI:
                        # result=[unpackCDABToFloat (readResult.registers,2)]
                        result=[unpackABCDToFloat (readResult.registers,2)]
                else:
                    # print ('*'*20,f'raise error:{readResult}')
                    self.error=readResult
                    raise myexceptions.ModbusException(readResult)
            elif self.function==2:
                readResult = await connection.read_discrete_inputs(self.address, self.regCount, self.unit)
                if not(readResult.isError()):
                    result = readResult.bits
                else:
                    self.error=readResult
                    # print ('*'*20,f'raise error:{readResult}')
                    raise myexceptions.ModbusException(readResult)
        except TimeoutError:
            self.error='Timeout Error '
            print(f'Timeout Error reading {self.client.ip}:{self.client.port}, addr={self.address}')
            result=None
        except AttributeError:
            self.error='Connection error'
            result=None
            # raise ModbusExceptions.ConnectionException(result)
        # print(f'from reader: {result}')
        lock = asyncio.Lock()
        async with lock:
            self.result=result
        
        return result

    async def writeRegister(self,reg:int,value):
        ...

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