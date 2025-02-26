from gathercore.interfaces.db import DBInterface
from gathercore.interfaces.db.dbcommands import (
    DBInsert,
    DBCommit,
    DBSelect,
)
from models import Idle

def insert_sql(db_queue, sql: str, params: tuple):
    db_queue.put(DBInsert(sql, params))


def insert_state(db_queue, state_rec: dict):
    sql = f'''insert into track_{state_rec.get(
        "project_id", "")} values  (%s,%s,%s,%s)'''
    params = (state_rec.get('id'),
              state_rec.get('time'),
              state_rec.get('state'),
              state_rec.get('length'))
    db_queue.put(DBInsert(sql, params))


def insert_middle(db_queue, rec: dict):
    sql = f'''insert into middle_{rec.get(
        "project_id", "")} values  (%s,%s,%s)'''
    params = (rec.get('m_id'),
              rec.get('date_time'),
              rec.get('value'))
    db_queue.put(DBInsert(sql, params))


def insert_idle(db_queue, ilde_rec):
    sql = f'''insert into idles_{ilde_rec.get(
        "project_id", "")} values  (%s,%s,%s,%s,%s,%s)'''
    params = (ilde_rec.get('id'),
              ilde_rec.get('cause'),
              ilde_rec.get('operator_id',),
              ilde_rec.get('cause_time'),
              ilde_rec.get('cause_set_time'),
              ilde_rec.get('length'))
    db_queue.put(DBInsert(sql, params))



def replace_current_idle_tmp(db_queue, tmp_ilde_rec):
    sql = 'replace into temp_idles values  (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    params = (tmp_ilde_rec.get('machine_id'),
              tmp_ilde_rec.get('state'),
              tmp_ilde_rec.get('tech_idle'),
              tmp_ilde_rec.get('begin_time'),
              tmp_ilde_rec.get('operator_id'),
              tmp_ilde_rec.get('cause_id',),
              tmp_ilde_rec.get('cause_time'),
              tmp_ilde_rec.get('cause_set_time'),
              tmp_ilde_rec.get('length')
              )
    db_queue.put(DBCommit(sql, params))


def delete_current_idle_tmp(db_queue, machine_id):
    sql = 'delete from temp_idles where machine_id = %s'
    params = (
        machine_id,
    )
    db_queue.put(DBCommit(sql, params))


def select_temp_idles(db_interface: DBInterface) -> list:
    sql = '''select * from temp_idles'''

    reply = db_interface.direct_call(DBSelect(sql))
    
    return reply

def querry_causes(db_interface: DBInterface,
                  machine_id: int,
                  project_id: int) -> list:
     
    sql = f'''SELECT cause_id, NAME, color, position 
                FROM machine_causes_{project_id} 
                JOIN idle_causes ON idle_causes.id = machine_causes_{project_id}.cause_id
                WHERE machine_id = %s'''
    params = (
        machine_id,
    )
    reply = db_interface.direct_call(DBSelect(sql, params))
    return reply

def querry_idels(db_interface: DBInterface, machine_id, time1, time2, project_id):
    sql = f'''SELECT * FROM idles_{project_id} 
                WHERE machine_id = %s 
                AND 
                cause_time BETWEEN %s AND %s 
                order by cause_time'''
    params = (machine_id, time1, time2)
    reply = db_interface.direct_call(DBSelect(sql, params))
    return reply

def querry_settings(db_interface: DBInterface):
    sql = 'SELECT * FROM settings'
    reply = db_interface.direct_call(DBSelect(sql))
    return reply

def update_arg_setting(db_queue, arg, val):
    sql = 'UPDATE settings SET value = %s WHERE arg = %s'  
    params = (str(val), arg)
    db_queue.put(DBInsert(sql, params))