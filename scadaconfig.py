from handlers import r_level_timeout, idle
from handlers import lib
from gather.consts import ValTypes, Formats, ModbusFuncs, SourceTypes


# Список опрашиваемых модулей
# id:str: для идентификации
# type:str: тип устройства, реализовано: ModbusTcp
# ip:str: ip или testN, тест - эммулятор сигнала с алгоритмом работы задающимся N
# port:int: порт модуля
# unit:int: номер устройства (в ТСР обычно 1, если ТСР конвертер в 485 - номер в 485-й сети)
# address:int: с какого адреса начинаес читать данные
# count:int: кол-во адресов для чтения
# function:ModbusFuncs: модбас функция: реализованы: 2-read_discrete_inputs, 3-read_holding_registers, 4-read_input_registers
# format:ValTypes:  читаеет источник и предобазует результат в следующийе форматы:
#                   DI биты состояния [1,1,0,0] | [True, True, False,...], default_reg_count = 1 или count
#                   FLOAT- аналоговые данные default_reg_count = 2
#                   INT16 - 2 байтный INT, default_reg_count = 1
#                   INT32 - 4 байтный INT, default_reg_count = 2
#                   LIST - list[int16] - массив целых default_reg_count = 1 или count
# count: int - кол-во считанных подряд регистров
# order:Formats -> порядок распаковки ABCD | CDAB для FLOAT, INT32, AB | BA для INT16
# period:float: период опроса в сек
# handler:callable: функция предобработки данных из channel_handlers

module_list = [
    # {'id': 'cocos_di',
    #  'type': SourceTypes.MODBUS_TCP, 'ip': '127.0.0.1', 'port': '511',
    #  'unit': 0x1, 'address': 0, 'function': ModbusFuncs.READ_DI,
    #  'count': 8,
    #  'format': ValTypes.DI,
    #  'period': 1},
    # {'id': 'cocos_ai',
    #  'type': SourceTypes.MODBUS_TCP, 'ip': '127.0.0.1', 'port': '511',
    #  'unit': 0x1, 'address': 0, 'count': 1,
    #  'function':  ModbusFuncs.READ_IR, 'format': ValTypes.INT16, 'order': Formats.AB,
    #  'period': 1},
]


