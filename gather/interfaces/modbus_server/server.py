
"""
Modbus server class based on Pymodbus aSynchronous Server 
--------------------------------------------------------------------------

"""
# import logging
# FORMAT = ('%(asctime)-15s %(threadName)-15s'
#           ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
# logging.basicConfig(format=FORMAT)
# log = logging.getLogger()
# log.setLevel(logging.DEBUG)

from loguru import logger
import asyncio

from pymodbus.datastore import (ModbusSequentialDataBlock, ModbusServerContext,
                                ModbusSlaveContext)
from pymodbus.server.async_io import ModbusTcpServer, ModbusConnectedRequestHandler


from ...sourcepool import Source
from ...consts import Formats
from ...myexceptions import ModbusExchangeServerException

MB_FUNCS = {Formats.CO: 1, Formats.DI: 2, Formats.HR: 3, Formats.IR: 4}


class ModBusServer(ModbusTcpServer):
    def __init__(self, addr_map, sources, host, port, **kwargs):
        self.loop: asyncio.AbstractEventLoop = kwargs.get(
            "loop") or asyncio.get_event_loop()
        self.addr_map: list = addr_map
        self.sources: list[Source] = sources
        self.source_cache: dict = dict((s.id, s)
                                       for s in self.sources)

        # Defaults.ZeroMode=True
        self.context: ModbusServerContext = self.mb_server_context_init(
            addr_map)
        # self.id_map: dict = self.addr_map_2_id_map(self.addr_map)
        super().__init__(self.context, address=(host, port),
                         handler=MyRequestHandler
                         )

    def mb_server_context_init(self, addr_map: dict) -> ModbusServerContext:
        '''
        ModbusServerContext initialasing
        MBServerAdrMap=[
            {'unit':0x1, 
                'map':{
                    'di':[{'id':4207,'addr':1,'length':2, order: AB},
                          {'id':4208,'addr':3,'length':2, order: AB}],
                    'hr':[{'id':4209,'addr':0,'type':'int',, order: AB},
                          {'id':4210,'addr':1,'type':'float', order: ABCD}]
                }
            }]
        returns ModbusServerContext
        '''
        start_addr = 0x01
        slaves: dict[int, ModbusSlaveContext] = dict()
        for unit in addr_map:
            slaveContext = ModbusSlaveContext()
            co = unit['map'].get('co', None)
            di = unit['map'].get('di', None)
            hr = unit['map'].get('hr', None)
            ir = unit['map'].get('ir', None)

            if co and len(co):
                maxAddr = 0
                length = 1
                for device in co:
                    if device['addr'] > maxAddr:
                        maxAddr = device['addr']
                        length = device['length']
                    else:
                        length = device['length']
                ciLength = maxAddr+length
            else:
                ciLength = 1
            ciDataBlock = ModbusSequentialDataBlock(start_addr, [0]*ciLength)
            slaveContext.register(1, 'c', ciDataBlock)
            if di and len(di):
                maxAddr = 0
                length = 1
                for device in di:
                    if device['addr'] > maxAddr:
                        maxAddr = device['addr']
                        length = device['length']
                    else:
                        length = device['length']
                diLength = maxAddr+length
            else:
                diLength = 1
            diDataBlock = ModbusSequentialDataBlock(start_addr, [0]*diLength)
            slaveContext.register(2, 'd', diDataBlock)
            if hr and len(hr):
                maxAddr = 0
                length = 1
                for device in hr:
                    if device['addr'] >= maxAddr:
                        maxAddr = device['addr']
                        length = device.get('length', 1)
                hrLength = maxAddr + length
            else:
                hrLength = 1
            hrDataBlock = ModbusSequentialDataBlock(start_addr, [0]*hrLength)
            slaveContext.register(3, 'h', hrDataBlock)
            if ir and len(ir):
                maxAddr = 0
                length = 2
                for device in ir:
                    if device['addr'] > maxAddr:
                        maxAddr = device['addr']
                    if device['addr'] > maxAddr:
                        maxAddr = device['addr']
                        length = device.get('length', 2)
                irLength = maxAddr+length
            else:
                irLength = 1
            irDataBlock = ModbusSequentialDataBlock(start_addr, [0]*irLength)
            slaveContext.register(4, 'i', irDataBlock)
            # if len(addr_map)==1:
            #     context=ModbusServerContext(slaves=slaveContext, single=True)
            # else:
            slaves[unit['unit']] = slaveContext
        # if context ==None:
        context = ModbusServerContext(slaves, single=False)
        return context

    def get_source(self, func, addr, slave_unit):
        for unit_block in self.addr_map:
            if unit_block.get('unit') == slave_unit:
                if func in [1, 5, 15]:
                    data = unit_block.get('map').get('co')
                elif func in [2, ]:
                    data = unit_block.get('map').get('di')
                elif func in [3, 6, 16]:
                    data = unit_block.get('map').get('hr')
                elif func in [4, ]:
                    data = unit_block.get('map').get('ir')
                else:
                    raise ModbusExchangeServerException(
                        f' func {func} dont match co, di, hr, ir register {addr}, unit {slave_unit}')

                for reg in data:
                    if reg.get('addr') == addr:
                        return self.source_cache[reg['id']]
                    else:
                        raise ModbusExchangeServerException(
                            f'no source {addr=} at server corresponding addr map')

    async def start(self):
        logger.info('modbus server start')
        await self.serve_forever()

    async def stop(self):
        logger.info('Exchange server stopping...')
        await self.shutdown()
        logger.info('Exchange server stop')

    def set_value(self, func, unit, addr, val_list):
        # if val_list is None or len(val_list) == 0:
        #     val_list=ExceptionResponse(func, ModbusExceptions.SlaveFailure)
        self.context[unit].setValues(func, addr, val_list)


