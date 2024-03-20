# from gather.interfaces.db.dbinterface import DBInterface
from gathercore.interfaces.db.dbcommands import (
    DBInsert,
    DBCommit,
    DBSelect,
)
from models import Idle


def insert_state(db_quie, state_rec: dict):
    #print(f'db_put_state {state_rec}')
    sql = f'''insert into track_{state_rec.get(
        "project_id", "")} values  (%s,%s,%s,%s)'''
    params = (state_rec.get('id'),
              state_rec.get('time'),
              state_rec.get('status'),
              state_rec.get('length'))
    db_quie.put(DBInsert(sql, params))
    # db_quie.put({
    #     'func':DBInterface.commit_sql_querry,
    #     'sql':sql, 'params':params})


def insert_idle(db_quie, ilde_rec):
    sql = f'''insert into idles_{ilde_rec.get(
        "project_id", "")} values  (%s,%s,%s,%s,%s,%s)'''
    params = (ilde_rec.get('id'),
              ilde_rec.get('cause'),
              ilde_rec.get('operator_id',),
              ilde_rec.get('cause_time'),
              ilde_rec.get('cause_set_time'),
              ilde_rec.get('length'))
    db_quie.put(DBInsert(sql, params))


def replace_current_idle_tmp(db_quie, tmp_ilde_rec):
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
    db_quie.put(DBCommit(sql, params))


def delete_current_idle_tmp(db_quie, machine_id):
    sql = 'delete from temp_idles where machine_id = %s'
    params = (
        machine_id,
    )
    db_quie.put(DBCommit(sql, params))


def select_temp_idles(db_interface):
    sql = '''select * from temp_idles'''

    reply = db_interface.direct_call(DBSelect(sql))
    
    return reply


# def insert_idle(connection, params):
#     cur = connection.cursor()
#     cur.execute(
#     f'insert into idles_{params.get("project_id","")} values  (%s,%s,%s,%s,%s,%s)',
#                         (params.get('id'),
#                         params.get('cause'),
#                         params.get('operator_id',),
#                         params.get('cause_time'),
#                         params.get('cause_set_time'),
#                         params.get('length')))
#     connection.commit()

# def insert_state(connection, params):
#     cur = connection.cursor()
#     cur.execute(f'insert into track_{params.get("project_id","")} values  (%s,%s,%s,%s)',
#                         (params.get('id'),
#                         params.get('time'),
#                         params.get('status'),
#                         params.get('length')))
#     connection.commit()
