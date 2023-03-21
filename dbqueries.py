# from gather.interfaces.db.dbinterface import DBInterface
from gather.interfaces.db.dbcommands import DBInsert

MIN_STORED_IDLE_LENGTH=5
MIN_STORED_STATE_LENGTH=5

def insert_state(db_quie, state_rec):
    print (f'db_put_state {state_rec}')
    sql=f'insert into track_{state_rec.get("project_id","")} values  (%s,%s,%s,%s)'
    params=(state_rec.get('id'), 
            state_rec.get('time'), 
            state_rec.get('status'), 
            state_rec.get('length'))
    if state_rec.get('length')>MIN_STORED_STATE_LENGTH:
        db_quie.put(DBInsert(sql, params))
        # db_quie.put({
        #     'func':DBInterface.commit_sql_querry, 
        #     'sql':sql, 'params':params})

def insert_idle(db_quie, ilde_rec):
    sql=f'insert into idles_{ilde_rec.get("project_id","")} values  (%s,%s,%s,%s,%s,%s)'
    params=(ilde_rec.get('id'), 
            ilde_rec.get('cause'), 
            ilde_rec.get('operator_id',), 
            ilde_rec.get('cause_time'), 
            ilde_rec.get('cause_set_time'), 
            ilde_rec.get('length'))
    if ilde_rec.get('length')>MIN_STORED_IDLE_LENGTH:
        db_quie.put(DBInsert(sql, params))
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