from datetime import datetime

import dataconnector as dc
import settings


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
        'saved_status':0,                       сохраненный (подвешенный) отрезок статус
        'saved_length':0,                       сохраненный (подвешенный) отрезок
        'saved_time':0,                         сохраненный (подвешенный) отрезок
        'double_write':False,                   флаг для исключения повторной записи
        'buffered':False,                       флаг наличия буферезированный отрезок
        'buffer_time':0,                        буферезированный отрезок
        'buffer_status':0,                      буферезированный отрезок
        'dost_length':0,                        буферезированный отрезок
        'NA_status_before':False,               сохраненный предыдущий статус NA
        'was_write_init':False,                 флаг произошедшей принудительной записи в БД
        'dbQuie':'12001',                       связь с очередью записи в БД
        'cuase':'17002.args.cause_id',          текущая причина простоя
        'cause_time': '17003.args.current_cause_time', текущее время начала простоя
        'idle_handler_id':17002,                канал обработчика простоев
        'project_id': 3,                        id проекта к которому относится канал
        'operator_id': None,                    текущий оператор
    '''
    time_now = datetime.now()
    db_write_flag = False
    dost_change_flag = False
    NA_status = False
    result_in_error = False
    
    if vars.counters_reset == False and vars.counters_reset_in == False:    # если был сигнал отмены сброс_счетчика 
                                                                            # и он считан с источника, 
                                                                            # выставляем его None чтобы не писался в регистр полстоянно
            vars.counters_reset = None
    
    if vars.counters_reset == True and vars.counter_2 == 0:                # если был сигнал отмены сброс_счетчика 
                                                                            # и счетчик рулонов = 0, , сбрасываем его
            vars.counters_reset = False
    
    # if vars.counters_reset == True and vars.counters_reset_in == True:   # если был сигнал сброс_счетчика и он считан с источника, сбрасываем его
    #         vars.counters_reset = False
    
    if vars.write_counters:                     #           Запись счетчика
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
        vars.double_write = False
        vars.was_write_init = False
        vars.status_ch_b1, vars.status_ch_b2 = tuple(
            1 if b == '1' else 0 for b in reversed(bin(status)[2:].zfill(2)))

    # если меняется интервал или принудительная инициализации записи или недостоверность источника
    if status != vars.buffer_status or vars.write_init or dost_change_flag:
        # выставляем биты состояния статуса для доступа по модбас для внешних клиентов (совместимость с UTrack SCADA)
        vars.status_ch_b1, vars.status_ch_b2 = tuple(
            1 if b == '1' else 0 for b in reversed(bin(status)[2:].zfill(2)))
        print(f'{vars.channel_id}:{status=}, {vars.status_ch_b1=}, {vars.status_ch_b2=}')

        if vars.write_init or NA_status or vars.double_write:
            # если сюда попали тк форсированная запись или статус NA
            vars.write_init = False
            vars.was_write_init = True
            if vars.buffered:               # если есть подвешенный отрезок
                vars.double_write = True
                vars.buffered = False
                db_write_flag = True
            else:                            # если нет подвешенного отрезка
                vars.saved_status = vars.buffer_status
                vars.saved_time = vars.buffer_time
                vars.saved_length = (time_now-vars.buffer_time).total_seconds()
                db_write_flag = True
                vars.double_write = False
                vars.buffer_status = status
                vars.buffer_time = time_now
        else:   # Если смена статуса
            # Если техпростой еще не закончился но сменился статус
            if (time_now - vars.buffer_time).total_seconds() <= vars.tech_timeout:
                if status == 3:  # если Работа
                    if vars.saved_status == 3:
                        vars.saved_length = vars.saved_length + \
                            (time_now-vars.buffer_time).total_seconds()
                        vars.buffered = False
                    else:
                        vars.saved_length = (
                            time_now-vars.buffer_time).total_seconds()
                        vars.saved_status = vars.buffer_status
                        vars.saved_time = vars.buffer_time
                        db_write_flag = True
                        vars.buffered = False
                    vars.buffer_status = status
                    vars.buffer_time = time_now
                else:   # Если не Работа
                    if vars.buffer_status == 3:  # в буффере отрезок Работа
                        if vars.saved_status == 3:  # предыдущий отрезок был Работа
                            vars.saved_length = vars.saved_length + \
                                (time_now-vars.buffer_time).total_seconds()
                            vars.buffer_status = status
                            vars.buffer_time = time_now
                            vars.buffered = True
                        else:                # предыдущий отрезок был НЕ Работа
                            vars.saved_length = (
                                time_now-vars.buffer_time).total_seconds()
                            vars.saved_status = vars.buffer_status
                            vars.saved_time = vars.buffer_time
                            vars.buffer_status = status
                            vars.buffer_time = time_now
                            vars.buffered = True
                    else:                           # в буффере отрезок НЕ Работа
                        vars.buffer_status = status
                        # buffer_time=time_now; прибавляем время отрезка "неработа" время если меньше таймаута
                        vars.buffered = True
            else:
                if vars.saved_status == 3 and vars.buffer_status == 3:				# ------_----
                    vars.saved_status = vars.buffer_status
                    vars.saved_length = vars.saved_length + \
                        (time_now-vars.buffer_time).total_seconds()
                    if vars.was_write_init:  # если писали по сигналу write_init обновляем saved_time
                        vars.saved_time = vars.buffer_time
                    vars.buffered = True
                else:
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

    if vars.buffered:
        # если есть отрезок ожидающий записи - пишем его по прошествии min_length
        if (time_now-vars.buffer_time).total_seconds() >= vars.tech_timeout:
            db_write_flag = True
            vars.buffered = False

    if db_write_flag:
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
