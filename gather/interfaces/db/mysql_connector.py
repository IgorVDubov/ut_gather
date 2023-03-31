'''
Connection and SQL script funcs to MySql DB
'''

from typing import Callable, Sequence
import mysql.connector
# from mysql.connector import CMySQLConnection, MySQLConnection
from mysql.connector import MySQLConnection
from loguru import logger

from .absconnection import DBConnectorInterface
from ... import myexceptions


class MySQLConnector(DBConnectorInterface):
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
    def connector(func: Callable)->Callable:
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

    # @connector
    # def exec_querry_func(self,connection:MySQLConnection, func:Callable, params:dict={}):
    #     return func(connection, params)
    
    @connector
    def fetch_sql_querry(self, connection:MySQLConnection, sql:str, params:dict={}):
        '''
        get sql query with fetch result 
         - select
        '''
        cur = connection.cursor()
        cur.execute(sql,params)
        result = cur.fetchall()
        cur.close()
        return result 
    
    @connector
    def commit_sql_querry(self, connection:MySQLConnection, sql:str, values:tuple={}):
        '''
        put sql query with fetch result 
         - insert, update, delete 
        '''
        cur = connection.cursor()
        cur.execute(sql,values)
        connection.commit()
        cur.close()
    
    @connector
    def commit_many_sql_querry(self, connection:MySQLConnection, sql:str, values:list[tuple]=[]):
        '''
        put many sql query with fetch result and executemany method
         - insert, update, delete 
        '''
        cur = connection.cursor()
        cur.executemany(sql,values)
        connection.commit()
        cur.close()


    @connector
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
