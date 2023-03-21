from pymodbus.interfaces import Singleton

class Formats(Singleton):
    DATE_FORMAT_DB='%Y-%d-%m %H:%M:%S'

class ValTypes(Singleton):
    AI=0
    DI=1
    LIST=2
    FLOAT=3
    INT=4
    BIT=5
    BYTE=6
    WORD=7

class DeviceProtocol(Singleton):
    MODBUS='ModBus'

class DbNames(Singleton):
    DBC:str='db_connector'
    MYSQL:str='MySql'
    SQLIGHT3:str='Sqlight3'
    SELECT:str='select'
    INSERT:str='insert'
    UPDATE:str='update'
    DELETE:str='delete'



