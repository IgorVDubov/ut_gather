'''
Считает скорость по показаниям значения AI
по коэфф vars.k
'''


def ai2021(vars):
    '''
    result 
	result_in
	in_dost 
	counter 
	reset_counter 
	k 
	min_ai=10
    '''
    if vars.result_in is not None:
        result = vars.result_in
    else:
        return
    
    if not vars.in_dost or result < vars.min_ai:
        result = 0

    vars.result = result * vars.k * 60      # k роассчитан как м/сек, перевод m/min для отображения скорости

    if vars.result > 0:
        vars.counter_acc += result * vars.k      # считаем метры

    if vars.reset_counter:
        vars.counter_acc = 0
        vars.reset_counter = False
    vars.counter = round(vars.counter_acc)
    