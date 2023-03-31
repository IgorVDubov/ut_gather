from time import time
import asyncio

from ..mylib import logger

from . import channels

from .. import myexceptions

CHANNELS_EXEC_ORDER=[
            channels.Node,
            channels.Channel,
            channels.Programm, 
            channels.DBQuie, 
            channels.Scheduler,
            #channels.Message,
            ]

class ChannelsBase():
    def __init__(self):
        self.channels=[]
        self.channelsExecTime=None
        self.db_quie=asyncio.Queue()
    
    def add(self,channel:channels.Channel):
        found=next(filter(lambda _channel: _channel.id == channel.id, self.channels), None)
        if not found:
            if len(self.channels):
                try:
                    for ch in self.channels:
                        if CHANNELS_EXEC_ORDER.index(type(ch))>CHANNELS_EXEC_ORDER.index(type(channel)):
                            # print (f'insert channel {channel.id} ' )
                            self.channels.insert(self.channels.index(ch),channel)
                            return
                except ValueError:
                    logger.warning(f'cant find order on CHANNELS_EXEC_ORDER for channel {channel.id}, move to end')
            self.channels.append(channel)
            # print (f'append channel {channel.id} ' )
        else:
            raise myexceptions.ConfigException(f'duplicate id in channel base adding {channel} ')
    
    def get(self, id:int)->channels.Channel:
        try:
            found=next(filter(lambda _channel: _channel.id == id, self.channels))
        except StopIteration:
            found=None
        return found
        
    def get_by_argname(self, ch_arg_name:str)->channels.Channel:
        '''
        get Channel from str param 'ch_id.arg'
        '''
        ch_id, attr= channels.parse_attr_params(ch_arg_name)
        return self.get(ch_id)

    def execute(self, id:int):
        channel=self.get(id)
        try:
            result=channel()
        except myexceptions.ChannelException as e:
            logger.error(e)
        return result

    def executeAll(self):
        startTime=time()
        for channel in self.channels:
            print(f'exec {channel.id}')
            channel()
        self.channelsExecTime=time()-startTime

    def nodesToDict(self):
        result=dict()
        result.setdefault(channels.Node.__name__.lower(),[])
        for channel in self.channels:
            if isinstance(channel, channels.Node):
                result[channels.Node.__name__.lower()].append(channel.toDict())
        return result
    
    def nodesToDictFull(self):
        result=dict()
        result.setdefault(channels.Node.__name__.lower(),[])
        for channel in self.channels:
            if isinstance(channel, channels.Node):
                result[channels.Node.__name__.lower()].append(channel.toDictFull())
        return result
    
    def toDict(self):
        result=dict()
        for ch_type in CHANNELS_EXEC_ORDER:          #!!! если нет нового класса канала в массиве - не будет включен!!!!!!!!
            result.setdefault(ch_type.__name__.lower(),[])
        for channel in self.channels:
            result[channel.__class__.__name__.lower()].append(channel.toDict())
        return result
    
    def toDictFull(self):
        result=dict()
        for ch_type in CHANNELS_EXEC_ORDER:          #!!! если нет нового класса канала в массиве - не будет включен!!!!!!!!
            result.setdefault(ch_type.__name__.lower(),[])
        for channel in self.channels:
            result[channel.__class__.__name__.lower()].append(channel.toDictFull())
        return result

    def __str__(self) -> str:
        return ''.join(channel.__str__()+'\n' for channel in self.channels )

def channel_base_init(channels_config):
    # сначала у всех каналов создаем аттрибуты, потом привязываем связанные
    bindings=[]
    db_quie_channel=False
    ch_base=ChannelsBase()
    for channel_type in channels_config:
        ch_type=eval(channels.CHANNELS_CLASSES.get(channel_type))
        if ch_type==channels.Channel:
            cls=channels.Channel
        elif ch_type==channels.Node:
            cls=channels.Node
        elif ch_type==channels.Programm:
            cls=channels.Programm
        elif ch_type==channels.DBQuie:
            cls=channels.DBQuie
            db_quie_channel=True
        elif ch_type==channels.Scheduler:
            cls=channels.Scheduler
        # elif ch_type==channels.DBconnector:
        #     cls=channels.DBQuie
        # elif ch_type==channels.Message:
        #     cls=channels.Message
        else:
            raise myexceptions.ConfigException(f'no type in classes for {ch_type} {channel_type}')
        for channel_config in channels_config.get(channel_type):
            if db_quie_channel:
                channel_config.update({'dbQuie':ch_base.db_quie})
            if channel_config.get('args'):
                args=channel_config.pop('args')
                channel=cls(**channel_config)
                for name, arg in args.items():
                    bind_id, param= channels.parse_attr_params(arg)
                    if bind_id != None:
                        channel.addArg(name)
                        bindings.append((channel, name, bind_id, param))
                    else:
                        channel.addArg(name, param)
            else:
                channel=cls(**channel_config)
            if isinstance(channel, channels.Scheduler):
                channel.init_args()
            ch_base.add(channel)
        db_quie_channel=False
    for (channel_2_bind, name, bind_id, param) in bindings:
        if bind_id=='self':
            channel_2_bind.bindArg(name, channel_2_bind, param)
        elif bind_id and param:
            if bindChannel:=ch_base.get(bind_id):
                channel_2_bind.bindArg(name, bindChannel, param)
            else:
                raise myexceptions.ConfigException(f'Cant find channel {bind_id} when binding to {channel_2_bind.id}')
        elif bind_id and param==None:
            if bindChannel:=ch_base.get(bind_id):
                channel_2_bind.bindChannel2Arg(name, bindChannel)
            else:
                raise myexceptions.ConfigException(f'Cant find channel {bind_id} when binding in {channel_2_bind.id}')
    bindings=[]
    return ch_base

def bindChannelAttr(channelBase, ch_id:int,attrNmae:str)->channels.Vars:
    '''
    id- channel id
    attrname:str - channel attribute mane 
    '''
    if channel:=channelBase.get(ch_id):
        bindVar=channels.Vars()
        bindVar.addBindVar('value',channel,attrNmae)
        return bindVar
    else:
        raise myexceptions.ConfigException(f'Cant find channel {ch_id} in channelBase')

def bindChannelAttrName(channelBase, attrNmae:str)->channels.Vars:
    '''
    attrname:str - channel_id.attribute_mane 
    '''
    ch_id, attr = channels.parse_attr_params(attrNmae)
    return bindChannelAttr(channelBase, ch_id, attr)


if __name__ == '__main__':
    nodes=[  
            #{'id':4207,'moduleId':'ModuleA','type':'DI','sourceIndexList':[0,1],'handler':'func_1'},
            # {'id':4208,'moduleId':'ModuleB','type':'AI','sourceIndexList':[0]},
            {'id':4208,'moduleId':'test2','type':'DI','sourceIndexList':[0,1]},
            {'id':4209,'moduleId':'test3','type':'AI','sourceIndexList':[0]}
            ]
    import handlers
    prgs=[{'id':10001, 'handler':handlers.progvek, 'args':{'ch1':{'id':4208,'arg':'result'},'result':{'id':4209,'arg':'result_in'}}, 'stored':{'a':0}}]
    cb=channel_base_init(nodes, prgs) 
    print(cb)
    cb.get(4208).result=44
    cb.execute(10001)
    print(cb)
    cb.get(4208).result=50
    cb.execute(10001)
    print(cb)
    cb.executeAll()
    print(cb.channelsExecTime)
 