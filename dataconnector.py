from datetime import datetime

import config
from gathercore.consts import Formats  # TODO move Consts.DATE_FORMAT_DB from Consts

import dbqueries as dbc
import settings
import projectglobals as project_globals
from models import Operator
from gathercore.gtyping import DBQuie
import dbqueries as db_queries


def db_get_all_states(id: int):
    return [rec for rec in project_globals.states_db]


def db_get_all_idles(id: int):
    # return [rec for rec in project_globals.idles_db if (rec and rec.get('id')==id)]
    return [rec for rec in project_globals.idles_db]

def db_get_all_operators():
    result= [rec for rec in project_globals.operators_db]
    [rec.update({'operator': (settings.OPERATORS[rec['operator_id']]['name'])}) for rec in result]
    return result


def get_causes(id: int) -> dict[int:str]:
    return settings.IDLE_CAUSES
    # return dbc.querry_causes(id)


def get_allowed_machines() -> dict:
    if config.DEMO_DB:
        return settings.ALLOWED_MACHINES
    else:
        pass  # get data from db


def get_machine_operators(machine_id):
    '''
    список доступных операторов по id станка
    '''
    if config.DEMO_DB:
        return settings.OPERATORS


def get_operator_data(operator_id):
    return settings.OPERATORS.get(operator_id)


# взять из бд операторов machine_id последнюю не закрытую сессию
def get_current_operator(machine_id: int):
    if operator := get_logged_operator(machine_id):
        try:
            return {'id': operator['operator_id'], 'name': get_machine_operators(machine_id)[operator['operator_id']]['name']}
        except KeyError:
            return None
    else:
        return None


def get_operator(machine_id, operator_id):
    if oper_id := next((oper for oper in get_machine_operators(machine_id) if oper == operator_id), None):
        try:
            return {'id': oper_id, 'name': get_machine_operators(machine_id)[oper_id]['name']}
            # return {'id':oper_id, 'name':settings.OPERATORS[oper_id]['name']}
        except KeyError:
            return None
    else:
        return None


def get_logged_operator(machine_id: int):
    return next((oper for oper in project_globals.operators_db 
                    if (oper['machine_id']==machine_id) 
                        and (oper['logout'] is None)
                ),None)


def set_operator_login(macine_id, operator_id):
    '''
    пишем логин оператора на macine_id
    '''
    print(
        f'operator {get_machine_operators(1).get(operator_id, None)} logit to {macine_id}')
    rec={'operator_id': operator_id,
        'machine_id': macine_id,
        'login': datetime.now().strftime(Formats.DATE_FORMAT_DB),
        'logout': None}
    project_globals.operators_db.append(rec)
    rec.update({'operator': settings.OPERATORS[operator_id]['name']})
    project_globals.operators_buffer.append(rec)
    
    


def set_operator_logout(macine_id, operator_id):
    '''
    ищем у macine_id незакрытую сессию и пишем туда время окончания
    '''
    try:
        rec=get_logged_operator(macine_id)
        rec['logout'] = datetime.now().strftime(
            Formats.DATE_FORMAT_DB)
    except (KeyError, TypeError):
        print(f'no logout operators at {macine_id}')
    rec.update({'operator': settings.OPERATORS[operator_id]['name']})    
    project_globals.operators_buffer.append(rec)
    print(
        f'operator {get_machine_operators(1).get(operator_id, None)} logout to {macine_id}')

def jsdb_put_state(state_rec: dict):
    if state_rec.get('length') and state_rec['length'] > 0:
        project_globals.states_db.append(state_rec)
        project_globals.states_buffer.append(state_rec)


def db_put_state(db_quie: DBQuie, state_rec: dict):
    print(f'db_put_state {state_rec}')
    if state_rec.get('length') and state_rec['length'] > 0:
        if state_rec.get('project_id') == 0:
            jsdb_put_state(state_rec)
        else:
            db_queries.insert_state(db_quie, state_rec)