class MyRequestHandler(ModbusConnectedRequestHandler):
    '''
    Write functions with handler to send values to ChannelBase
    '''

    def __init__(self, server: ModBusServer):
        super().__init__(server)

    def connection_made(self, transport):
        """Call when a connection is made."""
        logger.log(
            'LOGIN', f'Client connection made from {transport.get_extra_info("peername")}')
        super().connection_made(transport)

    def connection_lost(self, call_exc):
        logger.log('LOGIN', 'Client connection lost')
        """Call when the connection is lost or closed."""
        super().connection_lost(call_exc)

    def execute(self, request, *addr):
        '''
        func 5 - write single coil
        func 6 - write single register
        func 15 - write multiple coils -> list[bool]
        func 16 - write multiple registers -> list[integer]
        '''
        # TODO
        # сначала выполнить execute посмотреть на валидвцию и ошибки
        # и потом  если ок - channel.set_channel_arg_name
        source: Source = self.server.get_source(
            request.function_code, request.address, request.unit_id)

        if request.function_code in [5, 6]:
            set_value = request.value
            asyncio.create_task(source.write(request.value))
        elif request.function_code == 15:
            set_value = request.values
        else:
            return super().execute(request, *addr)
        asyncio.create_task(source.write(set_value))

        return super().execute(request, *addr)


class MBServer(ModBusServer):
    def __init__(self, sources: list[Source], host, port, **kwargs):
        self.loop: asyncio.AbstractEventLoop = kwargs.get(
            "loop") or asyncio.get_event_loop()
        addr_map: list = self.create_address_map(sources)
        # self.source_pool: SourcePool = source_pool
        # self.source_cache: dict = dict((s.id, s)
        #                                for s in self.source_pool.sources)

        self.id_map: dict = self.addr_map_2_id_map(addr_map)
        super().__init__(addr_map, sources, host, port)

    @staticmethod
    def create_address_map(sources: list[Source]):
        addr_map = []
        for source in sources:
            exist_unit = next((unit_rec['unit'] for unit_rec in addr_map if unit_rec.get(
                'unit') == source.connection.unit), None)
            if not exist_unit:
                addr_map.append({'unit': source.connection.unit, 'map': {
                                'co': [], 'di': [], 'ir': [], 'hr': [], }})
            for unit_map in addr_map:
                if unit_map['unit'] == source.connection.unit:
                    match source.addr_pool:
                        case Formats.CO: map_key = 'co'
                        case Formats.DI: map_key = 'di'
                        case Formats.IR: map_key = 'ir'
                        case Formats.HR: map_key = 'hr'
                        case _: raise Exception(f'no such addr pool {source.addr_pool}')

                    unit_map['map'][map_key].append({'id': source.id,
                                                     'addr': source.connection.address,
                                                     'length': source.connection.reg_count})
        return addr_map

    def set_value_by_id(self, id: int, val_list: list):
        addr_pool, unit, addr, length = self.id_map[id]
        self.set_value(MB_FUNCS[addr_pool], unit, addr, val_list)

    def addr_map_2_id_map(self, addr_map: dict) -> dict:
        '''
        Convert addresMap to id map
        return dict {id:(addr_pool, unit, addr, length)}
        takes MBServerAdrMap=[
                {'unit':0x1, 
                    'map':{
                        'di':[{'id':4207,'addr':1,'len':2, order: AB},
                            {'id':4208,'addr':3,'len':2}, order: AB],
                        'hr':[{'id':4209,'addr':0,'type':'int', order: AB},
                            {'id':4210,'addr':1,'type':'float', order: ABCD}]
                    }
                }]
        '''
        id_map = dict()
        for unit in addr_map:
            co = unit['map'].get('co', None)
            if co:
                for device in co:
                    id_map[device['id']] = (Formats.CO, unit['unit'],
                                            device['addr'], device['length'])
            di = unit['map'].get('di', None)
            if di:
                for device in di:
                    id_map[device['id']] = (Formats.DI, unit['unit'],
                                            device['addr'], device['length'])
            hr = unit['map'].get('hr', None)
            if hr:
                for device in hr:
                    id_map[device['id']] = (Formats.HR, unit['unit'],
                                            device['addr'], device['length'])
            ir = unit['map'].get('ir', None)
            if ir:
                for device in ir:
                    id_map[device['id']] = (Formats.IR, unit['unit'],
                                            device['addr'], device['length'])
        return id_map

    def prepare_start_task(self):
        logger.info('create modbus server start task ')
        self.loop.create_task(self.start(), name='modbus_Server')
