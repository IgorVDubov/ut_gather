def querry_causes(id):
    ...

def insert_idle(connection, params):
    cur = connection.cursor()
    cur.execute(f'insert into idles_{params.get("project_id","")} values  (%s,%s,%s,%s,%s,%s)',
                        (params.get('id'), 
                        params.get('cause'), 
                        params.get('operator_id',), 
                        params.get('cause_time'), 
                        params.get('cause_set_time'), 
                        params.get('length')))
    connection.commit()

def insert_state(connection, params):
    cur = connection.cursor()
    cur.execute(f'insert into track_{params.get("project_id","")} values  (%s,%s,%s,%s)',
                        (params.get('id'), 
                        params.get('time'), 
                        params.get('status',), 
                        params.get('length')))
    connection.commit()