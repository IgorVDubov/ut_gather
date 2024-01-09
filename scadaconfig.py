from handlers import (db_writer,
                      write_init,
                      r_level_timeout, 
                      idle, 
                      ai2021, 
                      signal_techtimeout, 
                      signal_tout_2_counters)
from handlers import lib

from gathercore.consts import ValTypes, Formats, ModbusFuncs, SourceTypes


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
    # # LR COCOS
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
    
    # #  LR Sinthepon
    # {'id': 'synth_counters_reset_out',
    #  'type': SourceTypes.MODBUS_TCP, 'ip': '172.19.10.244', 'port': '502',
    #  'unit': 0x1, 'address': 0, 'count': 1,
    #  'function':  ModbusFuncs.WRITE_CO, 'format': ValTypes.BIT,'period': 1},
    # {'id': 'synth_product',
    #  'type': SourceTypes.MODBUS_TCP, 'ip': '172.19.10.244', 'port': '502',
    #  'unit': 0x1, 'address': 0, 'count': 2,
    #  'function':  ModbusFuncs.READ_HR, 'format': ValTypes.INT32, 'order': Formats.ABCD,
    #  'period': 1},
    # {'id': 'synth_rulon',
    #  'type': SourceTypes.MODBUS_TCP, 'ip': '172.19.10.244', 'port': '502',
    #  'unit': 0x1, 'address': 2, 'count': 2,
    #  'function':  ModbusFuncs.READ_HR, 'format': ValTypes.INT32, 'order': Formats.ABCD,
    #  'period': 1},
    # {'id': 'synth_v',
    #  'type': SourceTypes.MODBUS_TCP, 'ip': '172.19.10.244', 'port': '502',
    #  'unit': 0x1, 'address': 4, 'count': 1,
    #  'function':  ModbusFuncs.READ_HR, 'format': ValTypes.INT16, 'order': Formats.AB,
    #  'period': 1},
    # {'id': 'synth_status',
    #  'type': SourceTypes.MODBUS_TCP, 'ip': '172.19.10.244', 'port': '502',
    #  'unit': 0x1, 'address': 5, 'count': 1,
    #  'function':  ModbusFuncs.READ_HR, 'format': ValTypes.INT16, 'order': Formats.AB,
    #  'period': 1},
    # {'id': 'synth_counters_reset_in',
    #  'type': SourceTypes.MODBUS_TCP, 'ip': '172.19.10.244', 'port': '502',
    #  'unit': 0x1, 'address': 0, 'count': 1,
    #  'function':  ModbusFuncs.READ_CO, 'format': ValTypes.BIT,'period': 1},
    
    # ******************************************************************************************
    # {'id': 'synth_status1',
    #  'type': SourceTypes.MODBUS_TCP, 'ip': '172.19.10.244', 'port': '502',
    #  'unit': 0x1, 'address': 7, 'count': 1,
    #  'function':  ModbusFuncs.READ_HR, 'format': ValTypes.INT16, 'order': Formats.AB,
    #  'period': 1},
    # {'id': 'synth_status2',
    #  'type': SourceTypes.MODBUS_TCP, 'ip': '172.19.10.244', 'port': '502',
    #  'unit': 0x1, 'address': 9, 'count': 1,
    #  'function':  ModbusFuncs.READ_HR, 'format': ValTypes.INT16, 'order': Formats.AB,
    #  'period': 1},
    # {'id': 'synth_counters_reset_in',
    #  'type': SourceTypes.MODBUS_TCP, 'ip': '172.19.10.244', 'port': '502',
    #  'unit': 0x1, 'address': 25, 'count': 1,
    #  'function':  ModbusFuncs.READ_HR, 'format': ValTypes.INT16, 'order': Formats.AB,
    #  'period': 1},
    #  {'id': 'write_init_reset',
    #  'type': SourceTypes.MODBUS_TCP, 'ip': '127.0.0.1', 'port': '5021',
    #  'unit': 0x1, 'address': 0, 'count': 1,
    #  'function':  ModbusFuncs.WRITE_CO, 'format': ValTypes.BIT,'period': 1},
     

    
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
             'tech_timeout': 20,
         }
         },
        {'id': 2000,            # DEMO machine for idles
         'handler': r_level_timeout,
         'args': {
             'channel_id': 2000,
             'result_in': '2000.result',
            #  'result_in': '2000.result_in',
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
        {'id': 1001,                # канал со значениями инициализации
         'args': {
             'grWork': 30,
             'grStand': 1,
             'dostTimeout': 5,
             'tech_timeout': 10,
             'sedna_tech_timeout': 720,  # Техпростой SEDNA
             'cocos_tech_timeout': 300,  # Техпростой COCOS
             'synth_tech_timeout': 300,  # Техпростой СИНТЕПОН
         }
         },
    ],
    'nodes': [
        
        # {'id': 2121,        # COCOS AI
        #  'moduleId': 'cocos_ai', 'sourceIndexList': [0],
        #  'handler':ai2021,
        #  'args':{
        #      'result': 'self.result',
        #      'result_in': 'self.result_in',
        #      # 'in_dost':'2121.dost',
        #      'in_dost': True,
        #      'counter': 0,
        #      'reset_counter': False,
        #      'k': 0.00010584,
        #      'counter_acc': 0,
        #      'min_ai': 10,
        #  }
        #  },
        # {'id': 2120,        # COCOS STATUS
        #  'moduleId': 'cocos_di', 'sourceIndexList': [0, 1],
        #  'handler':signal_techtimeout,
        #  'args':{
        #      'channel_id': 2120,
        #      'result_in': '2120.result_in',
        #      'dost': '2120.dost',
        #      'counter': '2121.args.counter',
        #      'counter_reset': '2121.args.reset_counter',
        #      'write_init': '11002.args.write_init_2120',
        #      'write_counter': '11002.args.write_counter_2120',
        #      'status_ch_b1': '11001.args.b7',
        #      'status_ch_b2': '11001.args.b8',
        #      'dost_timeout': '1001.args.dostTimeout',
        #      'tech_timeout': '1001.args.cocos_tech_timeout',
        #      'status': 0,
        #      'not_dost_counter': 0,
        #      'init': True,
        #      'saved_status': 0,
        #      'saved_length': 0,
        #      'saved_time': 0,
        #      'write_buffer': False,
        #      'buffered': False,
        #      'buffer_time': 0,
        #      'buffer_status': 0,
        #      'dost_length': 0,
        #      'NA_status_before': False,
        #      'was_write_init': False,
        #      'db_quie': '12001',
        #      'cause': '17002.args.current_cause',
        #      'cause_time': '17002.args.current_cause_time',
        #      'idle_handler_id': 17002,
        #      'project_id': 3,
        #      'operator_id': None,
        #      'stop_signal': False,
        #  }
        #  },
        # {'id': 2040,                                        # Линия Синтепона status
        #  'moduleId': 'synth_status', 'sourceIndexList': [0],
        #  'handler':signal_tout_2_counters,
        #  'args':{
        #      'channel_id': 2040,
        #      'result_in': '2040.result_in',
        #      'dost': '2040.dost',
        #      'counter_1': '2041.result',
        #      'counters_reset': '2044.result_in',
        #      'counters_reset_in': '2045.result',
        #      'counter_2': '2042.result_in',
        #      'counter_1_id': 2041,
        #      'counter_2_id': 2042,
        #      'write_init': '11002.args.write_init_2040',
        #      'write_counters': '11002.args.write_counter_2040',
        #      'status_ch_b1': '11001.args.b11',
        #      'status_ch_b2': '11001.args.b12',
        #      'dost_timeout': '1001.args.dostTimeout',
        #      'tech_timeout': '1001.args.synth_tech_timeout',
        #      'status': 0,
        #      'not_dost_counter': 0,
        #      'init': True,
        #      'saved_status': 0,
        #      'saved_length': 0,
        #      'saved_time': 0,
        #      'write_buffer': False,
        #      'buffered': False,
        #      'buffer_time': 0,
        #      'buffer_status': 0,
        #      'dost_length': 0,
        #      'NA_status_before': False,
        #      'was_write_init': False,
        #      'db_quie': '12001',
        #      'cause': '17003.args.current_cause',
        #      'cause_time': '17003.args.current_cause_time',
        #      'idle_handler_id': 17003,
        #      'project_id': 3,
        #      'operator_id': None,
        #      'stop_signal': False,
        #     }
        #  },
        # {'id': 2041,                                        # Линия Синтепона счетчик продукции
        #  'moduleId': 'synth_product', 'sourceIndexList': [0], },
        # {'id': 2042,                                        # Линия Синтепона счетчик продукции
        #  'moduleId': 'synth_rulon', 'sourceIndexList': [0], },
        # {'id': 2043,                                        # Линия Синтепона скорость выхода продукции
        #  'moduleId': 'synth_v', 'sourceIndexList': [0],
        #  'handler': lib.mult,
        #  'args': {
        #      'input': '2043.result_in',
        #      'output': '2043.result',
        #      'k': 0.1,
        #     },

        #  },
        # {'id': 2044,                                        # Линия Синтепона запись сигнала сброса счетчиков выхода продукции
        #  'moduleId': 'synth_counters_reset_out', },              
        # {'id': 2045,                                        # Линия Синтепона чтение сигнала сброса счетчиков выхода продукции
        #  'moduleId': 'synth_counters_reset_in', },              
        # {'id': 2999,                                        # запись регистра общей записи write_init собственного MBExchangeServer
        #  'moduleId': 'write_init_reset', },
    ],
    'programms': [
        
        {'id': 10001,       # wachdog seconds
         'handler': lib.current_second,
         'args': {
             'result': 'self.result',
         }
         },
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
        {'id': 11001,       # LR status byte
         'handler': lib.bits_to_word,
         'args': {
             'result': 'self.result',
             'b1': 0, 'b2': 0, 'b3': 0, 'b4': 0,
             'b5': 0, 'b6': 0, 'b7': 0, 'b8': 0,
             'b9': 0, 'b10': 0, 'b11': 0, 'b12': 0,
             'b13': 0, 'b14': 0, 'b15': 0, 'b16': 0
         }
         },
        # {'id': 11002,       # write init
        #  'handler': db_writer,
        #  'args': {
        #      'scheduller_write_states': '13001.args.write_init',
        #      'scheduller_write_counters': '13002.args.write_init',
        #      'mb_write_init': None,                        # сюда значение из функции записи регистра MBExchangeServer 
        #      'mb_write_init_reset': '2999.result_in',       # пишем значение в регистр собственного MBExchangeServer
        #      'mb_write_runs_flag': False,                   # 
        #      'write_init_2120': False,
        #      'write_counter_2120': False,
        #      'write_init_2040': False,
        #      'write_counter_2040': False,
        #  }
        #  },

        {'id': 17000,               # DEMO idles processing
         'handler': idle,  
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
        # {'id': 17002,               # COCOS idles processing
        #  'handler': idle,  
        #  'args': {
        #      'state': '2120.args.status',
        #      'machine_id': 2120,
        #      'operator_id': '2120.args.operator_id',
        #      'techidle_lenhth': '2120.args.tech_timeout',
        #      'cause_id': None,
        #      'current_cause': None,
        #      'current_cause_time': None,
        #      'reset_idle_flag': False,
        #      'set_cause_flag': False,
        #      'restore_idle_flag': False,
        #      'db_quie': '12001',
        #      'project_id': 7,
        #  }},
        # {'id': 17003,               # Синтепон idles processing
        #  'handler': idle,  
        #  'args': {
        #      'state': '2040.args.status',
        #      'machine_id': 2040,
        #      'operator_id': '2040.args.operator_id',
        #      'techidle_lenhth': '2040.args.tech_timeout',
        #      'cause_id': None,
        #      'current_cause': None,
        #      'current_cause_time': None,
        #      'reset_idle_flag': False,
        #      'set_cause_flag': False,
        #      'restore_idle_flag': False,
        #      'db_quie': '12001',
        #      'project_id': 7,
        #  }},
    ],
    'dbquie': [
        {'id': 12001},
    ],
    'scheduler': [
        {'id': 13001,  # scheduller записть статусов
         'time_list': ['07:00:02', '15:30:02', '23:30:02', '19:00:02', '11:30:02'],
         'handler':write_init,
         'args': {
             'write_init': False,
         }},
        {'id': 13002,  # scheduller запись счетчиков
         'time_list': ['06:59:59', '15:29:59', '23:29:59', '18:59:59', '11:29:59'],
         'handler':write_init,
         'args': {
             'write_init': False,
         }},
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
    {'unit': 0x1,
     'map': {
        #  'co': [
        #      {'addr': 0, 'channel': '11002.args.mb_write_init', 'type': ValTypes.BIT},  # write init
        #        ],
        #  #'di': [],
        #  'hr': [
        #         # {'channel': '2120.args.status', 'addr': 0, 'type': ValTypes.INT, 'order': Formats.AB},
        #         {'addr': 0, 'channel': '11001.result',
        #             'type': ValTypes.INT32, 'order': Formats.CDAB},         # status LR
        #         {'addr': 4, 'channel': '10001.result',
        #             'type': ValTypes.INT16},                                # wachdog seconds
        #         {'addr': 16, 'channel': '2121.args.counter',
        #             'type': ValTypes.FLOAT, 'order': Formats.ABCD},         # 2121 Counter
        #         {'addr': 18, 'channel': '2121.result',
        #             'type': ValTypes.FLOAT, 'order': Formats.ABCD},         # 2121 Result скорость выхода
        #         # {'addr': 292, 'channel': '11001.result',
        #         # 'type': ValTypes.INT32, 'order': Formats.CDAB},           # LR StatusByte
        #         {'addr': 20,   'channel': '2041.result',
        #             'type': ValTypes.FLOAT, 'order': Formats.ABCD},         # счетчик продукции
        #         {'addr': 22,   'channel': '2042.result',
        #             'type': ValTypes.FLOAT, 'order': Formats.ABCD},         # LR счетчик рулонов
        #         {'addr': 24,   'channel': '2043.result',
        #         'type': ValTypes.FLOAT, 'order': Formats.ABCD},             # LR скорость выхода
        #         ]
     }
     }
]
