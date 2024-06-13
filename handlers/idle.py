from datetime import datetime, timedelta

import logics
import settings
from loguru import logger


def idle(vars):
    # техпростой после останова, если вернулись в работу
    # если другая причина - заменяем техпростой
    '''
        idle serving programm (обработка простоев)
        vars:
            'state'                                            текущий статус
            'saved_state': 'канал_станка.args.saved_state',   отрезок предшествующий текущему: статус
            'saved_length': 'канал_станка.args.saved_length',   отрезок предшествующий текущему: длительность
            'machine_id': 'канал_станка.args.m_id'              id станка
            'operator_id': 'канал_станка.args.operator_id',     текущий оператор
            'techidle_lenhth': 'канал_станка.args.tech_timeout' длительность техпростоя
            'current_cause' -                                        id текущей причины
            'reset_idle_flag' -                                 флаг принудительного сброса текущего простоя без записи
            'set_cause_flag' -                                  флаг указания причины оператором
            'split_idle_flag' -                                 текущая причина записывается с 
                                                                временной меткой и создается 
                                                                такая же длящаяся далее
            'db_quie': 'databus.db_interface',                  БД интерфейс
            'project_id': 'канал_станка.args.project_id'        id проекта
            'min_state_len': 20,                                минимальная длительность состояния (в сек) по которому инициируется простой
            'buffer_state': True,                             флаг True если статус еще меньше минималоьного

    '''
    current_time = datetime.now()
    idle = logics.get_current_idle(vars.machine_id)
    try:
        if (current_time - vars.current_state_time).seconds <= vars.min_state_len:
            vars.buffer_state = True
        else:
            vars.buffer_state = False
    except TypeError:
        vars.buffer_state = False
    
    #   если через АПИ установили причину простоя записываем в текущий простой причину
    if vars.set_cause_flag:
        logger.log('PROG', f'{vars.machine_id} set_cause_flag: cause_id={vars.current_cause}  time={current_time}')
        vars.set_cause_flag = False
        logics.current_idle_add_cause(vars.machine_id,
                                      vars.operator_id,
                                      vars.current_cause,
                                      current_time,
                                      vars.project_id,
                                      vars.db_quie)
        return
    
    # записываем текущий простой и начинаем новый с текущего
    # времени (например в конце смены)
    if vars.split_idle_flag:
        vars.split_idle_flag = False
        if idle is not None:
            current_cause = idle.cause
            logger.log('PROG', f'{vars.machine_id} split_idle_flag to {idle.cause}  {idle.cause_time}')
        
            logics.save_current_idle(vars.machine_id,
                                    vars.project_id,
                                    0,
                                    vars.db_quie)
            logics.current_idle_reset(vars.db_quie,
                                  vars.machine_id,
                                  vars.project_id)
            logics.current_idle_set(vars.db_quie,
                                    vars.machine_id,
                                    vars.project_id,
                                    vars.state,
                                    vars.techidle_lenhth,
                                    vars.operator_id,
                                    current_time,
                                    current_cause,
                                    current_time,
                                    current_time)
            # logics.current_idle_add_cause(vars.machine_id,
            #                             vars.operator_id,
            #                             idle.cause,
            #                             current_time,
            #                             vars.project_id,
            #                             vars.db_quie)
        return

    # принудительный сброс текущего простоя без записи
    if vars.reset_idle_flag:
        vars.reset_idle_flag = False
        logger.log('PROG', 
                   f'{vars.machine_id} takes current_idle_reset signal Idle:{idle}')
        logics.current_idle_reset(vars.db_quie,
                                  vars.machine_id,
                                  vars.project_id)
        return
    
    # если текущий статус является простоем
    if vars.state in settings.IDLE_STATES:
        if idle is not None:             # простой уже зафиксирован
            if idle.cause is not None:  # уже есть причина
                if (idle.cause == settings.TECH_IDLE_ID
                        ) and (idle.calc_length() >= vars.techidle_lenhth):
                    # если был техпростой и он кончился  - записываем,
                    # устанавливаем idle как "нет причины",
                    # устанавливаем флаг обновления причины на клиенте
                    logger.log('PROG',
                        f'''{vars.machine_id} auto add NOT_CHEKED_CAUSE ''')
                    logics.current_idle_add_cause(vars.machine_id,
                                                  vars.operator_id,
                                                  settings.NOT_CHEKED_CAUSE,
                                                  current_time,
                                                  vars.project_id,
                                                  vars.db_quie)
            # else:            # простой зафиксирован и нет причины
            #    # здесь реакция если оператор не успел подтвердить простой за
            #    # необходимое время
            #    if (current_time-idle.begin_time).total_seconds(
                #   ) >=settings.CAUSE_CHECK_TIMEOUT:
            #        ...      # нe указана причина за отведенное время

        else:  # появился новый простой - формируем авто техпростой
            # if vars.saved_state == 3\
            #     and vars.saved_length > vars.min_state_len:     # только если предыдущее состояние 
                                                                # было работа и она 
                                                                # была дольше минимума
            if not vars.buffer_state:   # когда минимальное время состояния вышло
                                        # записываем техпростой вычитая min_state_len из тек времени
                logger.log('PROG', f'{vars.machine_id} buffer_state off, current_idle_set new Idle with TECH_IDLE cause curr time {current_time.strftime("%H:%M:%S")} dt={vars.min_state_len} begin {(current_time-timedelta(seconds=vars.min_state_len)).strftime("%H:%M:%S")}')
                logics.current_idle_set(
                                    vars.db_quie,
                                    vars.machine_id,
                                    vars.project_id,
                                    vars.state,
                                    vars.techidle_lenhth,
                                    vars.operator_id,
                                    current_time-timedelta(seconds=vars.min_state_len),
                                    settings.TECH_IDLE_ID,
                                    current_time-timedelta(seconds=vars.min_state_len),
                                    current_time-timedelta(seconds=vars.min_state_len),
                                    # vars.current_state_time,
                                    # vars.current_state_time
                )
    else:               # если был простой и переход в работу
        
        if idle:    # если простой был сохранен
            if idle.cause is not None:      # если указана причина
                pass
            else:  # если причина не указана
                logger.log('PROG', 
                           f'{vars.machine_id} переход в работу причина не указана current_idle_add_cause {idle}')
                logics.current_idle_add_cause(vars.machine_id,
                                              vars.operator_id,
                                              settings.NOT_CHEKED_CAUSE,
                                              current_time,
                                              vars.project_id,
                                              vars.db_quie
                                              )
            if not vars.buffer_state:
                logger.log('PROG', f'{vars.machine_id} переход в работу, отрезок > {vars.min_state_len} save_current_idle {idle}, current_idle_reset')
                logics.save_current_idle(
                    vars.machine_id,
                    vars.project_id,
                    # 0,
                    vars.min_state_len,
                    vars.db_quie
                    )
                logics.current_idle_reset(vars.db_quie,
                                        vars.machine_id,
                                        vars.project_id
                                        )
        else:                 # работа - выход
            pass
        # при переходе в работу текущая причина None
        if idle and not vars.buffer_state:
            idle.cause = None 
            idle.cause_time = None
    
    if idle:
        vars.current_cause = idle.cause
        vars.current_cause_time = idle.cause_time
    else:
        vars.current_cause = None
        vars.current_cause_time = None
