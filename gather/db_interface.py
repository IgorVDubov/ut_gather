'''
Фабрика интерфейса DB
DB adapter for different SQL servers:
-MySQL
-Sqlight3

'''
# SELECT='select'
# INSERT='insert'
# UPDATE='update'
# DELETE='delete'
from typing import Any, Callable
from .consts import DbNames

SELECT=DbNames.SELECT
INSERT=DbNames.INSERT
UPDATE=DbNames.UPDATE
DELETE=DbNames.DELETE




class DBInterface():
    def __init__(self, db_type: str, dbparams: dict) -> None:
        if db_type==DbNames.MYSQL:
            from . import mysqlconnector 
            self.connection= mysqlconnector.MySQLConnector(dbparams)
        if db_type==DbNames.SQLIGHT3:
            from . import sqlite3_connector 
            self.connection= sqlite3_connector.Sqlight3Connector(dbparams)
    
    def exec_querry_func(self, querry_func:Callable, params:dict):
        return self.connection.exec_querry_func(querry_func, params)
    
    def exec_sql(self,requestType:str, sql:str, params:Any=None ):
        '''
        execute SQL request
        requestType: 'select' | 'insert' | 'updatre' | 'delete'
        sql: sql request body with %s params 
        params: tuple or list of params
        exmpl: execSQL('select','SELECT * FROM %s', ('table',))
        '''
        # print (f'execSQL: {requestType},{sql}, params:{params}')
        if requestType==SELECT:
            return self.connection.querry(sql,params)
        if requestType==INSERT:
            return self.connection.insert(sql,params)
        if requestType==UPDATE:
            return self.connection.update(sql,params)
        if requestType==DELETE:
            return self.connection.delete(sql,params)



if __name__ == '__main__':
    # import defaults

    # db=DBInterface(Consts.MYSQL,defaults.MySQLServerParams)

    # result=db.execSQL(SELECT,'select * from pname')
    # for rec in result:
    #     print(rec)

    # db.execSQL(INSERT,'INSERT INTO track_2 VALUES (%s, %s, %s, %s)', (4001, '2022:10:27 19:43:50', 2, 18))
    # # db.execSQL(UPDATE,'update pname set name=%s where id=%s',('test1',5))

    # result=db.execSQL(SELECT,'select * from track_2')
    # for rec in result:
    #     print(rec)
    # result=db.execSQL(DELETE,'delete from pname where id=%s',(5,))

    