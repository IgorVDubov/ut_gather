from datetime import datetime
from loguru import logger
import dataconnector as dc


def r_level_timeout(vars):
    '''
    обработка аналогового сигнала источника
    по бегущему среднему
    с техпроcтоем
    -------------------
    args:
    'm_id'                                                          id станка
    'result_in':'канал_станка.resultIn',                            вход от источника
    'result': 'канал_станка.result',                                значение канала (бегущее среднее)
    'dost':'канал_станка.dost'                                      достоверность канала к источнику
    'gr_stand':1                                                    граница откл/простой
    'gr_work':8                                                     граница простой/работа
    'dost_timeout':'канал_настроек.args.dost_timeout' или int(cек)  таймаут недостоверности ,с
    'tech_timeout':'канал_настроек.args.minLength' или int(cек)     техпростой ,с
    'work_timeout':'канал_настроек.args.min_work_length' или int(cек) минимальный регистрируемый отрезок работы ,с
    'write_init':'db_writer2.args.writeInit',                       сигнал принудительной записи
    'state_ch_b1':'канал_статуса.args.b1',                         бит1 канала статуса
    'state_ch_b2':'канал_статуса.args.b2',                         бит2 канала статуса
    'state':0,                                                     текущий статус
    'saved_state':0,                                               сохраненный предыдущий отрезок статус
    'saved_length':0,                                              сохраненный предыдущий отрезок длительность
    'saved_time':0,                                                сохраненный предыдущий отрезок начало
    'current_state': 0,                                            текущий отрезок: статус
    'current_state_time': 0,                                       текущий отрезок: время смены статуса
    'current_interval': 0,                                         текущий интервал границ (откл-простой-работа)
    'buffered':False,                                              флаг наличия буферезированный отрезок
    'state_db': 0,
    'lengthDB': 0,
    'time_db': 0,
    'init':True,                                                    флаг инициализации (выполняется только при первом запуске)
    'dbQuie':'databus.db_interface',                                связь с очередью записи в БД через объект БД databus-а
    'idle_handler_name':отбработчик_простоя,                        канал обработчика простоев
    'project_id': 5,                                                id проекта к которому относится станок
    'operator_id': None,                                            текущий оператор
    'cause_id': 'отбработчик_простоя.args.current_cause',           текущая причина id
    'cause_time': 'отбработчик_простоя.args.current_cause_time',    текущая причина время начала
    'split_idle': 'отбработчик_простоя.args.split_idle_flag',       флаг разделения отрезка простоя (при переходе смены)
    'stop_signal': False,                                           сигнал сотановки от ядра для записи текущих отрезков
    'v1': 0,    переменная текущего среднего
    'v2': 0,    переменная текущего среднего
    'v3': 0,    переменная текущего среднего
    'v4': 0,    переменная текущего среднего
    'v5': 0,    переменная текущего среднего
    
    '''

    time_now = datetime.now()
    dostChangeFlag = False
    dbWriteFlag = False
    result_in_error = False
    if vars.init:
        vars.init = False
        vars.current_state_time = time_now
        vars.na_state = False
        vars.saved_length = 0
        vars.saved_time = time_now

    if vars.stop_signal and vars.saved_state is not None:
        logger.log(
            'PROG', f' {vars.m_id}  !!    get stop signal       !!')
        dc.db_put_state(vars.db_quie,
                        {'id': vars.m_id,
                         'project_id': vars.project_id,
                         'time': vars.current_state_time.strftime("%Y-%m-%d %H:%M:%S"),
                         'state': vars.current_state,
                         # 02/08 (was buffer_time)
                         'length': int(round((time_now-vars.current_state_time).total_seconds()))
                         })

    #  если нет источника или входящий результат пустой массив
    if vars.result_in is None:
        result_in_error = True

    na_state = False

    if vars.dost == False or result_in_error:
        vars.not_dost_counter += 1
        if vars.not_dost_counter > vars.dost_timeout:
            na_state = True
            vars.not_dost_counter = vars.dost_timeout+1
        else:
            return
    else:
        vars.not_dost_counter = 0

    if vars.na_state_before != na_state:
        dostChangeFlag = True
        vars.na_state_before = na_state
    else:
        dostChangeFlag = False

    # определяем текущий статус
    interval = vars.current_interval
    if not result_in_error:
        vars.v10 = vars.v9
        vars.v9 = vars.v8
        vars.v8 = vars.v7
        vars.v7 = vars.v6
        vars.v6 = vars.v5
        vars.v5 = vars.v4
        vars.v4 = vars.v3
        vars.v3 = vars.v2
        vars.v2 = vars.v1
        vars.v1 = vars.result_in
        vars.result = (vars.v1 + vars.v2 + vars.v3 + vars.v4 + vars.v5 + vars.v6 + vars.v7 + vars.v8 + vars.v9 + vars.v10)/10
