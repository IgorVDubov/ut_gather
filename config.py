from models import User


from gathercore import consts

DEMO_DB = True

http_server_params = {'host': '192.168.1.200',
                      'port': 8870,
                      'wsserver': 'ws://192.168.1.200:8870/ws',
                      'debug': True,
                      }
CHECK_AUTORIZATION = True

users: list[User] = [
    {'id': 1, 'name': 'Igor', 'm_name': '',
        's_name': 'Dubov', 'login': 'div', 'password': '123'},
]

user_machines = {1: [2000]}

DB_PERIOD = 3                       # период опроса очереди сообщений для БД DBQuie
# период пересчета каналов в секундах (float)
CHANNELBASE_CALC_PERIOD = 1

modbus_server_params = {'host': '127.0.0.1', 'port': 5021}
'''
параметры Модбас сервера для внешнего доступа
host, port->str: An optional (interface, port) to bind to.
'''
MBServerParams_E = {'host': '127.0.0.1', 'port': 5022}
'''
параметры эмулятора Модбас сервера 
host:str, port:itn  An optional (interface, port) to bind to.
'''
DB_TYPE = consts.DbNames.MYSQL  # тип используемой СУБД (доступные в dbclassfactory)
MySQLServerParams = {
    'host': '127.0.0.1',
    'database': 'utrack_db',
    'user': 'utrack',  # TODO в переменные окружения!!!!!
    'password': 'Adm_db78'
}
'''
параметры MySQLServer
'''
DB_PARAMS = MySQLServerParams  # параметры для инициализации текущей СУБД
