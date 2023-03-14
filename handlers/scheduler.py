import subprocess
from datetime import datetime
from time import time

TASK1_TIME='22:30'

def write_init(vars):
    print ('!!!!!!!!!!in sheduller Task1!!!!!!')
    vars.write_init_2020=True
    vars.write_counter_2020=True



def day_scheduler(vars):
    '''
    execute tasks at shedulled day time
    TASK1_TIME format str '24h:m:s' or '24h:m' (00 sec) 
    external cmd files at ./cmd  dir
    '''
    now=datetime.now()
    try:
        time1 = datetime.strptime(TASK1_TIME, '%H:%M:%S')
    except ValueError:
        time1 = datetime.strptime(TASK1_TIME, '%H:%M')
    # print (f'now:{now.hour}:{now.minute}:{now.second} goal:{time1.hour}:{time1.minute}:{time1.second} eqw:{now==time1}')
    if time1.hour==now.hour and time1.minute==now.minute and time1.second==now.second:
        print('!!!!!!!!!!!!******************!!!!!!!!!!!!!!!!!!')
        subprocess.run("./cmd/echo.cmd", shell=True)
        # vars.write_init_5001=True
        vars.write_init_2020=True
        vars.write_counter_2020=True
