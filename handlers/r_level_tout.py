from datetime import datetime
from loguru import logger
import dataconnector as dc


def r_level_timeout(vars):
    '''
    result_in level with timeout
    VARS:
        'channel':'4209',
        'write_init':'10001.args.write_init',
        'statusCh':'100.result_in',
        'gr_stand':1,
        'gr_work':8,
        'dost_timeout':5,
        'tech_timeout':20,
    ******************************************************        
    channel - привязка к каналу
    VAR_INPUT value_in :  IN вход канала
            * vars.saved_status : USINT END_VAR # статус отрезка для записи БД
            * vars.saved_length : UDINT END_VAR # длительность отрезка для записи БД
            * vars.saved_time : DATE_AND_TIME END_VAR # начало отрезка для записи БД
            * db_write : BOOL END_VAR # флаг записи в БД -> DB_in
    VAR_OUTPUT status : текущее состояние (для отображения)
    VAR_INPUT dost :  достоверность аргумент от канала к источнику
    VAR_INOUT write_init : BOOL := 1 END_VAR # принудительная инициализация записи
    VAR_OUTPUT status_bit1 : BOOL END_VAR # бит1 статуса для HEX канала состояния
    VAR_OUTPUT status_bit2 : BOOL END_VAR # бит2 статуса для HEX состояния
    gr_stand  граница простоя
    gr_work : REAL END_VAR # граница рботы
    dost_Timeout : USINT := 5 END_VAR # таймаут НЕдостоверности канала
    min_length : USINT := 20 END_VAR # минимальный отрезок времени сменеы статуса (если меньше, статус не меняется)
    VAR time_now : DATE_AND_TIME END_VAR
    '''

    time_now = datetime.now()
    dostChangeFlag = False
    dbWriteFlag = False
    result_in_error = False
    if vars.init:
        vars.init = False
        vars.current_state_time = time_now
        vars.na_status = False
        vars.saved_length = 0
        vars.saved_time = time_now

    if vars.stop_signal and vars.saved_status is not None:
        logger.log(
            'PROG', '!!!!!!!!!!!!!!!!!    get stop signal       !!!!!!!!!!!!!!!!!!!!!!!!!')
        dc.db_put_state(vars.db_quie,
                        {'id': vars.m_id,
                         'project_id': vars.project_id,
                         'time': vars.saved_time.strftime("%Y-%m-%d %H:%M:%S"),
                         'status': vars.saved_status,
                         # 02/08 (was buffer_time)
                         'length': int(round((time_now-vars.saved_time).total_seconds()))
                         })

    #  если нет источника или входящий результат пустой массив
    if vars.result_in is None:
        result_in_error = True

    na_status = False

    if vars.dost == False or result_in_error:
        vars.not_dost_counter += 1
        if vars.not_dost_counter > vars.dost_timeout:
            na_status = True
            vars.not_dost_counter = vars.dost_timeout+1
        else:
            return
    else:
        vars.not_dost_counter = 0

    if vars.na_status_before != na_status:
        dostChangeFlag = True
        vars.na_status_before = na_status
    else:
        dostChangeFlag = False

    # определяем текущий статус
    interval = vars.current_interval
    if not result_in_error:
        vars.v5 = vars.v4
        vars.v4 = vars.v3
        vars.v3 = vars.v2
        vars.v2 = vars.v1
        vars.v1 = vars.result_in
        vars.result = (vars.v1 + vars.v2 + vars.v3 + vars.v4 + vars.v5)/5
        result = vars.result
        if result < vars.gr_stand:  # откл
            status = 1
            interval = 1
        elif result > vars.gr_stand and result < vars.gr_work:  # простой
            status = 2
            interval = 2
        else:                   # работа
            status = 3
            interval = 3
    else:
        status = 0

    # если меняется интервал или принудительная инициализации записи
    if interval != vars.current_interval or vars.write_init or dostChangeFlag:

        if na_status:
            status = 0  # NA
        # выставляем биты состояния статуса для доступа по модбас для внешних клиентов
        # vars.statusCh=status
        if status == 0:
            vars.status_ch_b1 = 0
            vars.status_ch_b2 = 0
        elif status == 1:
            vars.status_ch_b1 = 1
            vars.status_ch_b2 = 0
        elif status == 2:
            vars.status_ch_b1 = 0
            vars.status_ch_b2 = 1
        elif status == 3:
            vars.status_ch_b1 = 1
            vars.status_ch_b2 = 1

        if vars.write_init or na_status:  # если форсированная запись или статус NA
            # задаем отрезок для записи: текущий статус до смены
            vars.saved_status = vars.current_state
            vars.saved_time = vars.current_state_time  # аналогично время
            # и длительность
            vars.saved_length = (
                time_now - vars.current_state_time).total_seconds()
            vars.current_state = status  # задаес текущий отрезок: статус
            vars.current_state_time = time_now  # время
            dbWriteFlag = True
            vars.buffered = False									    		# если отрезок был подвешен - сбрасываем флаг
        else:
            # подвешиваем запись и ждем не изменится ли статус в течении таймаута (min_length): ожидание записи
            vars.buffered = True
            # если статус меняется до таймаута
            if (time_now - vars.current_state_time).total_seconds() <= vars.tech_timeout:
                # state_value не меняется
                # state_time не меняется
                # увеличиваем длину подвешенного отрезка на длину текущего
                vars.saved_length = vars.saved_length + \
                    (time_now - vars.current_state_time).total_seconds()
                if status == vars.saved_status:  # если  текущий статус стал такой же как у подвешеного отрезка
                    vars.current_state = vars.saved_status  # подвешенный отрезок
                    vars.current_state_time = vars.saved_time  # становится текущим
                    vars.buffered = False  # снимаем отрезок с ожидания записи
                else:  # если статус меняется
                    vars.current_state = status  # обновляем статус и
                    vars.current_state_time = time_now  # время текущего отрезка
                    vars.buffered = True  # и подвешиваем- ожидание записи
            else:													                    # если статус меняется после таймаута
                # задаем отрезок для записи (подвешенный): статус
                vars.saved_status = vars.current_state
                vars.saved_time = vars.current_state_time  # время
                # длительность
                vars.saved_length = (
                    time_now - vars.current_state_time).total_seconds()
                vars.current_state = status  # задаем новй текущий отрезок: статус
                vars.current_state_time = time_now  # начала отрезка
            # в любом случае текущий интервал = интервал канала
            vars.current_interval = interval
    if vars.buffered:
        # если есть отрезок ожидающий записи - пишем его по прошествии min_length
        if (time_now-vars.current_state_time).total_seconds() >= vars.tech_timeout:
            dbWriteFlag = True
            vars.buffered = False
    vars.status = vars.current_state
    if dbWriteFlag:
        dbWriteFlag = False
        vars.write_init = False  # сбрасываем флаг инициализации записи если был 1
        if vars.saved_length > 10 or vars.saved_length < 90000:
            if vars.saved_status is not None:
                dc.db_put_state(vars.db_quie,
                                {'id': vars.m_id,
                                    'project_id': vars.project_id,
                                    'time': vars.saved_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    'status': vars.saved_status,
                                    'length': int(round(vars.saved_length))
                                 })
