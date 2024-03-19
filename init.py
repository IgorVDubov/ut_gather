import logics

def init(databus):
    db_interface = databus.get_object('db_interface')
    logics.load_machines_idle(db_interface)