import json
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import TypedDict

from gathercore.mylib import colors

from models import CurrentStateProtocol, Idle
import dataconnector as dc
import dbqueries as db_queries
import projectglobals as project_globals
import settings
import config
from gathercore.channels.channelbase import ChannelsBase
from gathercore.channels.channels import Channel
from gathercore.gtyping import DBInterface


def convert_none_2_str(func):
    '''
    convert None in function result to 'None'
    work with result type: single var, dict, list
    '''
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, dict):
            for key, val in result.items():
                if val is None:
                    result.update({key: str(val)})
        elif isinstance(result, list):
            for val in result:
                if val is None:
                    val = str(val)
        elif isinstance(result, type(None)):
            result = str(None)
        return result
    return wrapper


def get_server_time():
    '''
    returns server time for put to clients
    '''
    return datetime.now().strftime(settings.TIME_FORMAT)


def load_machines_idle(db_interface):
    # if settings.TEMP_IDLES_IN_DB:
    #     idles = load_idles_from_db(db_interface)
    # else:
    #     idles = load_from_file()
    idles = load_idles_from_db(db_interface)
    for idle in idles:
        project_globals.machines_idle.update(idle)


def load_idles_from_db(db_interface):
    '''
    loads idle from temp_idles 
    '''
    records = db_queries.select_temp_idles(db_interface)
    idles = []
    for rec in records:
        machine_id, state, tech_idle, \
            begin_time, operator_id, cause_id, cause_time, \
            cause_set_time, length = rec
        idles.append({machine_id: Idle(state,
                                       tech_idle,
                                       begin_time,
                                       operator_id,
                                       cause_id,
                                       cause_time,
                                       cause_set_time,
                                       length)})
    return idles


def load_from_file():
    '''
    loads idle from buffer file 
    '''
    # TODO временное решение или вынести в БД или вынести файл в настройки

    records = []
    with open('idles.txt', 'r') as file:
        line = ' '
        while line:
            if line := file.readline():
                if data := json.loads(line):
                    rec = {data.get('id'): Idle(
                        data.get('state'),
                        data.get('tech_idle'),
                        datetime.strptime(data.get('begin_time'),
                                          settings.TIME_FORMAT) if data.get(
                            'begin_time') else None,
                        data.get('operator'),
                        data.get('cause_id'),
                        datetime.strptime(data.get('cause_time'),
                                          settings.TIME_FORMAT) if data.get(
                            'cause_time') else None,
                        datetime.strptime(data.get('cause_set_time'),
                                          settings.TIME_FORMAT) if data.get(
                            'cause_set_time') else None,
                        data.get('length')
                    )
                    }
                    records.append(rec)
    return records


def save_machines_idle(db_quie, machine_id, project_id):
    if project_id != 0:  # проекты с индексом 0 - демо: не пишем в БД
        save_to_db(db_quie, machine_id, project_globals.machines_idle)
    # else:
    #     save_to_file(project_globals.machines_idle)


def save_to_db(db_quie, machine_id, machines_idle: dict):
    '''
    saves temp idle to db
    '''
    for machine_id, idle in machines_idle.items():
        if idle is not None:
            data = dict({'machine_id': machine_id,
                        'state': idle.state,
                         'tech_idle': idle.tech_idle,
                         'begin_time': idle.begin_time.strftime(settings.TIME_FORMAT) if idle.begin_time else None,
                         'operator_id': idle.operator,
                         'cause_id': idle.cause,
                         'cause_time': idle.cause_time.strftime(settings.TIME_FORMAT) if idle.cause_time else None,
                         'cause_set_time': idle.cause_set_time.strftime(settings.TIME_FORMAT) if idle.cause_set_time else None,
                         'length': idle.length})
            db_queries.replace_current_idle_tmp(db_quie, data)
        else:
            db_queries.delete_current_idle_tmp(db_quie, machine_id)


def save_to_file(machines_idle: dict):
    '''
    saves idle from buffer file 
    '''
    # TODO временное решение или вынести в БД или вынести файл в настройки
    with open('idles.txt', 'w') as file:
        for machine_id, idle in machines_idle.items():
            if idle:
                data = dict({'id': machine_id,
                            'state': idle.state,
                             'tech_idle': idle.tech_idle,
                             'begin_time': idle.begin_time.strftime(settings.TIME_FORMAT) if idle.begin_time else None,
                             'operator': idle.operator,
                             'cause_id': idle.cause,
                             'cause_time': idle.cause_time.strftime(settings.TIME_FORMAT) if idle.cause_time else None,
                             'cause_set_time': idle.cause_set_time.strftime(settings.TIME_FORMAT) if idle.cause_set_time else None,
                             'length': idle.length})
                file.write(json.dumps(data)+'\n')


