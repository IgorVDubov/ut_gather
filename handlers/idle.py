from datetime import datetime

import logics
import settings


def idle(vars):
    '''
        idle serving programm (обработка простоев)
        vars:
            'status'                                            текущий статус
            'saved_status': 'канал_станка.args.saved_status',   отрезок предшествующий текущему: статус
            'saved_length': 'канал_станка.args.saved_length',   отрезок предшествующий текущему: длительность
            'machine_id': 'канал_станка.args.m_id'              id станка
            'operator_id': 'канал_станка.args.operator_id',     текущий оператор
            'techidle_lenhth': 'канал_станка.args.tech_timeout' длительность техпростоя
            'cause_id' -                                        id текущей причины
            'reset_idle_flag' -                                 флаг принудительного сброса текущего простоя без записи
            'set_cause_flag' -                                  флаг указания причины оператором
            'split_idle_flag' -                                 текущая причина записывается с 
                                                                временной меткой и создается 
                                                                такая же длящаяся далее
            'db_quie': 'databus.db_interface',                  БД интерфейс
            'project_id': 'канал_станка.args.project_id'        id проекта
            'min_work_len': 20,                                  минимальная длительность работы (в сек)

    '''
    idle = logics.get_current_idle(vars.machine_id)

    if vars.set_cause_flag:
        print(f'set cause flag to {vars.machine_id} to {vars.cause_id}')
        vars.set_cause_flag = False
        logics.current_idle_add_cause(vars.machine_id,
                                      vars.operator_id,
                                      vars.cause_id,
                                      datetime.now(),
                                      vars.project_id,
                                      vars.db_quie)

    # записываем текущий простой и начинаем новый с текущего
    # времени (например в конце смены)
    if vars.split_idle_flag:
        vars.split_idle_flag = False
        if idle is not None:
            logics.current_idle_store(vars.machine_id,
                                    vars.project_id,
                                    vars.db_quie)
            current_cause = idle.cause
            logics.current_idle_reset(vars.db_quie,
                                  vars.machine_id,
                                  vars.project_id)
            
            logics.current_idle_set(vars.db_quie,
                                    vars.machine_id,
                                    vars.project_id,
                                    vars.status,
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
    
    # если текущий статус является простем
    if vars.status in settings.IDLE_STATES:
        if idle:             # простой уже зафиксирован
            if idle.cause:  # уже есть причина
                if (idle.cause == settings.TECH_IDLE_ID
                        ) and (idle.calc_length() >= vars.techidle_lenhth):
                    # если был техпростой и он кончился  - записываем,
                    # устанавливаем idle как "нет причины",
                    # устанавливаем флаг обновления причины на клиенте
                    print(
                        f'''store from backend {idle.calc_length()
                                                >= vars.techidle_lenhth}''')
                    # logics.current_idle_store(vars.machine_id)
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

        else:                # появился новый простой - формируем авто техпростой
            if vars.saved_status == 3\
                and vars.saved__length > vars.min_work_len:     # только если предыдущее состояние 
                                                                # было работа и она 
                                                                # была дольше минимума
                logics.current_idle_set(
                                    vars.db_quie,
                                    vars.machine_id,
                                    vars.project_id,
                                    vars.status,
                                    vars.techidle_lenhth,
                                    vars.operator_id,
                                    settings.TECH_IDLE_ID,
                                    datetime.now(),
                                    datetime.now()
                )
    else:
        if idle:             # если был простой и переход в работу
#TODO добавить проверку на длятельность работы, если короче минимума не сбрасывать причину
            if idle.cause:      # если указана причина
                pass
            else:  # если причина не указана
                logics.current_idle_add_cause(vars.machine_id,
                                              vars.operator_id,
                                              settings.NOT_CHEKED_CAUSE,
                                              datetime.now(),
                                              vars.project_id,
                                              vars.db_quie
                                              )
            logics.current_idle_store(vars.machine_id,
                                      vars.project_id,
                                      vars.db_quie)
            logics.current_idle_reset(vars.db_quie,
                                      vars.machine_id,
                                      vars.project_id
                                      )
        else:                 # работа - выход
            pass
        # при переходе в работу текущая причина None
        if idle:
            idle.cause = None 
            idle.cause_time = None
    
    if idle:
        vars.current_cause = idle.cause
        vars.current_cause_time = idle.cause_time
    else:
        vars.current_cause = None
        vars.current_cause_time = None
        
