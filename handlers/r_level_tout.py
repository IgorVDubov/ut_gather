from datetime import datetime

import logics

def r_level_timeout(vars):
    '''
    result_in level with timeout
    VARS:
        'channel':'4209',
        'dbChannel':None,
        'writeInit':'10001.args.writeInit',
        'statusCh':'100.result_in',
        'grStand':1,
        'grWork':8,
        'dostTimeout':5,
        'minLength':20,
    ******************************************************        
    channel - привязка к каналу
    VAR_INPUT value_in :  IN вход канала
                * vars.statusDB : USINT END_VAR # статус отрезка для записи БД
                * vars.lengthDB : UDINT END_VAR # длительность отрезка для записи БД
                * vars.timeDB : DATE_AND_TIME END_VAR # начало отрезка для записи БД
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
	VAR timeNow : DATE_AND_TIME END_VAR
    '''
    timeNow=datetime.now()
    dostChangeFlag = False
    dbWriteFlag = False
    if vars.init:
        vars.init=False
        vars.currentStateTime=timeNow
        vars.NAStatus=False
        vars.lengthDB=0
        vars.timeDB=timeNow

    if vars.channel.result_in==None:       #########!!!!!!!!!!!!
        vars.channel.result_in=0
    # print (vars.channel.result_in)
    if vars.channel.dost==False:
        vars.notDost+=1
    else:
        vars.notDost=0
        NA_status=False
    if vars.notDost>vars.dostTimeout:
        NA_status=True
        vars.d_length=vars.dost_Timeout+1
    if vars.NAStatusBefore!=vars.NAStatus :
        dostChangeFlag = True
    else:
       dostChangeFlag = False

    vars.NAStatusBefore = vars.NAStatus
    # определяем текущий статус
    if vars.channel.result_in < vars.grStand:  #откл
        status=1
        interval=1
    elif vars.channel.result_in > vars.grStand and vars.channel.result_in<vars.grWork:    #простой
        status=2
        interval=2
    elif vars.channel.result_in > vars.grWork: #работа
        status=3
        interval=3


    if interval != vars.currentInterval or vars.writeInit or dostChangeFlag:  #если меняется интервал или принудительная инициализации записи
	
        if vars.NAStatus:
            status = 0 #NA
        # print(f'{vars.channel.id}:{status=}')
    	#выставляем биты состояния статуса для доступа по модбас для внешних клиентов
        #vars.statusCh=status
        if status==0: 
            vars.statusCh_b1=0 
            vars.statusCh_b2=0
        elif status==1: 
            vars.statusCh_b1=1 
            vars.statusCh_b2=0
        elif status==2: 
            vars.statusCh_b1=0 
            vars.statusCh_b2=1
        elif status==3: 
            vars.statusCh_b1=1 
            vars.statusCh_b2=1

        if vars.writeInit or NA_status :							        #если форсированная запись или статус NA
            vars.statusDB=vars.currentState								    #задаем отрезок для записи: текущий статус до смены
            vars.timeDB=vars.currentStateTime							    #аналогично время
            vars.lengthDB=(timeNow - vars.currentStateTime).total_seconds()	#и длительность
            vars.currentState= status						        		#задаес текущий отрезок: статус
            vars.currentStateTime = timeNow                                  #время
            dbWriteFlag=True							
            vars.buffered=False									    		# если отрезок был подвешен - сбрасываем флаг
        else:
            vars.buffered=True	#подвешиваем запись и ждем не изменится ли статус в течении таймаута (min_length): ожидание записи 
            if (timeNow - vars.currentStateTime).total_seconds() <= vars.minLength : 		# если статус меняется до таймаута
                #state_value не меняется
                #state_time не меняется
                vars.lengthDB=vars.lengthDB+(timeNow - vars.currentStateTime).total_seconds()           #увеличиваем длину подвешенного отрезка на длину текущего
                if status==vars.statusDB :							                    #если  текущий статус стал такой же как у подвешеного отрезка		
                    vars.currentState=vars.statusDB						                #подвешенный отрезок 
                    vars.currentStateTime=vars.timeDB						            #становится текущим
                    vars.buffered=False									                #снимаем отрезок с ожидания записи
                else:												                    #если статус меняется			
                    vars.currentState = status							                #обновляем статус и
                    vars.currentStateTime = timeNow 					                #время текущего отрезка
                    vars.buffered=True									                #и подвешиваем- ожидание записи
            else:													                    # если статус меняется после таймаута
                vars.statusDB=vars.currentState				        	                #задаем отрезок для записи (подвешенный): статус
                vars.timeDB=vars.currentStateTime						                #время
                vars.lengthDB=(timeNow - vars.currentStateTime).total_seconds()			#длительность
                vars.currentState = status								                #задаем новй текущий отрезок: статус
                vars.currentStateTime = timeNow 						                #начала отрезка
            vars.currentInterval = interval							                    #в любом случае текущий интервал = интервал канала
    if vars.buffered : 
        if (timeNow-vars.currentStateTime).total_seconds()>=vars.minLength :            #если есть отрезок ожидающий записи - пишем его по прошествии min_length
            dbWriteFlag=True
            vars.buffered=False

    if dbWriteFlag  :
        dbWriteFlag=False
        vars.writeInit=False                    #сбрасываем флаг инициализации записи если был 1
        if vars.lengthDB>10 or vars.lengthDB<90000 : 
            #vars.lengthDB=1                    #отмечаем первый отрезок формируемый при старте МРВ тк нет текущей даты
            # vars.dbQuie.put({'type':Consts.INSERT,
            # 'sql':'INSERT INTO track_2 VALUES (%s, %s, %s, %s)'
            # ,'params': (vars.channel.id, vars.timeDB.strftime("%Y:%m:%d %H:%M:%S"), vars.statusDB, int(round(vars.lengthDB)))
            # })
            logics.db_put_state(vars.db_quie,
                                {   'id':vars.channel.id, 
                                    'project_id':vars.project_id, 
                                    'time':vars.timeDB.strftime("%Y-%m-%d %H:%M:%S"),
                                    'status':vars.statusDB,
                                    'length':int(round(vars.lengthDB))
                                    })
            
            logics.jsdb_put_state({   'id':vars.channel.id, 
                                    'time':vars.timeDB.strftime("%Y-%m-%dT%H:%M:%S"),
                                    'status':vars.statusDB,
                                    'length':int(round(vars.lengthDB))
                                    })
            