from pymodbus.interfaces import Singleton
AI=1
DI=2
LIST=0
FLOAT=1
INT=2
BIT=3
BYTE=4
WORD=5

class Consts(Singleton):
    MODBUS='ModBus'
    MYSQL='MySql'
    SQLIGHT3='Sqlight3'
    SELECT='select'
    INSERT='insert'
    UPDATE='update'
    DELETE='delete'
    DBC='dbc'
    DATE_FORMAT_DB='%Y-%d-%m %H:%M:%S'


