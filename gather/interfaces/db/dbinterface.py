'''
'''
# from abc import ABC, abstractmethod 
from typing import Any, Callable

from .absconnection import DBConnectorInterface
from .dbcommands import AbstractDBCommand

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