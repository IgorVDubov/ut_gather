
def db_writer(vars):
    '''
        принудительная запись в БД
        'scheduller_write_init': '13002.args.write_init',
        'mb_write_init': None,                         # сюда значение из функции записи регистра MBExchangeServer 
        'mb_write_init_reset': '2999.result_in',       # пишем значение в регистр собственного MBExchangeServer
        'mb_write_runs_flag': False,                   # идет процесс записи от сигнала mb - для исключения двойной записи пока сбрасывакется сигнал
        'write_init_2120': False,
        'write_counter_2120': False,
        'write_init_2040': False,
        'write_counter_2040': False,
    '''
    if vars.scheduller_write_init:
        print('!!!!!!!!!!    sheduller write_init   !!!!!!')
    if vars.mb_write_init:
        print('!!!!!!!!!!    modbus signal write_init   !!!!!!')

    if vars.mb_write_init is False and vars.mb_write_init_reset is False:
        vars.mb_write_init_reset = None
        vars.mb_write_runs_flag = False

    if vars.scheduller_write_init or vars.mb_write_init and not vars.mb_write_runs_flag:
        vars.mb_write_runs_flag = True
        vars.write_init_2120 = True
        vars.write_counter_2120 = True
        vars.write_init_2040 = True
        vars.write_counter_2040 = True

    if vars.scheduller_write_init:
        vars.scheduller_write_init = False
    if vars.mb_write_init:
        vars.mb_write_init_reset = False
