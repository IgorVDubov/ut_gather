'''
Connection and SQL script funcs to MySql DB
'''
from typing import Callable

import mysql.connector
from mysql.connector import CMySQLConnection, MySQLConnection
from loguru import logger

from . import myexceptions


class MySQLConnector:
    '''
    connection to MySQL base on 
    https://dev.mysql.com/doc/connector-python/en/
    
    '''
    def __init__(self,dbParams):
        '''
        params
        {host='localhost', port=3032, database=None, user=None, password=None}
        '''
        self.params=dbParams
        
    def connect(self)->(CMySQLConnection | MySQLConnection | None ):
        try:
            cnx = mysql.connector.connect(**self.params)
            if cnx.is_connected():
                return cnx
        except mysql.connector.Error as err:
            logger.error(err)
        else:
            raise myexceptions.DBException (f'DB not connected with params: {self.params}')
    
    @staticmethod
    def connection(func: Callable)->Callable:
        def makeConn(self,*args, **kwargs):
            ctx=None
            try:
                ctx=self.connect()
                result=func(self,ctx,*args,**kwargs)
                ctx.close()
                return result
            except mysql.connector.Error as err:
                logger.error(err)
            finally:
                if ctx and ctx.is_connected():
                    ctx.close()
        return makeConn

    @connection
    def exec_querry_func(self,connection:MySQLConnection, func:Callable, params:dict={}):
        return func(connection, params)

    @connection
    def querry(self, connection:MySQLConnection, sql:str, params:tuple=()):
        '''
        base querry
        sql: sql string as "select * from ... where ..=%s and .=%s"
        params: None or list of %s..%sN params [param1,...,paramN] by order in sql
        '''
        cur = connection.cursor()
        cur.execute(sql,params)
        result = cur.fetchall()
        cur.close()
        return result 

    @connection
    def insertManyToTable(self, connection:MySQLConnection, table:str, values_list:list[tuple]):    #TODO liast of tuples + executemany для нескольких записей
        '''
        insert querry of values list. 
        
        table: table name in sql string as INSERT INTO TABLE VALUES ( %s... %s )
        values:list of tuples (%s..%sN) values by order in sql [(p1,p2)...,(p1,p2)]
         
        Values nunber = table fields number!!!
        '''
        if len(values_list):
            values = list(filter(None, values_list))
            valueLenngth=len(values[0])
            if values[0]:
                sql=f'INSERT INTO {table} VALUES( {", ".join(["%s"] * valueLenngth)})'
                cur = connection.cursor()
                cur.executemany(sql,values)
                connection.commit()
                cur.close()
            else:
                logger.error(f'Empty value tuple in isert querry to table:{table}, values:{values} ')
        else:
                logger.error(f'Empty value tuple in isert querry to table:{table}, values:{values_list} ')
    
    @connection
    def insert(self,connection:MySQLConnection, table:str, values:tuple):    
        '''
        insert querry of values list. 
        
        table: table name in sql string as INSERT INTO TABLE VALUES ( %s... %s )
        values:list of tuples (%s..%sN) values by order in sql [(p1,p2)...,(p1,p2)]
         
        Values nunber = table fields number!!!
        '''
        if length:=len(values):
            cur = connection.cursor()
            sql=f'INSERT INTO {table} VALUES( {", ".join(["%s"] * length)})'
            cur.execute(sql,values)
            connection.commit()
            cur.close()
        else:
                logger.error(f'Empty value tuple in isert querry to table:{table}, values:{values} ')
       
    @connection
    def update(self,connection:MySQLConnection, sql:str, params:tuple=()):
        '''
        update querry. 
        
        sql: sql string as UPDATE table_name SET name = %s WHERE id = %s
        params: tuple (%s..%sN) sql params by order in sql param1..paramN
        '''
        if len(params):
            cur = connection.cursor()
            cur.execute(sql,params)
            connection.commit()
            cur.close()
        else:
            logger.error(f'Empty value list in isert querry:{sql}')
    
    @connection
    def delete(self,connection:MySQLConnection, sql:str,params:tuple=()):
        '''
        delete querry.
        sql: sql string as DELETE FROM table_name WHERE id=%s AND profile_id=%s'
        params: list of tuples (%s..%sN) sql params by order in sql param1..paramN
        '''
        if len(params):
            cur = connection.cursor()
            cur.execute(sql,params)
            connection.commit()
            cur.close()
        else:
            logger.error(f'Empty value list in isert querry:{sql}')

   

if __name__ == '__main__':
    pass
    # import defaults
    # connection = mysql.connector.connect(**globals.MySQLServerParams)
    # cursor =connection.cursor()
    # cursor.execute(query,tuple(10021))
    # for rec in cursor:
    #     print(rec)
    # cursor.close()
    # connection.close()
  