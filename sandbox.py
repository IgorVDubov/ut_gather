# from gather.interfaces.db.mysql_connector import MySQLConnector
# from gather.interfaces.db.dbinterface import DBInterface
# from datetime import datetime

MySQLServerParams={
    'host': '127.0.0.1',
    'database': 'test',
    'user': 'test',                       
    'password' : 'test'
}
# class AbstractDBCommand:
#     """
#     Level 0
#     Просто интерфейс
#     """
#             # отход от паттрена - параметрический execute (ниже понятно зачем)
#             # но AbstractDBCommand именно DBCommand !!!
#     def execute(self, connection:DBInterface):
#         raise NotImplementedError

# class DBCommand(AbstractDBCommand):
#     query: str
#     params: tuple
    
#     def __init__(self, query: str, params:tuple):
#         self.query = query
#         self.params = params
        
#     def execute(self, connection:DBInterface):
#         raise NotImplementedError

# class DBInsertCommand(DBCommand):
#     def execute(self, connection:DBInterface):
#         connection.commit_sql_querry(self.query, self.params)
        
# class DBConsumer():
#     connection:DBInterface
#     def __init__(self,connection:DBInterface) -> None:
#         self.connection=connection
        
#     def call(self, command: AbstractDBCommand):
#             command.execute(self.connection)


# def write_by_command2():
#     connector=MySQLConnector(MySQLServerParams)
#     db=DBConsumer(connector)
    
#     db.call(DBInsertCommand('insert into test1 values (%s,%s)', (2,22) ))

# def write_by_command():
#     #-------------------------- core init -------------------------
#     connector=MySQLConnector(MySQLServerParams)
#     db=DBConsumer(connector)
#     #------------------------project level -------------------------------
#     # ------ и тут ничего не знаю про connector
#     db.call(DBInsertCommand('insert into test1 values (%s,%s)', (2,22) ))
#     # можно отсюда кидать в очередь и на верхнем уровне разбирать ее DBConsumer-ом, сроить буфферы и др бантики
#     # и тогда на этом уровне вообще не будет DBConsumer-а и надо знать только доступные классы команд (DBInsertCommand и тд)
#     # которые можно поместить в модуль типа dbcommands и импортируя его понимать что и как можно вызывать
    
#     # и получается что для подсистемы БД  я предоставляю 
#     #   - очередь для массовой записи из тех же ассинхронных сущнгостей,например, 
#     #   - конзьюмер для прямого посыла команд (селекты) 
#     #   - набор классов команд
#     # вроде то, что я и хотел - всё остальное под капотом ядра 
#     # и настраивается в инициализаторе проекта вначале
    
    
from gather.interfaces.db.dbconnector import create_db_connector
from  gather.interfaces.db.dbinterface import DBCommandProcessor
from  gather.interfaces.db import dbcommands
import gather.consts

if __name__=='__main__':
     
    connection=create_db_connector(gather.consts.DbNames.MYSQL, MySQLServerParams)
    db_proc= DBCommandProcessor(connection)
    db_proc.call(dbcommands.DBInsert('insert into test1 values (%s,%s)', (2,22) ))
    