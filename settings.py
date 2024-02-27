
CLIENT_VERSION = 0.1
STATE_ARG = 'args.status'
STATE_TIME_ARG = 'args.saved_time'
TECH_IDLE_ARG = 'args.tech_timeout'
CAUSEID_ARG = 'args.cause_id'
CAUSE_TIME_ARG = 'args.cause_time'
IDLE_HANDLERID_ARG = 'args.idle_handler_id'
IDLE_STATES = (1, 2)  # состояния при которых фиксируется простой
CAUSE_CHECK_TIMEOUT = 120  # таймаут указания причины простоя
IDLE_CAUSES = {1: 'Не подтверждена', 2: 'Технологический простой',
               3: "Авария", 4: "Нет сырья", 5: "Нет задания", 6: "Плановый простой"}
DEFAILT_IDLE_CAUSES = {1: 'Не подтверждена', 2: 'Технологический простой',
               3: "Авария", 4: "Нет сырья", 5: "Нет задания", 6: "Плановый простой"}
NOT_CHEKED_CAUSE = 1  # причина простоя по умолсанию (если не указана)
TECH_IDLE_ID = 2
STATES = ['N/A', 'Откл', 'Простой', 'Работа']
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

DEFAULT_CAUSES = [1, 2] # причины которые не отображаются в интерфейсе оператора 
MIN_STORED_IDLE_LENGTH=5
MIN_STORED_STATE_LENGTH=5
# id каналов и разрешенные ip, к которым могут подключаться клиенты контроля простоя через запрос ?m=id
ALLOWED_MACHINES = {2000: [], 2120: [], 2040:[]}
OPERATORS = {1111: {'name': 'Петров А.П.'},
             2222: {'name': 'Сидоров А.Р.'}}

web_server_path_params = {
    'static_path': 'web/webdata',
    'template_path': 'web/webdata',
    'static': 'web/webdata',
    'js': 'web/webdata/js',
    'css': 'web/webdata/css',
    'images': 'web/webdata/images',
}

CHECK_AUTORIZATION = False
DEFAULT_USER = {'id': 0, 'name': '', 'm_name': '',
                's_name': '', 'login': '', 'password': ''
                }
                
users = [
    {'id': 1, 'name': 'Igor', 'm_name': '',
        's_name': 'Dubov', 'login': 'div', 'password': '123'},
]

user_machines = {1: [2000, 2040]}