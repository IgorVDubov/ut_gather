import handlers
from handlers import lib
from gather.consts import AI, DI, INT, FLOAT,LIST


'''
Список опрашиваемых модулей
id->str: для идентификации
type->str: тип устройства, реализовано: ModbusTcp
ip->str: ip или testN, тест - эммулятор сигнала с алгоритмом работы задающимся N
port->int: порт модуля
unit->int: номер устройства (в ТСР обычно 1, если ТСР конвертер в 485 - номер в 485-й сети)
address->int: с какого адреса начинаес читать данные
count->int: кол-во адресов для чтения
function->int: модбас функция: реализованы: 2-read_discrete_inputs, 3-read_holding_registers, 4-read_input_registers  
format->str: AI - массив бит, DI - массив чисел длинной count
period->float: период опроса в сек
handler->callable: функция предобработки данных из channel_handlers 
''' 
module_list=[ 
            {'id':'machine1','type':'ModbusTcp','ip':'192.168.1.200','port':'502','unit':0x1, 'address':0, 'regCount':2, 'function':3, 'format':DI, 'period':1},
            ]    
  

'''
словарь конфигурации каналов:
{'id':4209,'moduleId':'test3','type':'AI','sourceIndexList':[0], 
            'handler':channel_handlers.middle10,
            'args':{'name':val,...}}
id->int: id объекта контроля
moduleId->str: модуль с входами датчиков от  объекта контроля
type->str: di биты состояния, ai- аналоговые данные - одно значение, нет группового чтения
sourceIndexList->list: позиции (индексы с 0) данных массива результата чтения модуля moduleId
handler->str: имя функции обработчика результата (в модуле handler_funcs)
args: запись аргументов: 
    'args':{
        'argName1':value[число] в args создается аргумент с именем argName1 и значением value 
        'argName1':'id' в args создается аргумент с именем argName1 и привязкой к объекту канала id 
        'argName1':'id.arg' в args создается аргумент с именем argName1 и привязкой к аргументу arg объекта канала id 
        'argName1':'id.arg.v1' в args создается аргумент с именем argName1 и привязкой к аргументу arg.v1 объекта канала id 
        'argName1':'self.v1' в args создается аргумент с именем argName1 и привязкой к аргументу v1 этого канала 
}
'''   
channels_config={
    'channels':[
        {'id':1001, 'args':{
                        'grWork':30,
                        'grStand':1,
                        'dostTimeout':5,
                        'tech_timeout':10,
                    }
        },
    ],
    'nodes':[  
        {'id':4001,'moduleId':None,'type':'AI','sourceIndexList':[], 
                        'handler':handlers.prog1,
                        'args':{
                            'result_in':'4001.result',
                            'result_link_ch':'5001.result',
                        }},
        {'id':5003,'moduleId':None,'type':'AI','sourceIndexList':[], # счетчик
                        },
        {'id':5004,'moduleId':None,'type':'AI','sourceIndexList':[], # сброс счетчика
                        },
        {'id':5002,'moduleId':'machine1','type':'DI','sourceIndexList':[0,1], 'handler':handlers.signal_techtimeout,'args':{
                        'channel_id':5002,
                        'result_in':'5002.result_in',
                        'dost':'5002.dost',
                        'counter_in':'5003.result',
                        'counter_reset':'5004.result',
                        'write_init':'13001.args.write_init_5002',
                        'write_counter':'13001.args.write_counter_5002',
                        'status_ch_b1':'11001.args.b3',
                        'status_ch_b2':'11001.args.b4',
                        'dost_timeout':'1001.args.dostTimeout',
                        'tech_timeout':'1001.args.tech_timeout',
                        'status':0,
                        'not_dost_counter':0,
                        'init':True,    
                        'saved_status':0,
                        'saved_length':0,
                        'saved_time':0,
                        'double_write':False,
                        'buffered':False,
                        'buffer_time':0,
                        'buffer_status':0,
                        'dost_length':0,
                        'NA_status_before':False,
                        'was_write_init':False,
                        'dbQuie':'12001',
                        'сause':'17002.args.cause_id',
                        'idle_handler_id':17002,
                        'project_id':7,
                        }},
        {'id':5001,'moduleId':None,'type':'AI','sourceIndexList':[], 'handler':handlers.r_level_timeout,'args':{
                        'channel':'4001',
                        'dbChannel':None,
                        'writeInit':'13001.args.write_init_5001',
                        'statusCh_b1':'11001.args.b1',
                        'statusCh_b2':'11001.args.b2',
                        'grWork':'1001.args.grWork',
                        'grStand':'1001.args.grStand',
                        'dostTimeout':'1001.args.dostTimeout',
                        'minLength':'1001.args.tech_timeout',
                        'notDost':0,
                        'NAStatusBefore':False,
                        'currentState':0,
                        'currentStateTime':0,
                        'currentInterval':0,
                        'buffered':False,
                        'statusDB':0,
                        'lengthDB':0,
                        'timeDB':0,
                        'init':True,
                        'dbQuie':'12001',
                        'idle_handler_id':17001,
                        'project_id':7,
                        }},
    ],
    'programms':[
        {'id':11001,  'handler':lib.bits_to_word,
                'args':{'result':'1001.result',
                        'b1':0,'b2':0,'b3':0,'b4':0,'b5':0,'b6':0,'b7':0,'b8':0,'b9':0,'b10':0,
                        'b11':0,'b12':0,'b13':0,'b14':0,'b15':0,'b16':0
                        }},
        {'id':13001,  'handler':handlers.day_scheduler,
                'args':{
                        'write_init_5001':False,
                        'write_init_5002':False,
                        'write_counter_5002':False
                        }},
        
        {'id':17001,  'handler':handlers.idle,
                'args':{
                    'state':'5001.args.currentState',
                    'machine_id':5001,
                    'techidle_lenhth':'5001.args.minLength',
                    'cause_id':None,
                    'current_cause':None,
                    'reset_idle_flag':False,
                    'set_cause_flag':False,
                    'restore_idle_flag':False,
                    'db_quie':'12001',
                    'project_id':7,
                }},
        {'id':17002,  'handler':handlers.idle,
                'args':{
                    'state':'5002.args.status',
                    'machine_id':5002,
                    'techidle_lenhth':'5002.args.tech_timeout',
                    'cause_id':None,
                    'current_cause':None,
                    'reset_idle_flag':False,
                    'set_cause_flag':False,
                    'restore_idle_flag':False,
                    'project_id':7,
                }},
        
    ],
    'dbquie':[
        {'id':12001},
        ]
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


                                
mb_server_addr_map=[
]
    # {'unit':0x1, 'map':{
    #     # 'di':[{'id':4001, 'attr':'result', 'addr':0, 'len':16}
    #     #     ],
    #     'hr':[{'channel':'4001.result', 'addr':0, 'type':INT},
    #           {'channel':'4001.args.v','addr':1,'type':FLOAT, 'len':2}
    #     ]
    #     }
    # }]


MBServerAdrMap=mb_server_addr_map
channelsConfig=channels_config
ModuleList=module_list
