'''
'''
from .dbcommands import AbstractDBCommand
from .absconnection import DBConnectorInterface
# from abc import ABC, abstractmethod 
from typing import Any, Callable

# class DBConnectorInterface(ABC):
#     '''
#     абстрактный DB bynthatqc
#     ABS DB interface SQL servers:
#     '''
#     def __init__(self, params: dict) -> None:...
#     @staticmethod
#     @abstractmethod     
#     def connector(func: Callable)->Callable:... #как вариант можно пользоваться декоратором из класса для подключения
#     # @abstractmethod     
#     # def exec_querry_func(self, querry_func:Callable, params:tuple):...
#     @abstractmethod     
#     def fetch_sql_querry(self, sql:str, params:tuple):...
#     @abstractmethod     
#     def commit_sql_querry(self, sql:str, values:tuple):...
#     @abstractmethod     
#     def commit_many_sql_querry(self, sql:str, values:tuple):...
    
class DBCommandProcessor():
    '''
    db commansd handler
    calls connection method according to command
    '''
    connection:DBConnectorInterface
    def __init__(self,connection:DBConnectorInterface) -> None:
        self.connection=connection
        
    def call(self, command: AbstractDBCommand):
            command.execute(self.connection)


        