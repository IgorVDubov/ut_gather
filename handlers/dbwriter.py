def db_writer(vars):
    """
    принудительная запись в БД
    'scheduller_write_states': '13001.args.write_init', # оигнал записи статусов (через 3 сек после записи счетчиков)
    'scheduller_write_counters': '13002.args.write_init',   # оигнал записи счетчиков
    'mb_write_init': None,                         # сюда значение из функции записи регистра MBExchangeServer
    'mb_write_init_reset': '2999.result_in',       # пишем значение в регистр собственного MBExchangeServer
    'mb_write_runs_flag': False,                   # идет процесс записи от сигнала mb - для исключения двойной записи пока сбрасывакется сигнал
    'write_init_2120': False,
    'write_counter_2120': False,
    'write_init_2040': False,
    'write_counter_2040': False,
    'write_init_2100': False,
    'write_counter_2100': False,
    """

    def write_counters_ON():
        vars.write_counter_2120 = True
        vars.write_counter_2040 = True
        vars.write_counter_2100 = True
        vars.write_counter_2111 = True
        vars.write_counter_2114 = True
        vars.write_counter_2117 = True
        vars.write_counter_2103 = True
        vars.write_counter_2106 = True

    def write_init_ON():
        vars.write_init_2120 = True
        vars.write_init_2040 = True
        vars.write_init_2100 = True
        vars.write_init_2111 = True
        vars.write_init_2114 = True
        vars.write_init_2117 = True
        vars.write_init_2103 = True
        vars.write_init_2106 = True
        vars.write_init_1416 = True
        vars.write_init_1501 = True
        vars.write_init_2901 = True
        vars.write_init_2902 = True
        vars.write_init_2903 = True
        vars.write_init_2904 = True
        vars.write_init_2905 = True
        vars.write_init_2906 = True

    if vars.scheduller_write_states:
        print("!!!!!!!!!!    sheduller write states  !!!!!!")
    if vars.scheduller_write_counters:
        print("!!!!!!!!!!    sheduller write counters   !!!!!!")
    if vars.mb_write_init:
        print("!!!!!!!!!!    modbus signal write_init   !!!!!!")

    if vars.mb_write_init is False and vars.mb_write_init_reset is False:
        vars.mb_write_init_reset = None
        vars.mb_write_runs_flag = False

    if vars.scheduller_write_states:
        write_init_ON()

    if vars.scheduller_write_counters:
        write_counters_ON()

    if vars.mb_write_init and not vars.mb_write_runs_flag:
        vars.mb_write_runs_flag = True
        write_init_ON()
        write_counters_ON()

    if vars.scheduller_write_states:
        vars.scheduller_write_states = False

    if vars.scheduller_write_counters:
        vars.scheduller_write_counters = False

    if vars.mb_write_init:
        vars.mb_write_init_reset = False
