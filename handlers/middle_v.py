from datetime import datetime
import dataconnector as dc

# def running_middle(vars):
#     '''
#     обработчик текущего среднего скорости
#     пишется 1 раз в 5 минут
#     VARS:
#         result - текущее среднее значение
#         data - входящее значение
#         min_V - мин порог скорости для подсчета среднего
#         summ - аккумулятор
#         n - количество значений
#         reset - сброс среднего
#         write - флаг записи
#         db - база данных
#     '''
#     if vars.reset:
#         vars.summ = 0
#         vars.n = 0
#         vars.reset = False
        
#     if vars.data > vars.min_V:
#         vars.summ+=vars.data
#         vars.n+=1
#         vars.result = vars.summ / vars.n
        
    
def running_middle(vars):
    '''
    обработчик текущего среднего 
    периодический расчет
    считает собственное бегущее среднее значение, которое сбрасывается через 
    reset_signal. Может использоваться в расчетах цепочек 
    значение->среднее за 5минут->среднее за 30 минут-среднее за 1 час
    вызов часового среднего сбрасывает 30мин среднее и тп
    VARS:
        result - текущее среднее значение источника за время подсчета
        data - входящее значение
        middle - текущее собственное среднее значение
        summ - аккумулятор собственного среднего
        n - количество значений
        min_V - мин порог скорости для подсчета среднего
        reset_signal - исходящий сигнал сброс среднего
        reset - входящий сигнал сброс среднего
        m_id - id станка
        project_id - id проекта
        db_quae - очередь записи в базу данных
    '''
    vars.reset_signal = True
    
    vars.result = vars.data
    
    if vars.reset:
        vars.summ = 0
        vars.n = 0
        vars.reset = False
        vars.middle = 0
    
    if vars.data > vars.min_V:
        vars.summ += vars.data
        vars.n += 1
        vars.middle = vars.summ / vars.n
    
    if vars.db_queue is not None:
        dc.db_put_middle(vars.db_queue, {
            'm_id': vars.m_id,
            'project_id': vars.project_id,
            'date_time': datetime.now(),
            'value': vars.result
            })
