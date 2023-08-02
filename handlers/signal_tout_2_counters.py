from datetime import datetime

import dataconnector as dc
import settings
from loguru import logger


def signal_tout_2_counters(vars):
    '''
    signals values with timeout
    VARS:
        'channel_id': ch_id
        'result_in':'5002.resultIn', -              вход от источника
        'dost': 'self.dost',                        достоверность
        'counter_1':'_.result',                     вход от источника счетчика1
        'counters_reset':'_.result_in',             вход от источника записи сигнала сброса счетчика
        'counters_reset_in': '_.result',            вход от источника чтения сигнала сброса счетчика
        'counter_2': _.result_in',                  вход от источника счетчика2
        'counter_1_id': _                           id счетчика2 для записи в БД
        'counter_2_id': _                           id счетчика2 для записи в БД
        'write_init':'прогр_db_writer.args.writeInit',    сигнал принудительной записи
        'write_counters':'прогр_db_writer.args.write_counter_idканала' сигнал записи счетчика
        'status_ch_b1':'11001.args.b1',         бит1 канала статуса
        'status_ch_b2':'11001.args.b2',         бит2 канала статуса
        'dost_timeout':'1001.args.dost_timeout', таймаут достоверности ,с
        'tech_timeout':'1001.args.minLength',   техпростой ,с
        'status':0,                             текущий статус
        'not_dost_counter':0,                   счетчик времени недостоверности
        'init':True,                            флаг инициализации
        'saved_status':0,                       текущий сохраненный отрезок статус
        'saved_length':0,                       текущий сохраненный отрезок длительтность
        'saved_time':0,                         текущий сохраненный отрезок время начала отрезка
        'buffered':False,                       флаг наличия подвешенного отрезок (техпростой или нет)
        'buffer_time':0,                        буферезированный отрезок время начала
        'buffer_status':0,                      буферезированный отрезок сосотяние
        'write_buffer':False,                   флаг для записи подвешенного отрезка при принудительной записи
        'dost_length':0,                        буферезированный отрезок
        'NA_status_before':False,               сохраненный предыдущий статус NA
        'was_write_init':False,                 флаг произошедшей принудительной записи в БД
        'dbQuie':'12001',                       связь с очередью записи в БД
        'cuase':'17002.args.cause_id',          текущая причина простоя
        'cause_time': '17003.args.current_cause_time', текущее время начала простоя
        'idle_handler_id':17002,                канал обработчика простоев
        'project_id': 3,                        id проекта к которому относится канал
        'operator_id': None,                    текущий оператор
        'stop_signal': False,                   сигнал остановки системы
    '''
    time_now = datetime.now()
    db_write_flag = False
    dost_change_flag = False
    NA_status = False
    result_in_error = False
        
    if vars.stop_signal:
        logger.log('PROG', '!!!!!!!!!!!!!!!!!    get stop signal       !!!!!!!!!!!!!!!!!!!!!!!!!')
        dc.db_put_state(vars.db_quie,
                        {'id': vars.counter_1_id,
                         'project_id': vars.project_id,
                         'time': time_now,
                         'status': 7,
                         'length': vars.counter_1
                         })
        dc.db_put_state(vars.db_quie,
                        {'id': vars.counter_2_id,
                         'project_id': vars.project_id,
                         'time': time_now,
                         'status': 7,
                         'length': vars.counter_2
                         })
        dc.db_put_state(vars.db_quie,
                        {'id': vars.channel_id,
                            'project_id': vars.project_id,
                            'time': vars.saved_time.strftime("%Y-%m-%d %H:%M:%S"),
                            'status': vars.saved_status,
                            'length': int(round((time_now-vars.saved_time).total_seconds()))                # 02/08 (was buffer_time)
                            })
        # if vars.buffered:                                                                                 # 02/08
        #     dc.db_put_state(vars.db_quie,
        #                     {'id': vars.channel_id,
        #                         'project_id': vars.project_id,
        #                         'time': vars.saved_time.strftime("%Y-%m-%d %H:%M:%S"),
        #                         'status': vars.saved_status,
        #                         'length': int(round(vars.saved_length))
        #                         })
    
    if vars.counters_reset is False and vars.counters_reset_in is False:    # если был сигнал отмены сброс_счетчика 
                                                                            # и он считан с источника, 
                                                                            # выставляем его None чтобы не писался в регистр полстоянно
            vars.counters_reset = None
    
    if vars.counters_reset is True and vars.counter_2 == 0:                # если был сигнал отмены сброс_счетчика 
                                                                            # и счетчик рулонов = 0, , сбрасываем его
            vars.counters_reset = False
    
    # if vars.counters_reset == True and vars.counters_reset_in == True:   # если был сигнал сброс_счетчика и он считан с источника, сбрасываем его
    #         vars.counters_reset = False
    
    if vars.write_counters:                     #           Запись счетчика
        logger.log('PROG','write_counters')
        vars.write_counters = False
        dc.db_put_state(vars.db_quie,
                        {'id': vars.counter_1_id,
                         'project_id': vars.project_id,
                         'time': time_now,
                         'status': 7,
                         'length': vars.counter_1
                         })
        # TODO здесь пишем  со статусом 7, length - счетчик, time_now
        vars.counters_reset = True  # сбрасываем счетчик в контроллере
        dc.db_put_state(vars.db_quie,
                        {'id': vars.counter_2_id,
                         'project_id': vars.project_id,
                         'time': time_now,
                         'status': 7,
                         'length': vars.counter_2
                         })
        # TODO здесь пишем  со статусом 7, length - счетчик, time_now
        vars.counter_2_reset = True  # сбрасываем счетчик в контроллере
        return

    

    #           если нет источника или входящий результат пустой массив
    if vars.result_in is None:
        result_in_error = True

    #          вычисление достоверности ждем таймаут, потом выставляется NA_status
    if vars.dost is False or result_in_error:
        vars.not_dost_counter += 1
        if vars.not_dost_counter > vars.dost_timeout:
            NA_status = True
            vars.not_dost_counter = vars.dost_timeout+1
        else:
            return  # выходим если ждем таймаут
    else:
        vars.not_dost_counter = 0
        NA_status = False
    
    if vars.NA_status_before != NA_status:
        logger.log('PROG', f'смена достоверности {NA_status=}')
        dost_change_flag = True
        vars.NA_status_before = NA_status  # запоминаем NA_status
    else:
        dost_change_flag = False

    #           определяем текущий статус
    if not result_in_error:
        status = (not NA_status) * vars.result_in
    else:
        status = 0
    vars.status = status

    #         первоначальная инициализация
    if vars.init:
        logger.log('PROG', 'vars init')
        vars.init = False
        if result_in_error and not NA_status:
            vars.saved_status = 0
        else:
            vars.saved_status = status
        vars.currentStateTime = time_now
        vars.saved_time = time_now
        vars.saved_length = 0
        vars.buffer_status = status
        vars.buffer_time = time_now
        vars.buffered = False
        vars.write_buffer = False
        vars.was_write_init = False
        vars.status_ch_b1, vars.status_ch_b2 = tuple(
            1 if b == '1' else 0 for b in reversed(bin(status)[2:].zfill(2)))

    if status != vars.buffer_status or vars.write_init or dost_change_flag:
        # если меняется интервал или принудительная инициализации записи или недостоверность источника
        logger.log('PROG', 'меняется интервал или принудительная инициализации записи или недостоверность источника')
        logger.log('PROG', f'{status=}, {vars.buffer_status=}, {vars.write_init=}, {dost_change_flag=}')
        logger.log('PROG', 'на входе в условие ')
        logger.log('PROG', f'saved_status:{vars.saved_status} saved_time:{vars.saved_time.strftime("%Y-%m-%d %H:%M:%S")} saved_length:{vars.saved_length}')
        logger.log('PROG', f'buffer_status:{vars.buffer_status} buffer_time:{vars.buffer_time.strftime("%Y-%m-%d %H:%M:%S")} ')
        logger.log('PROG', f'{vars.buffered=} {db_write_flag=} {vars.was_write_init=}')
        # выставляем биты состояния статуса для доступа по модбас для внешних клиентов (совместимость с UTrack SCADA)
        vars.status_ch_b1, vars.status_ch_b2 = tuple(
            1 if b == '1' else 0 for b in reversed(bin(status)[2:].zfill(2)))
        print(f'{vars.channel_id}:{status=}, {vars.status_ch_b1=}, {vars.status_ch_b2=}')

        if vars.write_init or NA_status or vars.write_buffer:
            # сюда попали тк форсированная запись или статус NA или доп запись буфера 
            logger.log('PROG','если сюда попали тк форсированная запись или статус NA')
            logger.log('PROG',f'{vars.write_init=} {NA_status=} {vars.write_buffer=}')
            vars.write_init = False
            vars.was_write_init = True
            db_write_flag = True
            if vars.buffered:               # если есть подвешенный отрезок
                logger.log('PROG',f'есть подвешенный отрезок')
                vars.write_buffer = True
                vars.buffered = False
            else:                            # если нет подвешенного отрезка / попадаем сюда если write_buffer  
                if vars.write_buffer:                # если дополнительтно записываем буферный отрезок              27/07
                    logger.log('PROG',f'пишем буфер')
                    vars.write_buffer = False
                    vars.saved_status = vars.buffer_status
                    vars.saved_time = vars.buffer_time
                    vars.saved_length = (time_now-vars.buffer_time).total_seconds()
                else:                                   # если нет буф отрезка пишем начало сохраненного отрезка    27/07
                    logger.log('PROG',f'нет подвешенного отрезка ')
                    vars.saved_length = (time_now-vars.saved_time).total_seconds()
                vars.buffer_status = status
                vars.buffer_time = time_now
                    
        else:   # Если смена статуса
            logger.log('PROG',f'смена статуса {status=} {vars.buffer_status=}')
            if (time_now - vars.buffer_time).total_seconds() <= vars.tech_timeout:
                # Если техпростой еще не закончился но сменился статус
                logger.log('PROG','техпростой еще не закончился но сменился статус')
                if status == 3:  # если Работа
                    if vars.saved_status == 3:
                        logger.log('PROG','status == 3 saved_status == 3')
                        vars.saved_length = vars.saved_length + (time_now-vars.buffer_time).total_seconds()
                        vars.buffered = False
                    else:
                        logger.log('PROG','status = 3 saved_status != 3')
                        vars.saved_length = (
                            time_now-vars.buffer_time).total_seconds()
                        vars.saved_status = vars.buffer_status
                        vars.saved_time = vars.buffer_time
                        db_write_flag = True
                        vars.buffered = False
                    vars.buffer_status = status
                    vars.buffer_time = time_now
                else:   # Если не Работа
                    logger.log('PROG','status != 3')
                    if vars.buffer_status == 3:  # в буффере отрезок Работа
                        logger.log('PROG','в буффере отрезок Работа')
                        if vars.saved_status == 3:  # предыдущий отрезок был Работа
                            logger.log('PROG','предыдущий отрезок был Работа')
                            vars.saved_length = vars.saved_length + \
                                (time_now-vars.buffer_time).total_seconds()
                            vars.buffer_status = status
                            vars.buffer_time = time_now
                            vars.buffered = True
                        else:                # предыдущий отрезок был НЕ Работа
                            logger.log('PROG','предыдущий отрезок был НЕ Работа')
                            vars.saved_length = (
                                time_now-vars.buffer_time).total_seconds()
                            vars.saved_status = vars.buffer_status
                            vars.saved_time = vars.buffer_time
                            vars.buffer_status = status
                            vars.buffer_time = time_now
                            vars.buffered = True
                    else:                           # в буффере отрезок НЕ Работа
                        logger.log('PROG','в буффере отрезок НЕ Работа')
                        vars.buffer_status = status
                        # buffer_time=time_now; прибавляем время отрезка "неработа" время если меньше таймаута
                        vars.buffered = True
            else:   # техпростой закончился и сменился статус
                logger.log('PROG','техпростой закончился и сменился статус')
                if vars.saved_status == 3 and vars.buffer_status == 3:				# ------_----
                    logger.log('PROG','перерыв в работе: vars.saved_status == 3 and vars.buffer_status == 3   ----_----')
                    vars.saved_status = vars.buffer_status
                    vars.saved_length = vars.saved_length + \
                        (time_now-vars.buffer_time).total_seconds()
                    if vars.was_write_init:  # если предыдущий раз писали по сигналу write_init обновляем saved_time
                        vars.saved_time = vars.buffer_time
                        logger.log('PROG', f'предыдущий раз писали по сигналу write_init обновляем saved_time {vars.saved_time=}')
                    vars.buffered = True
                else:
                    logger.log('PROG','не перерыв в работе')
                    vars.saved_status = vars.buffer_status
                    vars.saved_time = vars.buffer_time
                    vars.saved_length = (
                        time_now-vars.buffer_time).total_seconds()
                    if vars.buffer_status == 3:
                        vars.buffered = True
                    else:
                        vars.buffered = False
                        db_write_flag = True
                vars.buffer_status = status
                vars.buffer_time = time_now
                vars.was_write_init = False
        logger.log('PROG','на выходе из условий ')
        logger.log('PROG',f'saved_status:{vars.saved_status} saved_time:{vars.saved_time.strftime("%Y-%m-%d %H:%M:%S")} saved_length:{vars.saved_length}')
        logger.log('PROG',f'buffer_status:{vars.buffer_status} buffer_time:{vars.buffer_time.strftime("%Y-%m-%d %H:%M:%S")} ')
        logger.log('PROG',f'{vars.buffered=} {db_write_flag=} {vars.was_write_init=}')

    if vars.buffered:
        # если есть отрезок ожидающий записи - пишем его по прошествии tech_timeout
        if (time_now-vars.buffer_time).total_seconds() >= vars.tech_timeout:
            logger.log('PROG',f'buffered + tech_timeout -> db_write_flag = True' )
            db_write_flag = True
            vars.buffered = False

    if db_write_flag:
        logger.log('PROG',f'db_write: ch:{vars.channel_id} t={vars.saved_time.strftime("%Y-%m-%d %H:%M:%S")} s:{vars.saved_status} l:{int(round(vars.saved_length))}' )
        db_write_flag = False
        vars.write_init = False  # сбрасываем флаг инициализации записи если был 1
        if vars.saved_length > settings.MIN_STORED_STATE_LENGTH:
            dc.db_put_state(vars.db_quie,
                            {'id': vars.channel_id,
                             'project_id': vars.project_id,
                             'time': vars.saved_time.strftime("%Y-%m-%d %H:%M:%S"),
                             'status': vars.saved_status,
                             'length': int(round(vars.saved_length))
                             })
        vars.saved_length = 0                                                       # 02/08
        