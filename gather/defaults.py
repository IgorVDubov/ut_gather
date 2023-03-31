from .consts import DbNames, Formats

DB_PERIOD=3    #период опроса очереди сообщений для БД DBQuie
CHANNELBASE_CALC_PERIOD=1 #период пересчета каналов в секундах (float)
FLOAT_ACCURACY=3
DEFAULT_4_BYTES_ORDER=Formats.ABCD
DEFAULT_2_BYTES_ORDER=Formats.AB

modbus_client_params={'host':'127.0.0.1','port':502}
modbus_server_params={'host':'127.0.0.1','port':502}
DB_TYPE=DbNames.MYSQL        #тип используемой СУБД (доступные в dbclassfactory)
users=[             # пользователи админки gather-a
    {'id': 1, 'first_name': 'Igor', 'middle_name': '', 'second_name': 'Dubov', 'login': 'div', 'pass': '123'},
] 