
"""
Modbus server class based on Pymodbus Synchronous Server 
--------------------------------------------------------------------------

"""
# --------------------------------------------------------------------------- #
# import the various server implementations
# --------------------------------------------------------------------------- #
import asyncio
import struct
from threading import Thread
from copy import deepcopy

from pymodbus.datastore import (ModbusSequentialDataBlock, ModbusServerContext,
                                ModbusSlaveContext)

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server.async_io import ModbusTcpServer, ModbusConnectedRequestHandler  # , _serverList
from pymodbus.version import version
from pymodbus.constants import Defaults

from pymodbus.register_write_message import (
    WriteSingleRegisterRequest,
    WriteSingleRegisterResponse,
)
import bpacker

from .channels.channelbase import ChannelsBase
from .myexceptions import ConfigException, ModbusExchangeServerException
from .consts import ValTypes, Formats
from .defaults import FLOAT_ACCURACY, DEFAULT_4_BYTES_ORDER, DEFAULT_2_BYTES_ORDER

FLOAT = ValTypes.FLOAT
INT16 = ValTypes.INT16
INT32 = ValTypes.INT32
LIST = ValTypes.LIST
BYTE = ValTypes.BYTE

CO = Formats.CO
DI = Formats.DI
HR = Formats.HR
IR = Formats.IR
ABCD = Formats.ABCD
CDAB = Formats.CDAB


# from pymodbus.transaction import ModbusRtuFramer, ModbusBinaryFramer
# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
# import logging
# FORMAT = ('%(asctime)-15s %(threadName)-15s'
#           ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
# logging.basicConfig(format=FORMAT)
# log = logging.getLogger()
# log.setLevel(logging.DEBUG)


def convert_int16(value: int, order: Formats | None = None) -> int:
    if order is None:
        order = DEFAULT_2_BYTES_ORDER
    if order == Formats.BA:
        bpacker.convert_int16_AB2BA(value)

def pack_int32(value: int, order: Formats | None = None) -> int:
    if order is None:
        order = DEFAULT_4_BYTES_ORDER
    if order == Formats.CDAB:
        return bpacker.pack_int32_to_CDAB(value)
    else:
        return bpacker.pack_int32_to_ABCD(value)


def pack_float(value: float, order: Formats | None = None) -> list:
    if order is None:
        order = DEFAULT_4_BYTES_ORDER
    if order == Formats.CDAB:
        return bpacker.float_pack_2_CDAB(value)
    else:
        return bpacker.float_pack_2_ABCD(value)


def unpack_float(value: list[int], order: Formats | None = None)-> float:
    if order is None:
        order = DEFAULT_4_BYTES_ORDER
    if order == Formats.CDAB:
        return bpacker.CDAB_unpack_2_float(value, FLOAT_ACCURACY)
    else:
        return bpacker.ABCD_unpack_2_float(value, FLOAT_ACCURACY)

   
