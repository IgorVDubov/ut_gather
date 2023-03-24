
'''
Connection and SQL script funcs to Sqlite3 DB
'''
import sqlite3

from loguru import logger
from myexceptions import DBException


def connection(func)->sqlite3.Connection|None:
    def makeConn(self,*args, **kwargs):
        ctx=self.connect()
        try:
            cnx = sqlite3.connect(**self.params)
            if cnx.is_connected():                                  #TODO реализовать если надо?? 
                result=func(self,ctx,*args,**kwargs)
                ctx.close()
                return result
        except sqlite3.Error as err: 
            logger.error(f'sqlite3 error: {err}')
    return makeConn



class Sqlight3Connector(object):
    '''
    connection to MySQL base on 
    https://dev.mysql.com/doc/connector-python/en/
    
    '''
    def __init__(self,dbParams):
        '''
        params "DB_name_with_path"
        
        '''
        self.params=dbParams
        
    def _connect(self)->sqlite3.Connection|None:
        try:
            cnx =sqlite3.connect(self.params)
            if cnx.cursor():                        #проверка подключения (проверить тестами сколько занимает времени)
                return cnx
        except sqlite3.Error as err:
            logger.error(err)
        else:
            raise DBException (f'DB {self.params} not connected')
    

    def connection(func):
        def makeConn(self,*args, **kwargs):
            try:
                ctx=self._connect()
                result=func(self,ctx,*args,**kwargs)
                ctx.close()
                return result
            except sqlite3.Error.Error as err:
                logger.error(err)
            finally:
                if ctx:
                    if ctx.is_connected():
                        ctx.close()
        return makeConn
    @connection
    def exec_querry_func(self,connection:MySQLConnection, func:Callable, params:dict={}):
        return func(connection, params)

    @connection
    def querry(self,connection,sql:str,params:tuple=()):
        '''
        base querry
        sql: sql string as "select * from ... where ..=%s and .=%s"
        params: None or list of %s..%sN params [param1,...,paramN] by order in sql
        '''
        cur = connection.cursor()
        cur.execute(sql,tuple(params))
        result = cur.fetchall()
        cur.close()
        return result 

    @connection
    def insert(self,connection,table:str,values:tuple=()):    #TODO liast of tuples + executemany для нескольких записей
        '''
        insert querry of values list. 
        
        table: table name in sql string as INSERT INTO TABLE VALUES ( %s... %s )
        values:list of tuples (%s..%sN) values by order in sql [(p1,p2)...,(p1,p2)]
         
        Values nunber = table fields number!!!
        '''
        if len(values):
            values = list(filter(None, values))
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
                logger.error(f'Empty value tuple in isert querry to table:{table}, values:{values} ')
       
    @connection
    def update(self,connection,sql:str,params:tuple=()):
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
    def delete(self,connection,sql:str,params:tuple=()):
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
    import defaults

    db=MySQLConnector(defaults.MySQLServerParams)
    result=db.test([10018])
    for rec in result:
        print(rec)

    # import globals
    # connection = mysql.connector.connect(**globals.MySQLServerParams)

    # cursor =connection.cursor()

    # query = ("SELECT * from mname where id=%s")

    # cursor.execute(query,tuple(10021))

    # for rec in cursor:
    #     print(rec)

    # cursor.close()
    # connection.close()
  