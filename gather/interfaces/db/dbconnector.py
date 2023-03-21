'''
Фабрика интерфейса DB
DB adapter for different SQL servers:
-MySQL
-...
'''

from ... import consts, myexceptions
from .mysql_connector import MySQLConnector
from .absconnection import DBConnectorInterface

def create_db_connector(type:str, params: dict)-> DBConnectorInterface: 
    match type:
        case consts.DbNames.MYSQL:
            return MySQLConnector(params)
        case _:
            raise myexceptions.DBException(f'{type=} not implemented no db connection')