class MBServer(ModbusTcpServer):
    def __init__(self, addr_map, channel_base: ChannelsBase, serverParams, **kwargs):
        self.loop: asyncio.AbstractEventLoop = kwargs.get("loop") or asyncio.get_event_loop()
        self.addr_map: list = addr_map
        self.channel_base: ChannelsBase = channel_base
        self.serverParams: dict = serverParams
        # Defaults.ZeroMode=True
        self.context: ModbusServerContext = self.mb_server_context_init(addr_map)
        self.id_map: dict = self.addr_map_2_id_map(addr_map)
        # self.id_map:dict=self.addr_map_2_id_map(self._pop_addr(addr_map))
        super().__init__(self.context, address=(self.serverParams['host'],
                         self.serverParams['port']),
                         handler=ChannelsRequestHandler)

    def get_channel_attr(self, func, addr, slave_unit):
        for unit_block in self.addr_map:
            if unit_block.get('unit') == slave_unit:
                if func in [1, 5, 15]:
                    data = unit_block.get('map').get('co')
                elif func in [2,]:
                    data = unit_block.get('map').get('di')
                elif func in [3, 6, 16]:
                    data = unit_block.get('map').get('hr')
                elif func in [4,]:
                    data = unit_block.get('map').get('ir')
                else:
                    raise ConfigException(f' func {func} dont match co, di, hr, ir register {addr}, unit {slave_unit}')
                for reg in data:
                    if reg.get('addr') == addr:
                        return (reg.get('channel'),
                                reg.get('type'),
                                reg.get('length', 1),
                                reg.get('order', 1)
                                )

    # def _pop_addr(self, addr_maping: dict) -> dict:
    #     newAddrMap = deepcopy(addr_maping)
    #     bindings = dict()
    #     for unit in newAddrMap:
    #         for regType, data in unit.get('map').items():
    #             for reg in data:
    #                 reg.pop('attr')
    #     return newAddrMap

    def addr_map_2_id_map(self, addr_map: dict) -> dict:
        '''
        Convert addresMap to id map
        return dict {id:(unut,adr,length,type, order)}
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
            ci = unit['map'].get('ci', None)
            if ci:
                for device in ci:
                    id_map[device['channel']] = (CO, unit['unit'],
                                                 device['addr'],
                                                 1,
                                                 bool,
                                                 device.get('order'))
            di = unit['map'].get('di', None)
            if di:
                for device in di:
                    id_map[device['channel']] = (DI, unit['unit'],
                                                 device['addr'],
                                                 device['length'], 
                                                 BYTE,
                                                 device.get('order'))
            hr = unit['map'].get('hr', None)
            if hr:
                for device in hr:
                    valLength = 1
                    if device['type'] in (FLOAT, INT32):
                        valLength = 2
                    elif device['type'] == INT16:
                        valLength = 1
                    elif device['type'] == LIST:
                        valLength = device.get('length', 1)
                    id_map[device['channel']] = (HR, unit['unit'],
                                                 device['addr'],
                                                 valLength,
                                                 device['type'],
                                                 device.get('order'))
            ir = unit['map'].get('ir', None)
            if ir:
                for device in ir:
                    valLength = 1
                    if device['type'] in (FLOAT, INT32):
                        valLength = 2
                    elif device['type'] == INT16:
                        valLength = 1
                    elif device['type'] == LIST:
                        valLength = device.get('length', 1)
                    id_map[device['id']] = (IR, unit['unit'],
                                            device['addr'],
                                            valLength,
                                            device['type'],
                                            device.get('order'))
            # print(id_map)
        return id_map

    def mb_server_context_init(self, addr_map: dict) -> ModbusServerContext:
        '''
        ModbusServerContext initialasing
        MBServerAdrMap=[
            {'unit':0x1, 
                'map':{
                    'di':[{'id':4207,'addr':1,'lenght':2, order: AB},
                          {'id':4208,'addr':3,'lenght':2, order: AB}],
                    'hr':[{'id':4209,'addr':0,'type':'int',, order: AB},
                          {'id':4210,'addr':1,'type':'float', order: ABCD}]
                }
            }]
        returns ModbusServerContext
        '''
        start_addr = 0x01
        slaves: dict[int, ModbusSlaveContext]= dict()
        for unit in addr_map:
            slaveContext = ModbusSlaveContext()
            ci = unit['map'].get('ci', None)
            di = unit['map'].get('di', None)
            hr = unit['map'].get('hr', None)
            ir = unit['map'].get('ir', None)
            
            if ci:
                maxAddr = 0
                length = 1
                for device in ci:
                    if device['addr'] > maxAddr:
                        maxAddr = device['addr']
                        length = device['lenght']
                    else:
                        length = device['lenght']
                ciLength = maxAddr+length
            else:
                ciLength = 1
            ciDataBlock = ModbusSequentialDataBlock(start_addr, [0]*ciLength)
            slaveContext.register(1, 'c', ciDataBlock)
            if di:
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
            if hr:
                maxAddr = 0
                length = 1
                for device in hr:
                    if device['addr'] > maxAddr:
                        maxAddr = device['addr']
                    if device['type'] in (FLOAT, INT32):
                        length = 2
                    elif device['type'] == INT16:
                        length = 1
                    elif device['type'] == LIST:
                        length = device.get('length', 1)
                hrLength = maxAddr + length
            else:
                hrLength = 1
            hrDataBlock = ModbusSequentialDataBlock(start_addr, [0]*hrLength)
            slaveContext.register(3, 'h', hrDataBlock)
            if ir:
                maxAddr = 0
                length = 2
                for device in ir:
                    if device['addr']>maxAddr:
                        maxAddr = device['addr']
                    if device['addr'] > maxAddr:
                        maxAddr = device['addr']
                    if device['type'] in (FLOAT, INT32):
                        length = 2    
                    elif device['type'] == INT16:
                        length = 1    
                    elif device['type'] == LIST:
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

    def start(self):
        # StartTcpServer(self.context, address=(self.serverParams['host'],self.serverParams['port']))
        self.loop.create_task(self.serve_forever(), name='Exchange_Server')
    
    def stop(self):
        # self.server_close()
        asyncio.create_task(self.shutdown())

    # def startInThread(self):
    #     serverThread = Thread(target=self.start)
    #     serverThread.daemon = True
    #     serverThread.start()
    #     self.serverThread = serverThread
        
    # def stopInThread(self):
    #     asyncio.create_task(self.shutdown())

    def setCI(self, unit, addr, val):
        # print('setDI')
        self.context[unit].setValues(1, addr, val)
    
    def setDI(self, unit, addr,val):
        # print('setDI')
        self.context[unit].setValues(2, addr, val)

    def setInt(self, unit, addr,val):
        # print('setInt')
        self.context[unit].setValues(3, addr, val)
    
    def set_func_3(self, unit, addr, val):
        # print('setInt')
        self.context[unit].setValues(3, addr, val)

    def set_func_4(self, unit: int, addr: int, vals: list):
        # print('setFloat')
        self.context[unit].setValues(4, addr, vals)

    def setFloat(self, unit, addr, val):
        # print('setFloat')
        self.context[unit].setValues(4, addr, bpacker.packFloatToCDAB(val))     # уточнить метод упаковки
    
    def setValue(self, channel_attr: str, val):
        '''
        set value by ID according to addr map
        if val=None NOT SET value!!!!!
        id:int
        val: [b,b,b...] if DI
             int if HR type int
             float or int as float if HR type float
        '''
        try:
            reg_type, unit, addr, length, val_type, order = self.id_map.get(channel_attr)
        except TypeError:
            raise ConfigException(f'ModBus server[setValue]: cant get mnapping for id:{id}')
        # print(f'{id=} {addr=} {length=} {val=}')
        if addr is None or val is None:                                                             
            # raise ModbusExchangeServerException('modbusServer setValue no such ID in map')
            return
        else:
            if reg_type == DI:
                if type(val) == list:
                    val = val[:length]            # обрезаем результат в соответствии с заданной длиной записи         &&&&&&&&&&  ?????????????????????????
                    self.setDI(unit, addr, val)
                else:
                    raise ModbusExchangeServerException(f'modbusServer setValue value ({val}) for id:{id} is not list type')
            elif reg_type == CO:
                if type(val) == bool:
                    self.setCI(unit, addr, val)
                else:
                    raise ModbusExchangeServerException(f'modbusServer setValue value ({val}) for id:{id} is not bool type')
            elif reg_type == HR:
                if val_type == INT16:
                    if type(val) == int:
                        self.set_func_3(unit, addr, [convert_int16(val, order)])
                    else:
                        raise ModbusExchangeServerException(f'modbusServer setValue value ({val}) for id:{id} is not int type')
                if val_type == INT32:
                    if type(val) == int:
                        self.set_func_3(unit, addr, pack_int32(val, order))
                    else:
                        raise ModbusExchangeServerException(f'modbusServer setValue value ({val}) for id:{id} is not int type')
                elif val_type == LIST:
                    if type(val) == list:
                        self.set_func_3(unit, addr, val)
                    else:
                        raise ModbusExchangeServerException(f'modbusServer setValue value ({val}) for id:{id} is not list type')
                elif val_type == FLOAT:
                    if type(val) in (int, float):
                        self.set_func_3(unit, addr, pack_float(val, order))     # уточнить метод упаковки
                    else:
                        raise ModbusExchangeServerException(f'modbusServer setValue value ({val}) for id:{id} is not int or float type')
            elif reg_type == IR:
                if val_type == FLOAT:
                    if type(val) in (int, float):
                        self.set_func_4(unit, addr, pack_float(val, order))     # уточнить метод упаковки
                    else:
                        raise ModbusExchangeServerException(f'modbusServer setValue value ({val}) for id:{id} is not int or float type')
                elif val_type == INT16:
                    if type(val) == int:
                        self.set_func_4(unit, addr, [convert_int16(val, order)])
                    else:
                        raise ModbusExchangeServerException(f'modbusServer setValue value ({val}) for id:{id} is not int type')
                elif val_type == INT32:
                    if type(val) == int:
                        self.set_func_4(unit, addr, [pack_int32(val, order)])
                    else:
                        raise ModbusExchangeServerException(f'modbusServer setValue value ({val}) for id:{id} is not int type')
                elif val_type == LIST:
                    if type(val) == list:
                        self.set_func_4(unit, addr, val)
                    else:
                        raise ModbusExchangeServerException(f'modbusServer setValue value ({val}) for id:{id} is not list type')

    def handle_func_6(self):
        ...


class ChannelsRequestHandler(ModbusConnectedRequestHandler):
    '''
    Write functions with handler to send values to ChannelBase
    '''
    
    def __init__(self, server: MBServer):
        super().__init__(server)

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

        channel_arg, val_type, length, order = self.server.get_channel_attr(request.function_code, request.address, request.unit_id)
        
        channel = self.server.channel_base.get_by_argname(channel_arg)
        if request.function_code in [5, 6]:
            channel.set_channel_arg_name(channel_arg, request.value)           
        elif request.function_code == 15:
            set_value = request.values
            channel.set_channel_arg_name(channel_arg, request.values)            # TODO разбор типа значения и конвертация
        elif request.function_code == 16:
            if val_type == LIST:
                set_value = request.values
            elif val_type == INT16:
                set_value = request.values
            elif val_type == INT32:
                set_value = request.values
            elif val_type == FLOAT:
                set_value = bpacker.unpackCDABToFloat(request.values)
            channel.set_channel_arg_name(channel_arg, set_value)            # TODO разбор типа значения и конвертация

        return super().execute(request, *addr)


def updating_writer(con):
    i = 1
    context = con['con']
    while True:
        i+=1
        context[0].setValues(4,1,[i])
        # context[0].setValues(2,1,[1,0,0,1,0,1])
        sleep(1)
        
        
        
        
        
# ----------------------------- testing ---------------------------------------

def run_server():

    store = ModbusSlaveContext(
        #di=ModbusSequentialDataBlock(1, [1]*16),
        di=None,
        ir=ModbusSequentialDataBlock(1, [65534,277,3,0]+packFloatTo2WordsCDAB(1.75))
        )
    # store = ModbusSlaveContext(
    #     ir=ModbusSequentialDataBlock(0, [4]*1))
    # store = ModbusSlaveContext(
        # di=ModbusSequentialDataBlock(0, [1]*1),
    #     co=ModbusSequentialDataBlock(0, [2]*1),
    #     hr=ModbusSequentialDataBlock(0, [3]*1),
    #     ir=ModbusSequentialDataBlock(0, [4]*1))

    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    # If you don't set this or any fields, they are defaulted to empty strings.
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Pymodbus Server'
    identity.ModelName = 'Pymodbus Server'
    identity.MajorMinorRevision = version.short()

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    # Tcp:
   
   
    updating_writer_thread = Thread(target = updating_writer, args = [{'con':context}])    
    updating_writer_thread.daemon=True
    updating_writer_thread.start()

    StartTcpServer(context, identity=identity, address=("192.168.1.200", 5020))
    print ('afterstart')

async def call(server):
    i=1
    while True:
        try:
            i+=1
            server.setValue(4001,i)
            server.setValue(4002,i+50)
            # server.setValue(4003,[1])
            # server.setValue(4004,[i%2==True,0,1])
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break

from time import sleep


def main(loop):
    #run_server()
    MBServerParams={'host':'127.0.0.1','port':5021}
    mb_server_addr_map=[
    {'unit':0x1, 'map':{
        # 'di':[{'id':4001, 'attr':'result', 'addr':0, 'len':16}
        #     ],
        'ir':[
            {'id':4001, 'attr':'result', 'addr':1, 'type':'int'},
            {'id':4002, 'attr':'result', 'addr':2, 'type':'float'},
            # {'id':4003, 'attr':'result', 'addr':3, 'type':'int'},
            # {'id':4004, 'attr':'result', 'addr':4, 'type':'int'},
        ]
        }
    }]
 
    # server=loop.run_until_complete(StartAsyncTcpServer(mb_server_addr_map,MBServerParams,loop=loop))
    server=MBServer(mb_server_addr_map,MBServerParams,loop=loop)
    # l=_serverList(server,[],True)
    # l.run()
    loop.create_task(call(server))
    loop.create_task(server.serve_forever())
    # loop.run_forever()
    # server.start()
    # server.startInThread()

if __name__ == "__main__":
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main(loop)
    loop.run_forever()

