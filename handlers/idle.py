from datetime import datetime

import logics
import settings

def idle(vars):
    '''
        idle serving programm (обработка простоев)
        vars:
            state - current state
            machine_id - id станка
            cause_id - id причины
            techidle_lenhth - длительность техпростоя
            reset_idle_flag - принудительный сброс текущего простоя без записи
            set_cause_flag - флаг указания причины оператором
            restore_idle_flag - текущая причина записывается с временной меткой и создается такаяже длящаяся далее
            operator_id - текущий оператор

    '''
    idle=logics.current_idle_get(vars.machine_id)
    
    if vars.set_cause_flag:
        print(f'set cause flag to {vars.machine_id} to {vars.cause_id}')
        vars.set_cause_flag=False
        logics.current_idle_add_cause(vars.machine_id, vars.operator_id, vars.cause_id, datetime.now(), vars.project_id, vars.db_quie)
    
    if vars.restore_idle_flag:      # записываем текущий простой и начинаем новый с текущего времени (например в конце смены)
        vars.restore_idle_flag=False
        logics.current_idle_store(vars.machine_id)
        logics.current_idle_add_cause(vars.machine_id, vars.operator_id, idle.cause_id, datetime.now(), vars.project_id, vars.db_quie)
    
    if vars.reset_idle_flag:        # принудительный сброс текущего простоя без записи
        vars.reset_idle_flag=False
        logics.current_idle_reset(vars.machine_id)

    if vars.state in settings.IDLE_STATES:
        if idle:             # простой уже зафиксирован 
            if idle.cause: # уже есть причина
                if (idle.cause==settings.TECH_IDLE_ID) and ((datetime.now()-idle.cause_time).total_seconds() >= vars.techidle_lenhth): 
                    #если кончился техпростой - записываем, устанавливаем как "нет причины", устанавливаем флаг обновления причины на клиенте
                    print (f'store from backend {(datetime.now()-idle.cause_time).total_seconds() >= vars.techidle_lenhth}')
                    # logics.current_idle_store(vars.machine_id)
                    logics.current_idle_add_cause(vars.machine_id, vars.operator_id, settings.NOT_CHEKED_CAUSE, datetime.now(), vars.project_id, vars.db_quie)
            #else:            # простой зафиксирован и нет причины
            #    # здесь реакция если оператор не успел подтвердить простой за необходимое время
            #    if (datetime.now()-idle.begin_time).total_seconds() >=settings.CAUSE_CHECK_TIMEOUT:
            #        ...      # нe указана причина за отведенное время

        else:                # появился новый простой - авто техпростой
            logics.current_idle_set(vars.machine_id, vars.state, vars.techidle_lenhth, vars.operator_id, settings.TECH_IDLE_ID , datetime.now(), datetime.now())
    else:
        if idle:             # если был простой и переход в работу
            if idle.cause:      # если указана причина
                pass
            else:   #если причина не указана
                logics.current_idle_add_cause(vars.machine_id, vars.operator_id, settings.NOT_CHEKED_CAUSE, datetime.now(), vars.project_id,  vars.db_quie)
            logics.current_idle_store(vars.machine_id, vars.project_id, vars.db_quie)
            logics.current_idle_reset(vars.machine_id)
        else:                 # работа - выход  
            pass
    if idle:
        vars.current_cause=idle.cause
        vars.current_cause_time=idle.cause_time