# !!!! ------------- dev-------------------        
        vars.result = vars.result_in
# !!!! ------------- dev-------------------        
        result = vars.result
        if result < vars.gr_stand:  # откл
            state = 1
            interval = 1
        elif result > vars.gr_stand and result < vars.gr_work:  # простой
            state = 2
            interval = 2
        else:                   # работа
            state = 3
            interval = 3
    else:
        state = 0

    # если меняется интервал или принудительная инициализации записи
    if interval != vars.current_interval or vars.write_init or dostChangeFlag:

        if na_state:
            state = 0  # NA
        # выставляем биты состояния статуса для доступа по модбас для внешних клиентов
        # vars.stateCh=state
        if state == 0:
            vars.state_ch_b1 = 0
            vars.state_ch_b2 = 0
        elif state == 1:
            vars.state_ch_b1 = 1
            vars.state_ch_b2 = 0
        elif state == 2:
            vars.state_ch_b1 = 0
            vars.state_ch_b2 = 1
        elif state == 3:
            vars.state_ch_b1 = 1
            vars.state_ch_b2 = 1

        if vars.write_init or na_state:  # если форсированная запись или статус NA
            # задаем отрезок для записи: текущий статус до смены
            vars.saved_state = vars.current_state
            vars.saved_time = vars.current_state_time  # аналогично время
            # и длительность
            vars.saved_length = (
                time_now - vars.current_state_time).total_seconds()
            vars.current_state = state  # задает текущий отрезок: статус
            vars.current_state_time = time_now  # задает текущий отрезок: время
            vars.split_idle = True # сигнал разделить текущий простой
            dbWriteFlag = True
            vars.buffered = False									    		# если отрезок был подвешен - сбрасываем флаг
        else:
            # подвешиваем запись и ждем не изменится ли статус в течении таймаута (min_length): ожидание записи
            vars.buffered = True
            # если статус меняется до таймаута
            if state == 3:
                section_timeout = vars.work_timeout
            else:
                section_timeout = vars.tech_timeout
            if (time_now - vars.current_state_time).total_seconds() <= section_timeout:
                # state_value не меняется
                # state_time не меняется
                # увеличиваем длину подвешенного отрезка на длину текущего
                vars.saved_length = vars.saved_length + \
                    (time_now - vars.current_state_time).total_seconds()
                if state == vars.saved_state:  # если  текущий статус стал такой же как у подвешеного отрезка
                    vars.current_state = vars.saved_state  # подвешенный отрезок
                    vars.current_state_time = vars.saved_time  # становится текущим
                    vars.buffered = False  # снимаем отрезок с ожидания записи
                else:  # если статус меняется
                    vars.current_state = state  # обновляем статус и
                    vars.current_state_time = time_now  # время текущего отрезка
                    vars.buffered = True  # и подвешиваем- ожидание записи
            else:													                    # если статус меняется после таймаута
                # задаем отрезок для записи (подвешенный): статус
                vars.saved_state = vars.current_state
                vars.saved_time = vars.current_state_time  # время
                # длительность
                vars.saved_length = (
                    time_now - vars.current_state_time).total_seconds()
                vars.current_state = state  # задаем новй текущий отрезок: статус
                vars.current_state_time = time_now  # начала отрезка
            # в любом случае текущий интервал = интервал канала
            vars.current_interval = interval
    if vars.buffered:
        # если есть отрезок ожидающий записи - пишем его по прошествии min_length
        if state == 3:
            section_timeout = vars.work_timeout
        else:
            section_timeout = vars.tech_timeout
        if (time_now-vars.current_state_time).total_seconds() >= section_timeout:
            dbWriteFlag = True
            vars.buffered = False
    vars.state = vars.current_state
    if dbWriteFlag:
        dbWriteFlag = False
        vars.write_init = False  # сбрасываем флаг инициализации записи если был 1
        if vars.saved_length > 10 or vars.saved_length < 90000:
            if vars.saved_state is not None:
                dc.db_put_state(vars.db_quie,
                                {'id': vars.m_id,
                                    'project_id': vars.project_id,
                                    'time': vars.saved_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    'state': vars.saved_state,
                                    'length': int(round(vars.saved_length))
                                 })

def db_logger(vars):
    sql = 'insert into db_logger values (%s, %s, %s, %s, %s)'
    params = (
        vars.mch_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        vars.result_in,
        vars.result,
        vars.current_state
    )
    dc.insert_sql(vars.db_quie, sql, params)