from .consts import Consts

DB_PERIOD=3    #период опроса очереди сообщений для БД DBQuie
CHANNELBASE_CALC_PERIOD=1 #период пересчета каналов в секундах (float) 
modbus_client_params={'host':'127.0.0.1','port':502}
modbus_server_params={'host':'127.0.0.1','port':502}
DB_TYPE=Consts.MYSQL        #тип используемой СУБД (доступные в dbclassfactory)
users=[             # пользователи админки gather-a
    {'id': 1, 'first_name': 'Igor', 'middle_name': '', 'second_name': 'Dubov', 'login': 'div', 'pass': '123'},
] 