def jsdb_put_state(state_rec: dict):
    raise NotImplemented('move to dc')
    if state_rec.get('length') and state_rec['length'] > 0:
        project_globals.states_db.append(state_rec)
        project_globals.states_buffer.append(state_rec)


def db_put_state(db_quie: DBInterface, state_rec: dict):
    raise NotImplemented('move to dc')
    print(f'db_put_state {state_rec}')
    if state_rec.get('length') and state_rec['length'] > 0:
        if state_rec.get('project_id') == 0:
            jsdb_put_state(state_rec)
        else:
            db_queries.insert_state(db_quie, state_rec)


def jsdb_put_idle(rec: dict):

    print(f'jsdb_put_idle {rec}')
    project_globals.idles_db.append(rec)
    if operator := get_operator_data(rec['operator']):
        rec['operator'] = operator.get('name')
    else:
        pass  # TODO обработать
    project_globals.idles_buffer.append(rec)
    ...


def addCause(new_cause: str):  # добавляем новую причину в список возможных
    settings.IDLE_CAUSES.update(
        {max(settings.IDLE_CAUSES.keys())+1: new_cause})


def reset_causes():  # добавляем новую причину в список возможных
    settings.IDLE_CAUSES = settings.DEFAILT_IDLE_CAUSES


def check_allowed_machine(machine_id: int, remote_ip: str) -> bool:
    '''
     проверяет доступность канала станка для подключения клиента с указанного в разрешенных ip
     если список ip  пустой - разрешаются все
    '''
    allowed = dc.get_allowed_machines()
    if machine_id in allowed.keys():
        allowed_ip = allowed[machine_id]
        if len(allowed_ip) == 0 or remote_ip in allowed_ip:
            return True
        else:
            raise ValueError(
                f'ip {remote_ip} not allowed for {machine_id} client')
    else:
        raise ValueError(
            f'machine {machine_id} not allowed for client from ip {remote_ip}')


def get_machine_operators(machine_id: int):
    return dc.get_machine_operators(machine_id)


def get_operator_data(operator_id: int):
    return dc.get_operator_data(operator_id)


def get_machine_from_user(user_id: int) -> list[int]:
    # try:
    return settings.user_machines[user_id]
    # except ValueError:
    #     raise ValueError


# TODO убрать
def get_causeid_arg(machine_ch: Channel) -> str:
    '''
    значение causeid_arg обработчика канала machine_ch для передаси в web клиент для подписки
    '''
    return str(machine_ch.get_arg(settings.IDLE_HANDLERID_ARG)) + '.' + settings.CAUSEID_ARG


# TODO refact with DB
def get_machine_causes(id: int) -> dict[int, str]:
    '''
    causes of current machine id
    '''
    return settings.IDLE_CAUSES


# TODO refact with DB
def get_causes() -> dict[int, str]:
    '''
    return all avaluable causes 
    '''
    return settings.IDLE_CAUSES

# @convert_none_2_str


def get_channel_arg(channel_base: ChannelsBase,
                    machine_id: int,
                    arg: str) -> int | str | None:
    result = channel_base.get_by_name(str(machine_id)).get_arg(arg)
    return result


def get_current_state(machine_channel: Channel) -> CurrentStateProtocol:
    # channel = channel_base.get_by_name(str(machine_id))
    if idle := project_globals.machines_idle.get(machine_channel.
                                                 get_arg('args.m_id')):
        saved_state = idle.state
        saved_state_time = idle.begin_time.strftime(
            settings.TIME_FORMAT) if idle.begin_time else None
        saved_current_cause = idle.cause
        saved_current_cause_time = idle.cause_time.strftime(
            settings.TIME_FORMAT) if idle.cause_time else None
        saved_current_cause_set_time = idle.cause_set_time.strftime(
            settings.TIME_FORMAT) if idle.cause_set_time else None
    else:
        saved_state = None
        saved_state_time = None
        saved_current_cause = None
        saved_current_cause_time = None
        saved_current_cause_set_time = None
    state = machine_channel.get_arg(settings.STATE_ARG)
    # if state==saved_state:
    if state in settings.IDLE_STATES and idle:
        state = saved_state
        begin_time = saved_state_time
        cause_id = saved_current_cause
        cause_time = saved_current_cause_time
        cause_set_time = saved_current_cause_set_time
    else:
        begin_time = machine_channel.get_arg(settings.STATE_TIME_ARG)
        if begin_time is not None and begin_time != 0:
            begin_time = begin_time.strftime(settings.TIME_FORMAT)
        else:
            begin_time = None
        cause_id = None
        cause_time = None
        cause_set_time = None
    result: CurrentStateProtocol = {
        'machine': machine_channel.get_arg('args.m_id'),
        'state': state,
        'begin_time': begin_time,
        'cause_id': cause_id,
        'cause_time': cause_time,
        'cause_set_time': cause_set_time
    }
    return result


