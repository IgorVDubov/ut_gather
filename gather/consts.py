from pymodbus.interfaces import Singleton


class SourceTypes(Singleton):
    MODBUS_TCP = 1
    
    
class Formats(Singleton):
    DATE_FORMAT_DB = '%Y-%d-%m %H:%M:%S'
    AB = 1
    BA = 2
    ABCD = 3
    CDAB = 4
    BADC = 5
    DCBA = 6
     
    CO = 1
    DI = 2
    HR = 3
    IR = 4
    
class ModbusFuncs(Singleton):
    READ_CO = 1
    READ_DI = 2
    READ_HR = 3
    READ_IR = 4
    WRITE_CO = 5
    WRITE_HR = 6
    WRITE_MULT_CO = 15
    WRITE_MULT_HR = 16
    
    
class ValTypes(Singleton):
    BIT =   1
    BYTE =  2
    INT =   3
    WORD =  4
    LIST =  5
    DI =    6
    INT16 = 7
    INT32 = 8
    FLOAT = 9

class DeviceProtocol(Singleton):
    MODBUS='ModBus'

class DbNames(Singleton):
    DBC: str = 'db_connector'
    MYSQL: str = 'MySql'
    SQLIGHT3: str = 'Sqlight3'
    SELECT: str = 'select'
    INSERT: str = 'insert'
    UPDATE: str = 'update'
    DELETE: str = 'delete'



