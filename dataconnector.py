from datetime import datetime

import config
from gather.consts import  Formats # TODO move Consts.DATE_FORMAT_DB from Consts

import dbqueries as dbc
import settings
import projectglobals as project_globals


def get_causes(id:int)->dict[int:str]:
    return settings.IDLE_CAUSES
    # return dbc.querry_causes(id)

def get_allowed_machines()->dict:
    if config.DEMO_DB:
        return settings.ALLOWED_MACHINES
    else:
        pass # get data from db
def get_machine_operators(machine_id):
    '''
    список доступных операторов по id станка
    '''
    if config.DEMO_DB:
        return settings.OPERATORS

def get_operator_data(operator_id):
    return settings.OPERATORS.get(operator_id)

def get_current_operator(machine_id):     #взять из бд операторов machine_id последнюю не закрытую сессию
    if operator:=get_logged_operator(machine_id):
        try:
            return {'id':operator['operator_id'], 'name':get_machine_operators(machine_id)[operator['operator_id']]['name']}
        except KeyError:
            return None
    else:
        return None

def get_operator(machine_id, operator_id):   
    if oper_id:= next((oper for oper in get_machine_operators(machine_id) if oper==operator_id), None):
        try:
            return {'id':oper_id, 'name':get_machine_operators(machine_id)[oper_id]['name']}
            # return {'id':oper_id, 'name':settings.OPERATORS[oper_id]['name']}
        except KeyError:
            return None
    else:
        return None

def get_logged_operator(machine_id):     
    return next((oper for oper in project_globals.operators_db if oper['logout']==None), None)


def set_operator_login(macine_id, operator_id):
    '''
    пишем логин оператора на macine_id
    '''
    print (f'operator {get_machine_operators(1).get(operator_id, None)} logit to {macine_id}')
    project_globals.operators_db.append({'operator_id':operator_id ,'machine_id':macine_id , 'login':datetime.now().strftime(Formats.DATE_FORMAT_DB), 'logout':None})

def set_operator_logout(macine_id,operator_id):
    '''
    ищем у macine_id незакрытую сессию и пишем туда время окончания
    '''
    try:
        get_logged_operator(macine_id)['logout']=datetime.now().strftime(Consts.DATE_FORMAT_DB)
    except (KeyError, TypeError):
        print (f'no logout operators at {macine_id}')

    print (f'operator {get_machine_operators(1).get(operator_id, None)} logout to {macine_id}')