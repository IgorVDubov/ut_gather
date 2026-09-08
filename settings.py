CLIENT_VERSION = 0.1
PROJECTS_IDS = {2, 3}
DATE_FORMAT_DB = "%Y-%d-%m %H:%M:%S"
STATE_ARG = "args.state"
STATE_TIME_ARG = "args.current_state_time"
TECH_IDLE_ARG = "args.tech_timeout"
CAUSEID_ARG = "args.current_cause"
CAUSE_TIME_ARG = "args.cause_time"
IDLE_HANDLERID_ARG = "args.idle_handler_name"
STATE_COUNTER_NO = 7
STATE_MIDDLE_NO = 6
DEMO_PROJECT = 0
IDLE_STATES = (0, 1, 2)  # состояния при которых фиксируется простой
CAUSE_CHECK_TIMEOUT = 120  # таймаут указания причины простоя
IDLE_CAUSES = {
    1: ("Не подтверждена", 0),
    2: ("Техпростой", 0),
    3: ("Ремонт", 6),
    11: ("Техническое обслуживание", 9),
    4: ("Нет сырья", 4),
    5: ("Нет задания", 8),
    6: ("Плановый   простой", 2),
    7: ("Технический перерыв", 5, "#cbf339"),
    8: ("Переналадка", 3),
    9: ("Загрузка   материала", 1),
    10: ("Работа с технологом", 7),
}
DEFAILT_IDLE_CAUSES = {
    1: "Не подтверждена",
    2: "Технологический простой",
}
NOT_CHEKED_CAUSE = 1  # причина простоя по умолсанию (если не указана)
TECH_IDLE_ID = 2
STATES = ["N/A", "Откл", "Простой", "Работа"]
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

DEFAULT_CAUSES = [1, 2]  # причины которые не отображаются в интерфейсе оператора
MIN_STORED_IDLE_LENGTH = 10
MIN_STORED_STATE_LENGTH = 10
# id каналов и разрешенные ip, к которым могут подключаться клиенты контроля простоя через запрос ?m=id
ALLOWED_MACHINES = {
    2000: [],
    2120: [],
    2040: [],
    1501: [],
    1416: [],
    2901: [],
    2902: [],
}
DEFAILT_OPERATOR = 0000
OPERATORS = {
    0000: {"name": "Оператор"},
    1111: {"name": "Оператор 1"},
    2222: {"name": "Оператор 2"},
}
OPERATOR_LOGIN = False
web_server_path_params = {
    "static_path": "web/webdata",
    "template_path": "web/webdata",
    "static": "web/webdata",
    "js": "web/webdata/js",
    "css": "web/webdata/css",
    "images": "web/webdata/images",
}

CHECK_AUTORIZATION = False
DEFAULT_USER = {
    "id": 0,
    "name": "",
    "m_name": "",
    "s_name": "",
    "login": "",
    "password": "",
}

users = [
    {
        "id": 1,
        "name": "Igor",
        "m_name": "",
        "s_name": "Dubov",
        "login": "div",
        "password": "123",
    },
]

# user_machines = {1: [2000, 2040, ]}
