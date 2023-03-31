import os.path

from gather import consts 

DEMO_DB=True

http_server_params={'host':'192.168.1.200',
                    'port':8870,
                    'wsserver':'ws://192.168.1.200:8870/ws',
                    'debug':True,
}
CHECK_AUTORIZATION=True    

users=[
    {'id': 1, 'first_name': 'Igor', 'middle_name': '', 'second_name': 'Dubov', 'login': 'div', 'pass': '123'},
    {'id': 2, 'first_name': 'Igor', 'middle_name': '', 'second_name': 'Dubov', 'login': 'div1', 'pass': '123'},
    ]


DB_PERIOD = 3                       # период опроса очереди сообщений для БД DBQuie
CHANNELBASE_CALC_PERIOD = 1         # период пересчета каналов в секундах (float) 

modbus_server_params = {'host': '127.0.0.1', 'port': 5021}
'''
параметры Модбас сервера для внешнего доступа
host, port->str: An optional (interface, port) to bind to.
'''
MBServerParams_E={'host': '127.0.0.1', 'port': 5022}
'''
параметры эмулятора Модбас сервера 
host:str, port:itn  An optional (interface, port) to bind to.
'''
DB_TYPE=consts.DbNames.MYSQL        #тип используемой СУБД (доступные в dbclassfactory)
MySQLServerParams={
    'host': '127.0.0.1',
    'database': 'utrack_db',
    'user': 'utrack',                       #TODO в переменные окружения!!!!!
    'password' : 'Adm_db78'
}
'''
параметры MySQLServer
'''
DB_PARAMS=MySQLServerParams     #параметры для инициализации текущей СУБД
