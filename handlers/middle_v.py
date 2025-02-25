
from handlers.lib import middle


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
        result - текущее среднее значение за время подсчета
        data - входящее значение
        middle - текущее собственное среднее значение
        summ - аккумулятор собственного среднего
        n - количество значений
        min_V - мин порог скорости для подсчета среднего
        reset_signal - исходящий сигнал сброс среднего
        reset - входящий сигнал сброс среднего
    '''
    vars.reset_signal = True
    
    if vars.result is None:
        vars.result = vars.data
        return
    
    # vars.result = vars.middle
    
    if vars.reset:
        vars.summ = 0
        vars.n = 0
        vars.reset = False
    
    if vars.data > vars.min_V:
        vars.summ += vars.data
        vars.n += 1
        vars.middle = vars.summ / vars.n
