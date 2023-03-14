'''
Фабрика интерфейса DB
DB adapter for different SQL servers:
-MySQL
-Sqlight3

'''
from typing import Any, Callable
from ...consts import DbNames

class DBInterface():
        
    def exec_querry_func(self, querry_func:Callable, params:dict):
        raise NotImplemented
        
    
    def exec_sql(self,requestType:str, sql:str, params:Any=None ):
        '''
        execute SQL request
        requestType: 'select' | 'insert' | 'updatre' | 'delete'
        sql: sql request body with %s params 
        params: tuple or list of params
        exmpl: execSQL('select','SELECT * FROM %s', ('table',))
        '''
        raise NotImplemented