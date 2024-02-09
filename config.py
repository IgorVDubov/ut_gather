from models import User


from gathercore import consts

DEMO_DB = True

http_server_params = {
                    'host': 'utrack.hcaskona.com',
                    'port': 8870,
                    'wsserver': 'ws://utrack.hcaskona.com:8870/ws',
                    'debug': True,
                    'static_path': 'web/webdata',
                    'template_path': 'web/webdata',
                    'static': 'web/webdata',
                    'js': 'web/webdata/js',
                    'css': 'web/webdata/css',
                    'images': 'web/webdata/images',
}



DB_PERIOD = 3                       # период опроса очереди сообщений для БД DBQuie
# период пересчета каналов в секундах (float)
CHANNELBASE_CALC_PERIOD = 1

modbus_server_params = {'host': '127.0.0.1', 'port': 5021}
'''
параметры Модбас сервера для внешнего доступа
host, port->str: An optional (interface, port) to bind to.
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


