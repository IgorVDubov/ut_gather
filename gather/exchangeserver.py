'''
модуль обмена данными по запросам от внешних клиентов
реализация : ModBus

'''
from abc import ABC, abstractmethod
from copy import deepcopy

from .channels import channelbase 
from .modbus_server import MBServer


class ExchangeServer(ABC):
    
    @abstractmethod
    def start():...
    @abstractmethod
    def stop():...
    @abstractmethod
    def setValue():...
    @abstractmethod
    def getValue():...

    



class ModbusExchangeServer(ExchangeServer):
    def __init__(   self,
                    addrMapP:list, 
                    channel_base:channelbase.ChannelsBase, 
                    exchange_bindings,
                    serverHost, 
                    serverPort, loop):
            self.server=MBServer(addrMapP, channel_base , {'host':serverHost, 'port':serverPort},loop=loop)
            self.exchange_bindings=exchange_bindings
    
    def start(self):
        self._mbStart()
    def stop(self):
        self._mbStop()
    def setValue(self,channel_attr,value):
        self._mbSetIdValue(channel_attr,value)
    def getValue(self, channel_attr): 
        return self._mbGetIdValue(channel_attr)

    def _mbStart(self):
        # self.server.startInThread()
        self.server.start()
    
    def _mbStop(self):
        self.server.stop()
    
    def _mbSetIdValue(self,channel_attr,value):
        self.server.setValue(channel_attr,value)
    def _mbGetIdValue(self,channel_attr):
        return self.server.getValue(channel_attr)

def MBServerAdrMapInit(channelBase:channelbase.ChannelsBase,addrMaping:dict)->tuple():
    '''
    привязка атрибутов каналов из addrMaping к атрибутам каналов из channelBase
    return
    channelBase у которой убраны поля привязки для совместимости с  MBServer
    bindings {channelID:binding} - словарь привязок для ускорения обработки
    '''
    bindings=dict()
    for unit in  addrMaping:
        for regType,data in unit.get('map').items():
            for reg in data:
                if channel_attr:=reg.get('channel'):
                    bindings.update({channel_attr:channelbase.bindChannelAttrName(channelBase,channel_attr)})
                # if attr:=reg.get('attr'):
                #     bindings.update({str(reg['id'])+'.'+reg['attr']:channelbase.bindChannelAttr(channelBase,reg['id'],attr)})
                else:
                    raise ValueError(f'no value to bind at {reg}')
    return bindings

if __name__ == '__main__':
    pass
