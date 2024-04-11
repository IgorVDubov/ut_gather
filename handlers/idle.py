from datetime import datetime

import logics
import settings
from loguru import logger


def idle(vars):
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
            'min_state_len': 20,                                  минимальная длительность состояния (в сек)
            'buffer_state': True,                             флаг True если статус еще меньше минималоьного

    '''
    idle = logics.get_current_idle(vars.machine_id)
    
    if (datetime.now() - vars.current_state_time).seconds < vars.min_state_len:
        vars.buffer_state = True
    else:
        vars.buffer_state = False
    
    #   если через АПИ установили причину простоя записываем в текущий простой причину
    if vars.set_cause_flag:
        print(f'set cause flag to {vars.machine_id} to {vars.current_cause}')
        vars.set_cause_flag = False
        logics.current_idle_add_cause(vars.machine_id,
                                      vars.operator_id,
                                      vars.current_cause,
                                      datetime.now(),
                                      vars.project_id,
                                      vars.db_quie)
        return
    
    # записываем текущий простой и начинаем новый с текущего
    # времени (например в конце смены)
    if vars.split_idle_flag:
        vars.split_idle_flag = False
        if idle is not None:
            current_cause = idle.cause
            logics.current_idle_store(vars.machine_id,
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
                                    current_cause,
                                    datetime.now(),
                                    datetime.now())
            # logics.current_idle_add_cause(vars.machine_id,
            #                             vars.operator_id,
            #                             idle.cause,
            #                             datetime.now(),
            #                             vars.project_id,
            #                             vars.db_quie)
        return

    # принудительный сброс текущего простоя без записи
    if vars.reset_idle_flag:
        vars.reset_idle_flag = False
        logics.current_idle_reset(vars.db_quie,
                                  vars.machine_id,
                                  vars.project_id)
        return
    
    # если текущий статус является простем
    if vars.state in settings.IDLE_STATES:
        if idle is not None:             # простой уже зафиксирован
            if idle.cause is not None:  # уже есть причина
                if (idle.cause == settings.TECH_IDLE_ID
                        ) and (idle.calc_length() >= vars.techidle_lenhth):
                    # если был техпростой и он кончился  - записываем,
                    # устанавливаем idle как "нет причины",
                    # устанавливаем флаг обновления причины на клиенте
                    logger.info(
                        f'''auto add NOT_CHEKED_CAUSE {vars.machine_id}''')
                    logics.current_idle_add_cause(vars.machine_id,
                                                  vars.operator_id,
                                                  settings.NOT_CHEKED_CAUSE,
                                                  datetime.now(),
                                                  vars.project_id,
                                                  vars.db_quie)
            # else:            # простой зафиксирован и нет причины
            #    # здесь реакция если оператор не успел подтвердить простой за
            #    # необходимое время
            #    if (datetime.now()-idle.begin_time).total_seconds(
                #   ) >=settings.CAUSE_CHECK_TIMEOUT:
            #        ...      # нe указана причина за отведенное время

        else:  # появился новый простой - формируем авто техпростой
            # if vars.saved_state == 3\
            #     and vars.saved_length > vars.min_state_len:     # только если предыдущее состояние 
                                                                # было работа и она 
                                                                # была дольше минимума
            if not vars.buffer_state:   # когда минимальное время состояния вышло
                                        # записываем техпростой с current_state_time
                logger.info(f'current_idle_set {idle}')
                logics.current_idle_set(
                                    vars.db_quie,
                                    vars.machine_id,
                                    vars.project_id,
                                    vars.state,
                                    vars.techidle_lenhth,
                                    vars.operator_id,
                                    settings.TECH_IDLE_ID,
                                    vars.current_state_time,
                                    vars.current_state_time
                                    # datetime.now(),
                                    # datetime.now()
                )
    else:               # если был простой и переход в работу
        
        if idle:    # если идет простой         
            if idle.cause is not None:      # если указана причина
                pass
            else:  # если причина не указана
                logger.info(f'переход в работу причина не указана current_idle_add_cause {idle}')
                logics.current_idle_add_cause(vars.machine_id,
                                              vars.operator_id,
                                              settings.NOT_CHEKED_CAUSE,
                                              datetime.now(),
                                              vars.project_id,
                                              vars.db_quie
                                              )
            if not vars.buffer_state:
                logger.info(f'переход в работу buffer_state=1 current_idle_store {idle}')
                logics.current_idle_store(
                    vars.machine_id,
                    vars.project_id,
                    vars.min_state_len,
                    vars.db_quie
                    )
                logger.info(f'переход в работу buffer_state=1 current_idle_reset {vars.machine_id}')
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
        