def current_idle_get(machine_id: int):
    return project_globals.machines_idle.get(machine_id)


def current_idle_set(db_quie,
                     machine_id: int,
                     project_id: int,
                     state: int,
                     tech_idle_length: int,
                     operator: int | None = None,
                     cause: int | None = None,
                     cause_time: datetime | None = None,
                     cause_set_time: datetime | None = None):
    print(f'set idle to {machine_id} with state {state}')
    begin_time = datetime.now()
    idle_data = {
                machine_id: Idle(state,
                tech_idle_length, begin_time,
                operator,
                cause, cause_time,
                cause_set_time,
                None)
                }
    project_globals.machines_idle.update(idle_data)
    save_machines_idle(db_quie, machine_id, project_id)


def current_idle_add_cause(machine_id: int,
                           operator_id: int,
                           cause_id: int,
                           cause_set_time: datetime,
                           prj_id: int,
                           db_quie: DBInterface
                           ):

    if current_idle := project_globals.machines_idle.get(machine_id):
        project_globals.machines_idle[machine_id].operator = operator_id
        if current_idle.cause is not None:
            print(
                f'change cause idle to {machine_id} from {current_idle.cause} to {cause_id}')
            if current_idle.cause != 0:  # если причина была сброшена через causeid=0 время причины оставляем от момента сброса
                current_idle_store(machine_id, prj_id, db_quie)
                project_globals.machines_idle[machine_id].cause_time = datetime.now(
                )
            elif current_idle.cause == settings.TECH_IDLE_ID:
                current_idle_store(machine_id, prj_id, db_quie)
                if (datetime.now()-current_idle.cause_time).seconds > current_idle.tech_idle:
                    project_globals.machines_idle[machine_id].cause_time = current_idle.cause_time + timedelta(
                        0, current_idle.tech_idle)
        else:
            project_globals.machines_idle[machine_id].cause_time = current_idle.begin_time

        print(f'add cause idle to {machine_id} cause:{cause_id}')
        project_globals.machines_idle[machine_id].cause = cause_id
        project_globals.machines_idle[machine_id].cause_set_time = cause_set_time
        save_machines_idle(db_quie, machine_id, prj_id)
    else:
        print(project_globals.machines_idle)
        raise KeyError(
            f'no machine {machine_id} in project_globals.machines_idle')


def current_idle_reset(db_quie, machine_id: int, project_id: int):
    print(f'reset idle {machine_id} ')
    project_globals.machines_idle.update({machine_id: None})
    save_machines_idle(db_quie, machine_id, project_id)


def current_idle_store(machine_id: int, prj_id: int, db_quie: DBInterface):
    if idle := project_globals.machines_idle.get(machine_id):
        project_globals.machines_idle[machine_id].length = int(
            round((datetime.now()-idle.cause_time).total_seconds()))
        print(
            f'{colors.CGREENBG}Store machime {machine_id} Idle to DB: {settings.STATES[idle.state]}, cause: {settings.IDLE_CAUSES.get(idle.cause, 0)}, length {idle.length} {colors.CEND}')
        print(idle)
        store_dict = {'id': machine_id}
        store_dict.update(project_id=prj_id)
        store_dict.update(asdict(idle))
        for key, val in store_dict.items():
            if isinstance(store_dict[key], datetime):
                store_dict.update(
                    {key: val.strftime('%Y-%m-%d %H:%M:%S')})  # type: ignore

        print(f'{colors.CYELLOWBG}db_quie:{store_dict} {colors.CEND}')
        if prj_id == 0:
            jsdb_put_idle(store_dict)  # локально для демо проекты с инд 0!!!
        else:
            db_queries.insert_idle(db_quie, store_dict)