# словарь конфигурации каналов:
# {'id':4209,'moduleId':'test3','type':'AI','sourceIndexList':[0],
#             'handler':channel_handlers.middle10,
#             'args':{'name':val,...}}
# id->int: id объекта контроля
# moduleId->str: модуль с входами датчиков от  объекта контроля
# type->: DI биты состояния [1,1,0,0] | [True, True, False,...],
#            AI- аналоговые данные - одно значение, нет группового чтения
#           LIST - list[int]
# sourceIndexList->list: позиции (индексы с 0) данных массива результата чтения модуля moduleId
# handler->str: имя функции обработчика результата (в модуле handler_funcs)
# args: запись аргументов:
#     'args':{
#         'argName1':value[число] в args создается аргумент с именем argName1 и значением value
#         'argName1':'id' в args создается аргумент с именем argName1 и привязкой к объекту канала id
#         'argName1':'id.arg' в args создается аргумент с именем argName1 и привязкой к аргументу arg объекта канала id
#         'argName1':'id.arg.v1' в args создается аргумент с именем argName1 и привязкой к аргументу arg.v1 объекта канала id
#         'argName1':'self.v1' в args создается аргумент с именем argName1 и привязкой к аргументу v1 этого канала
# }
channels_config = {
    'channels': [
        {'id': 1000,                # канал со значениями инициализации DEMO
         'args': {
             'grWork': 30,
             'grStand': 1,
             'dostTimeout': 5,
             'tech_timeout': 10,
         }
         },
        {'id': 1001,                # канал со значениями инициализации
         'args': {
             'grWork': 30,
             'grStand': 1,
             'dostTimeout': 5,
             'tech_timeout': 10,
         }
         },
    ],
    'nodes': [
        {'id': 2000,
         'moduleId': None,
         'sourceIndexList': [0],
         'handler': r_level_timeout,
         'args':{
             'channel_id': 2000,
             'result_in': '2000.result_in',
             'dost': True,
            #  'dost': '2000.dost',
             'write_init': False,
             'status_ch_b1': '11000.args.b1',
             'status_ch_b2': '11000.args.b2',
             'gr_work': '1000.args.grWork',
             'gr_stand': '1000.args.grStand',
             'dost_timeout': '1000.args.dostTimeout',
             'tech_timeout': '1000.args.tech_timeout',
             'not_dost_counter': 0,
             'na_status_before': False,
             'status': 0,
             'current_state': 0,
             'current_state_time': 0,
             'current_interval': 0,
             'buffered': False,
             'status_db': 0,
             'lengthDB': 0,
             'time_db': 0,
             'init': True,
             'db_quie': '12001',
             'idle_handler_id': 17000,
             'project_id': 0,
             'operator_id': None,
             'cause_id': '17000.args.current_cause',
             'cause_time': '17000.args.current_cause_time',
         }
         },
        # {'id': 2121,        # AI
        #  'moduleId': 'cocos_ai', 'sourceIndexList': [0],
        #  'handler':handlers.ai2021,
        #  'args':{
        #         'result': 'self.result',
        #         'result_in': 'self.result_in',
        #         # 'in_dost':'2121.dost',
        #         'in_dost': True,
        #         'counter': 0,
        #         'reset_counter': False,
        #         'k': 0.00010584,
        #         'counter_acc': 0,
        #         'min_ai': 10,
        #         }
        # },
        # {'id': 2120,
        #  'moduleId': 'cocos_di', 'sourceIndexList': [0, 1],
        #  'handler':handlers.signal_techtimeout,
        #  'args':{
        #         'channel_id': 2120,
        #         'result_in': '2120.result_in',
        #         'dost': '2120.dost',
        #         'counter': '2121.args.counter',
        #         'counter_reset': '2121.args.reset_counter',
        #         'write_init': '13002.args.write_init_2120',
        #         'write_counter': '13002.args.write_counter_2120',
        #         'status_ch_b1': '11001.args.b7',
        #         'status_ch_b2': '11001.args.b8',
        #         'dost_timeout': '1001.args.dostTimeout',
        #         'tech_timeout': '1001.args.tech_timeout',
        #         'status': 0,
        #         'not_dost_counter': 0,
        #         'init': True,
        #         'saved_status': 0,
        #         'saved_length': 0,
        #         'saved_time': 0,
        #         'double_write': False,
        #         'buffered': False,
        #         'buffer_time': 0,
        #         'buffer_status': 0,
        #         'dost_length': 0,
        #         'NA_status_before': False,
        #         'was_write_init': False,
        #         'db_quie': '12001',
        #         'cause': '17002.args.current_cause',
        #         'cause_time': '17002.args.current_cause_time',
        #         'idle_handler_id': 17002,
        #         'project_id': 3,
        #         'operator_id': None,
        #         }},

    ],
    'programms': [
        {'id': 11000,       # DEMO status byte
         'handler': lib.bits_to_word,
         'args': {
             'result': 'self.result',
             'b1': 0, 'b2': 0, 'b3': 0, 'b4': 0,
             'b5': 0, 'b6': 0, 'b7': 0, 'b8': 0,
             'b9': 0, 'b10': 0, 'b11': 0, 'b12': 0,
             'b13': 0, 'b14': 0, 'b15': 0, 'b16': 0
         }
         },
        # {'id': 11001,       # status byte
        #  'handler': lib.bits_to_word,
        #  'args': {
        #      'result': 'self.result',
        #      'b1': 0, 'b2': 0, 'b3': 0, 'b4': 0,
        #      'b5': 0, 'b6': 0, 'b7': 0, 'b8': 0,
        #      'b9': 0, 'b10': 0, 'b11': 0, 'b12': 0,
        #      'b13': 0, 'b14': 0, 'b15': 0, 'b16': 0
        #     }
        # },

        {'id': 17000, 'handler': idle,  # DEMO idles processing
         'args': {
             'state': '2000.args.status',
             'machine_id': 2000,
             'operator_id': '2000.args.operator_id',
             'techidle_lenhth': '2000.args.tech_timeout',
             'cause_id': None,
             'current_cause': None,
             'current_cause_time': None,
             'reset_idle_flag': False,
             'set_cause_flag': False,
             'restore_idle_flag': False,
             'db_quie': '12001',
             'project_id': 0,
         }},
        # {'id': 17002, 'handler': handlers.idle,     #idles processing
        #         'args': {
        #             'state': '2120.args.status',
        #             'machine_id': 2120,
        #             'operator_id': '2120.args.operator_id',
        #             'techidle_lenhth': '2120.args.tech_timeout',
        #             'cause_id': None,
        #             'current_cause': None,
        #             'current_cause_time': None,
        #             'reset_idle_flag': False,
        #             'set_cause_flag': False,
        #             'restore_idle_flag': False,
        #             'db_quie': '12001',
        #             'project_id': 7,
        #         }},
    ],
    'dbquie': [
        {'id': 12001},
    ],
    'scheduler': [
        # {'id': 13002,           #scheduller
        #  'time_list': ['07:00', '15:30', '23:30', '19:00'],
        #     'handler':handlers.scheduler.write_init,
        #     'args': {
        #         'write_init_2120': False,
        #         'write_counter_2120': False,
        #     }},
    ],
}


#
# разметка адресов Модбас сервера для внешнего доступа
# unit->int: номер unit-а по умолчанию 1
# map ->dict: общее:
#                 id->int: id объекта контроля
#                 addr->int: адрес (смещение) первого регистра
#             co - Coils initializer
#             di - discrete_inputs чтение функцией 2
#                 len->int: кол-во регистров
#             hr - holding_registers чтение функцией 3
#             ir - input_registers чтение функцией 4
#                 type->str:      float - 2xWord CD-AB(4Byte);
#                                 int - 1xWord (2Byte)


mb_server_addr_map = [
    # {'unit': 0x1,
    #  'map': {
    #     # 'di':[{'id':4001, 'attr':'result', 'addr':0, 'len':16}
    #     #     ],
    #     'hr': [
    #         {'channel': '2120.args.status', 'addr': 0, 'type': ValTypes.INT, 'order': Formats.AB},
    #         {'channel': '2121.args.counter', 'addr': 328, 'type': ValTypes.FLOAT, 'order': Formats.ABCD},   # 2121 Counter
    #         {'channel': '2121.result', 'addr': 330, 'type': ValTypes.FLOAT, 'order': Formats.ABCD},         # 2121 Result скорость выхода
    #         {'channel': '11001.result', 'addr': 292, 'type': ValTypes.INT32, 'order': Formats.CDAB},            # LR StatusByte
    #     ]
    #     }
    # }
]
