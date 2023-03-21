from .absconnection import DBConnectorInterface

class AbstractDBCommand:
    """
    Abstract command for DB system
    """
    query: str
    params: tuple
    def __init__(self, query: str, params:tuple):
        self.query = query
        self.params = params
    
    def execute(self, connection:DBConnectorInterface):
        raise NotImplementedError
    
    def on_init(self):
        pass
    
    def on_error(self, e: Exception):
        pass
    
    def on_success(self):
        pass
    
    def on_complete(self):
        pass

class DBInsert(AbstractDBCommand):
    '''
    insert into db
    params:
        sql_querry with %s for positional params
        tuple of values
    ex: DBInsert('insert into table_name values (%s,%s,%s)',(1,'lalala',33))
    '''
        
    def execute(self, connection:DBConnectorInterface):
        connection.commit_sql_querry(self.query, self.params)
    