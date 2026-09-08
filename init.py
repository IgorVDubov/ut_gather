import dbqueries as db_queries
import logics
from gathercore.channels.channelbase import ChannelsBase
from gathercore.gtyping import DBInterface
from loguru import logger


def init(databus):
    db_interface = databus.get_object("db_interface")
    logics.load_machines_idle(db_interface)


def init_args(db_interface: DBInterface, channels_base: ChannelsBase, project_ids: set):
    settings = []
    for id in project_ids:
        s = db_queries.querry_settings(db_interface, id)
        settings.extend(s)
    for setting in settings:
        arg, val_type, value, name = setting.values()
        if channel := channels_base.get_by_argname(arg):
            try:
                match val_type.lower():
                    case "int":
                        value = int(value)
                    case "float":
                        value = float(value)
                    case "bool":
                        value = bool(value)
                    case "str":
                        pass  # value = value
                channel.set_channel_arg_name(arg, value)
            except ValueError as e:
                logger.error(f"channel {arg} set {value} rise ValueError: {e}")
        else:
            logger.error(f"channel {arg} ({name}) not found")
