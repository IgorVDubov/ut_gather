from loguru import logger
import logics
from gathercore.channels.channelbase import ChannelsBase
from gathercore.gtyping import DBInterface
import dbqueries as db_queries

def init(databus):
    db_interface = databus.get_object('db_interface')
    logics.load_machines_idle(db_interface)
    
def init_args(db_interface: DBInterface, channels_base: ChannelsBase):
    settings = db_queries.querry_settings(db_interface)
    for arg, val_type, value, name in settings:
        if channel:= channels_base.get_by_argname(arg):
            try:
                match val_type.lower():
                    case 'int':
                        value = int(value)
                    case 'float':
                        value = float(value)
                    case 'bool':
                        value = bool(value)
                    case 'str':
                        pass # value = value
                channel.set_channel_arg_name(arg, value)
            except ValueError as e:
                logger.error(f'channel {arg} set {value} rise ValueError: {e}')
        else:
            logger.error(f'channel {arg} not found')