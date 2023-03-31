import asyncio
from abc import ABC, abstractmethod
from time import time

from .consts import SourceTypes
from . import modbusconnector
from .logger import logger
from . import myexceptions

class BaseSource(ABC):
    id=None
    format=None
    result=None
    period=None
    dost=None
    error=None

    @abstractmethod
    def read(self):...

class Source(BaseSource):
    def __init__(self, module: dict, exist_clients: dict[modbusconnector.AsyncModbusClient], loop):
        try:
            self.id = module['id']
            self.period = module.get('period')
            self.result = None
            self.format = module.get('format')
            self.order = module.get('order')
            use_exist_client = False
            if module['type'] ==  SourceTypes.MODBUS_TCP:
                for client in exist_clients:
                    if module['ip'] == client.ip and module['port'] == client.port:             # TODO если будут использоваться НЕ только TCP клиенты поменять алгоритм поиска существующего клиента
                        new_client = client
                        use_exist_client = True
                        break
                if not use_exist_client:
                        new_client = modbusconnector.AsyncModbusClient(module['ip'],module['port'])
                self.connection = modbusconnector.AsyncModbusConnection(new_client, 
                                                                        module['unit'],
                                                                        module['address'],
                                                                        module.get('count'),
                                                                        self.format,
                                                                        self.order,
                                                                        module.get('function')
                )
            else:
                raise myexceptions.ConfigException (f'No class for type {module["type"]}')
        except KeyError:
            raise myexceptions.ConfigException (f'Not enoth data fields in mopdule config srting {module}')
        
    def get_client(self):
        return self.connection.client

    async def read(self):
        try:
            self.dost=self.connection.connected
            self.result= await self.connection.read()
        except myexceptions.SourceException as e:
            self.error=e
            self.result=None
        return self.result
    
    def __str__(self):
        return f' {id(self)}    id:{self.id}, format:{self.format}, period:{self.period}s, conn_id:{id(self.connection.client)} {self.connection.__str__()} {"-OK" if self.connection.connected else "-N/A"}'

class SourcePool(object):
    def __init__(self,modules,loop=None):
        self.clients=[]
        self.sources=[]
        #self.results=[]
        for module in modules:
            source=Source(module, self.clients, loop)
            client=source.get_client()
            if client and client not in self.clients:
                self.clients.append(client)
            self.sources.append(source)             #TODO ????? помещать сюда только если успешный инит клиента и тест чтения по адресу
        if loop ==None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop=loop
        self.loop.run_until_complete(self.start_sources())
        self.setTasks()
        
    async def start_sources(self):
        for client in self.clients:
            await client.start()
    
    async def close_sources(self):
        for client in self.clients:
            await client.close()

    def str_clients(self):
        s=''
        for client in self.clients:
            s+=f'{id(client)}  host: {client.ip}:{client.port}'+'\n'
        return s[:-1]

    def __str__(self):
        s = ''
        for source in self.sources:
            s += source.__str__()+'\n'
        return s[:-1]
    
    def setTasks(self):
        for source in self.sources:
            self.loop.create_task(self.loopSourceReader(source), name='SourceReader_'+source.id)
        # self.loop.create_task(self.startQueueReder())

    async def loopSourceReader(self, source: Source):
        logger.debug(f'start loopReader client:{source.id}, period:{source.period}')
        while True:
            try:
                try:
                    before = time()
                    self.result = await source.read()
                    # print(f'after read {source.id} def result:{self.result} connected={source.connection.connected}')

                except asyncio.exceptions.TimeoutError as ex:
                    print(f"!!!!!!!!!!!!!!!!!!! asyncio.exceptions.TimeoutError for {source.id}:", ex)
                # except ModbusExceptions.ModbusException as ex:                                            #TODO взять exception от клиента
                #     print(f"!!!!!!!!!!!!!!!!!!! ModbusException in looper for {client.id} :",ex)
                
                delay = source.period-(time()-before)
                if delay <= 0:
                    logger.warning(f'Not enough time for source read, source id:{source.id}, delay={delay}')
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                print(f"Got CancelledError close client connection{id(source.connection)}")
                if source.connection.connected:
                    await source.connection.close()
                break
    
    def readAllOneTime(self):
        for source in self.sources:
            #print(f'run read task {source.id}')
            self.loop.run_until_complete(source.read())
            #print(f'next step  after read task {source.result}')
            if not source.result:
                print (f'!!!!!!!!!!!!!!! Cant read source {source.id}')

        # Let also finish all running tasks:
        # pending = asyncio.Task.all_tasks()
        # self.loop.run_until_complete(asyncio.gather(*pending))

        
 

