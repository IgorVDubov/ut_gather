from datetime import datetime

import dbqueries

def signal_techtimeout(vars):
    '''
    signals values with timeout
    VARS:
        'result_in':'5002.resultIn', -          вход от источника
        'counter':'5003.result',             вход от источника счетчика
        'counter_reset':'5004.result',          вход от источника сброс счетчика
        'write_init':'13001.args.writeInit',    сигнал принудительной записи
        'write_counter':'13001.args.write_counter' сигнал записи счетчика
        'status_ch_b1':'11001.args.b1',         бит1 канала статуса
        'status_ch_b2':'11001.args.b2',         бит2 канала статуса
        'dost_timeout':'1001.args.dost_timeout', таймаут достоверности ,с
        'tech_timeout':'1001.args.minLength',   техпростой ,с
        'status':0,                             текущий статус
        'cuase':'17002.args.cause_id',          текущая причина простоя
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
        'db_write_flag':False,                  флаг принудительной записи в БД
        'dbQuie':'12001',                       связь с очередью записи в БД
        'idle_handler_id':17002,                канал обработчика простоев
    '''
    time_now=datetime.now()
    db_write_flag=False
    dost_change_flag = False
    #           Запись счетчика
    if vars.write_counter:
        vars.write_counter=False
        dbqueries.db_put_state(vars.db_quie,
                                {   'id':vars.channel_id, 
                                    'project_id':vars.project_id, 
                                    'time':time_now,
                                    'status':7,
                                    'length':vars.counter
                                    })
        #TODO здесь пишем  со статусом 7, length - счетчик, time_now         
        vars.counter_reset=True #сбрасываем счетчик в контроллере
        return
    
    #           если нет источника
    if vars.result_in==None:       #########!!!!!!!!!!!!
        vars.result_in=0
    #          вычисление достоверности ждем таймаут, потом выставляется NA_status
    if vars.dost==False:
        vars.not_dost_counter+=1
    else:
        vars.not_dost_counter=0
        NA_status=False
    if vars.not_dost_counter>vars.dost_timeout:
        NA_status=True
        vars.d_length=vars.dost_Timeout+1
    if vars.NA_status_before!=NA_status :
        dost_change_flag = True
    else:
       dost_change_flag = False

    #           определяем текущий статус
    vars.NA_status_before = NA_status   #запоминаем NA_status 
    # result_bits=[1 if b=='1' else 0 for b in reversed(bin(vars.result_in)[2:].zfill(2))]
    if len(vars.result_in):
        signal1=vars.result_in[0]     # TODO вынести наверх тк привязка к конкретным позициям в массиве результата
        signal2=vars.result_in[1]            
    else:
        signal1=0
        signal2=0
    OFF_status = not signal1
    WORK_status = signal2
    status = (not NA_status) * ( OFF_status + (not OFF_status)*(2+WORK_status) )
    vars.status=status

    #         первоначальная инициализация
    if vars.init:
        vars.init=False
        vars.currentStateTime=time_now
        vars.saved_status = status
        vars.saved_time = time_now
        vars.saved_length=0
        vars.buffer_status = status
        vars.buffer_time=time_now
        vars.buffered=False
        vars.double_write=False
        vars.was_write_init=False
        vars.status_bit1, vars.status_bit2 = (1 if b=='1' else 0 for b in reversed(bin(status)[2:].zfill(2)))
        # NA_status=False
        # vars.lengthDB=0
        # vars.timeDB=time_now

    if status != vars.buffer_status or vars.write_init or dost_change_flag:  #если меняется интервал или принудительная инициализации записи
        print(f'{vars.channel_id}:{status=}')
    	#выставляем биты состояния статуса для доступа по модбас для внешних клиентов (совместимость с UTrack SCADA)
        vars.status_bit1, vars.status_bit2 = (1 if b=='1' else 0 for b in reversed(bin(status)[2:].zfill(2)))

        if vars.write_init or NA_status or vars.double_write:	
            #если сюда попали тк форсированная запись или статус NA
            vars.write_init	=False
            vars.was_write_init=True					        
            if vars.buffered:
                double_write=True															
                vars.buffered=False
                db_write_flag=True
            else:
                vars.saved_status=vars.buffer_status
                vars.saved_time=vars.buffer_time
                vars.saved_length=(time_now-vars.buffer_time).total_seconds()
                db_write_flag=True
                double_write=False
                vars.buffer_status=status
                vars.buffer_time=time_now
        else:   # Если смена статуса
            if (time_now - vars.buffer_time).total_seconds() <= vars.tech_timeout:   # Если техпростой еще не закончился но сменился статус
                if  status==3:  # если Работа
                    if vars.saved_status==3:
                        vars.saved_length=vars.saved_length+(time_now-vars.buffer_time).total_seconds()
                        vars.buffered=False
                    else:
                        vars.saved_length=(time_now-vars.buffer_time).total_seconds()
                        vars.saved_status=vars.buffer_status
                        vars.saved_time=vars.buffer_time
                        db_write_flag=True
                        vars.buffered=False
                    vars.buffer_status=status
                    vars.buffer_time=time_now
                else:   # Если не Работа
                    if vars.buffer_status==3: # в буффере отрезок Работа
                        if vars.saved_status==3: # предыдущий отрезок был Работа
                            vars.saved_length=vars.saved_length+(time_now-vars.buffer_time).total_seconds()
                            vars.buffer_status=status
                            vars.buffer_time=time_now
                            vars.buffered=True
                        else:                # предыдущий отрезок был НЕ Работа
                            vars.saved_length=(time_now-vars.buffer_time).total_seconds()
                            vars.saved_status=vars.buffer_status
                            vars.saved_time=vars.buffer_time
                            vars.buffer_status=status
                            vars.buffer_time=time_now
                            vars.buffered=True
                    else:                           # в буффере отрезок НЕ Работа
                        vars.buffer_status=status
                        #buffer_time=time_now; прибавляем время отрезка "неработа" время если меньше таймаута
                        vars.buffered=True
            else:
                if vars.saved_status==3 and vars.buffer_status==3:				# ------_----
                    vars.saved_status=vars.buffer_status
                    vars.saved_length=vars.saved_length + (time_now-vars.buffer_time).total_seconds()
                    if vars.was_write_init :								#если писали по сигналу write_init обновляем saved_time
                        vars.saved_time=vars.buffer_time
                    vars.buffered=True
                else:
                    vars.saved_status=vars.buffer_status
                    vars.saved_time=vars.buffer_time
                    vars.saved_length=(time_now-vars.buffer_time).total_seconds()
                    if vars.buffer_status==3:
                        vars.buffered=True
                    else:
                        vars.buffered=False
                        db_write_flag=True
                vars.buffer_status=status
                vars.buffer_time=time_now
                vars.was_write_init=False



    if vars.buffered : 
        if (time_now-vars.buffer_time).total_seconds()>=vars.tech_timeout :            #если есть отрезок ожидающий записи - пишем его по прошествии min_length
            db_write_flag=True
            vars.buffered=False

    if db_write_flag  :
        db_write_flag=False
        vars.write_init=False                    #сбрасываем флаг инициализации записи если был 1
        if vars.saved_length>10 or vars.saved_length<90000 : 
            dbqueries.insert_state(vars.db_quie,
                                 {  'id':vars.channel_id, 
                                    'project_id':vars.project_id, 
                                    'time':vars.saved_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    'status':vars.saved_status,
                                    'length':int(round(vars.saved_length))
                                    })
            # dbqueries.db_put_state(vars.db_quie,
            #                     {   'id':vars.channel_id, 
            #                         'project_id':vars.project_id, 
            #                         'time':vars.saved_time.strftime("%Y-%m-%d %H:%M:%S"),
            #                         'status':vars.saved_status,
            #                         'length':int(round(vars.saved_length))
            #                         })
            print(f'Put ti dbquire id={vars.channel_id}, time={vars.saved_time.strftime("%Y:%m:%d %H:%M:%S")}, status={vars.saved_status}, length={int(vars.saved_length)}')
            