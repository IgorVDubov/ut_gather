
def db_writer(vars):
    '''
    принудительная запись в БД
    ''' 
    if  vars.scheduller_write_init:
        print ('!!!!!!!!!!    sheduller write_init   !!!!!!')
    if  vars.mb_write_init:
        print ('!!!!!!!!!!    modbus signal write_init   !!!!!!')
    
    if vars.mb_write_init is False and vars.mb_write_init_reset is False:
        vars.mb_write_init_reset = None
        
    if vars.scheduller_write_init or vars.mb_write_init:
        vars.write_init_2120=True
        vars.write_counter_2120=True
        vars.write_init_2040=True
        vars.write_counter_2040=True
    
    if  vars.scheduller_write_init:
         vars.scheduller_write_init = False
    if  vars.mb_write_init:
         vars.mb_write_init_reset = False