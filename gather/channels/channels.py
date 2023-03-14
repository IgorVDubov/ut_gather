from abc import abstractmethod
from typing import Any, List, Type
import schedule

from .. import consts 
from .vars import Vars
from .. import myexceptions


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )
    cls.__str__ = __str__
    return cls



def get_deep_attr_value(obj:Type, attr:str):
    '''
    return  instance subobjects attributes value
    obj - class instance
    attr - attributes: example get_deep_attr_value(a, 'vars.b') if vars is instance with attr 'b' returns a.vars.b value
    '''
    s=''
    for i in range(0,len(attr)):
        if attr[i]=='.':
            result=getattr(obj,s)
            s=''
            obj=result
            continue
        s+=attr[i]
    try:
        return getattr(obj,s)
    except AttributeError:          #или raise выше ???
        return None

def get_subobject_attr(obj:Type, attr:str):
    '''
    return  subobjects instance and  attribute name for getattr
    obj - class instance
    attr - attributes: example 'a', 'vars.b' if vars instance of Var with attr 'b'
    return (subobj:Type, name:str)
    example: get_subobject_attr(someObj,'vars.b') returns (vars_instance,'b')
    '''
    s=''
    for i in range(0,len(attr)):
        if attr[i]=='.':
            result=getattr(obj,s)
            s=''
            obj=result
            continue
        s+=attr[i]
    return obj,s

def parse_attr_params(attrParam):
    '''
    parse attribute Params\n
    return cahnnel_id, attribute\n
    get Number return None, Value\n
    get str'channelID' return channelID:int , None\n
    get str'channelID.atrName' return channelID:int , 'atrName':str\n
    get str'channelID.atrName.var' return channelID:int , 'atrName.var':str'n
    get str'atrName.var' return 'self' , 'atrName.var':str'n
    '''
    if isinstance(attrParam, str):                                     #аттрибут - связь 
        s=''
        i=0
        for i in range(0,len(attrParam)):
            if attrParam[i]=='.':
                break
        if i==len(attrParam)-1:
            first=attrParam
        else:
            first=attrParam[:i+(1 if len(attrParam)==1 else 0)]
        other=attrParam[i+1:]
        try:
            BindChannelId=int(first)
            if not other:
                attr=None
            else:
                attr=other
        except ValueError:
            BindChannelId='self'
            #attr=attrParam
            attr=other
        # print(f'{attrParam=}: {BindChannelId=},{attr=}')
        if attr == None:      # channelBinding
            return BindChannelId, None
        else:                # channel attr Binding
            return BindChannelId, attr
    elif not(attrParam) or isinstance(attrParam, (int, float, bool, type(None))):   #аттрибут - число или None
        return None, attrParam

class Channel(object):
    channelType='channel'
    id=None
    result=None
    dost=None
    error=None
    handler:callable=None
    args:Vars=None
    type=None

    def __init__(self, id, args:Vars=None) -> None:
        self.id=id
        self.args=args
    @abstractmethod
    def __call__(self) -> Any: ...
    def toDict(self):...
    def toDictFull(self):
        return self.toDict()

    def __str__(self):
        return f' Channel: id:{self.id}' + f'\n  args:\n{self.args}' if self.args else ''
    
    def addArg(self, name, value=None):
        self.add_arg(name, value)
    
    def add_arg(self, name, value=None):
        if not self.args:
            self.args=Vars()
        self.args.addVar(name, value)
    
    def get_arg(self, arg:str):
        return get_deep_attr_value(self, arg)
    
    def bindArg(self, name:str, channel:Type, argName:str):
        self.args.addBindVar(name, channel, argName)

    def bindChannel2Arg(self, name:str, channel:Type):
        self.args.bindObject2Attr(name, channel)

    def addBindArg(self, name:str, channel:Type, argName:str):
        if not self.args:
            self.args=Vars()
        obj=self if channel==None else channel
        if argName!=None:
            self.args.addBindVar(name, obj, argName)
        else:
            self.args.bindObject(name, obj)
    
    def set_arg(self, arg_name, value):
        if arg_name[0:1]=='.':
            arg_name=arg_name[1:]
        if arg_name[:5]=='args.':
            self.args.__setattr__(arg_name[5:], value)  
        else:
            self.__setattr__(arg_name,value)

    def set_channel_arg_name(self, ch_arg_name, value):
        ch_id, attr_name = parse_attr_params(ch_arg_name)
        self.set_arg(attr_name, value)
        
    def toDictFull(self):
        return self.toDict()

    def toDict(self):
        if self.args:
            return { 
                    'channelType':self.channelType,
                    'id':self.id,
                    'args':self.args.toDict()}
        else:
            return { 'type':self.type, 'id':self.id}

class DBQuie(Channel):
    def __init__(self, id, dbQuie, args: Vars = None) -> None:
        self.dbQuie=dbQuie
        super().__init__(id, args)
    def __str__(self):
        return f'DBQuieChannel: id:{self.id}, quie length: {self.dbQuie.qsize()} '
   
    def put(self, data):
        self.dbQuie.put_nowait(data)
# class Message(Channel):
#     def __init__(self, id, args: Vars = None) -> None:
#         super().__init__(id, args)
#     def __str__(self):
#         return f'Message: id:{self.id}, result: {self.reuslt} '
   
#     def put(self, data):
#         self.dbQuie.put_nowait(data)

class DBConnector(Channel):
    def __init__(self, id, dbQuie, handler:callable, args: Vars = None) -> None:
        if handler==None:
            raise myexceptions.ConfigException(f'No handler at channel {id} params')
        self.handler=handler
        super().__init__(id, args)
        if args !=None:
            self.args.addVar(dbQuie)
    
    def execute(self):
        self.handler(self.args)

class Node(Channel):
    channelType='node'
    def __init__(self,id:int,moduleId:str, type:str, sourceIndexList:List, handler:callable=None, args:Vars=None) -> None:
        self.id=id
        self.sourceId=moduleId
        self.type=type
        self.sourceIndexList=sourceIndexList
        self.source=None
        self.result_in=None
        self.result=None # данные после обработки handler
        self.handler=handler
        self.args=args

    def __str__(self):
        return f"Node: id:{self.id}, source:{self.source.id if self.source  else None}, source Id:{id(self.source)}, handler:{self.handler}, {self.result=},"  + (f'\n  args:\n{self.args}' if self.args else '')

    def toDictFull(self):
        result= { 
                'channelType':self.channelType,
                'id':self.id,
                'sourceId':self.sourceId,
                'type':self.type,
                'sourceIndexList':self.sourceIndexList,
                'source':self.source,
                'result_in':self.result_in,
                'result':self.result}
        if self.handler:
            result.update({'handler':self.handler.__name__})
        if self.args:
            result.update({'args':self.args.toDict()})
        return result
    
    def toDict(self):
        return {    'channelType':self.channelType,
                    'id':self.id,
                    'result':self.result}

    def __call__(self):
        if self.source:
            if self.source.result:
                if self.source.format==consts.DI:
                    self.result_in=[self.source.result[i] for i in self.sourceIndexList]
                elif self.source.format==consts.AI:
                    self.result_in=self.source.result[0]                                 # только 1-й элемент....  уточнить!!!!!!!!!!!!!!!!!!!!!!
            else:
                print(f'No result in channel {self.id} source {self.source}')
            # print(f'result in channel {self.id} = {self.source.result}')
        if self.handler:
            self.handler(self.args)    
        else:
            self.result=self.result_in
        # else:
            # print (f'no source init for node id:{self.id}')
            # return
    
class Programm(Channel):
    channelType='programm'
    def __init__(self,id:int,handler:callable, args:Vars=None) -> None:
        self.id=id
        self.args=args
        self.handler=handler
    
    def __call__(self):
        try:
            self.handler(self.args)
        except Exception as e:
            raise myexceptions.ProgrammException(f'Exc in channel {self.id} handler:{self.handler.__name__} raise {e}')
    
    def toDictFull(self):
        return self.toDict()

    def toDict(self):
        result= { 'channelType':self.channelType,
                'id':self.id,
                'handler':self.handler.__name__}
        if self.args:
            result.update({'args':self.args.toDict()})
        return result
    
    def exec(self):
        return self.__call__()

    def __str__(self):
        return f'Programm id:{self.id}, handler:{self.handler}'+ f'\n  args:\n{self.args}' if self.args else ''

class Scheduler(Channel):
    channelType='scheduler'
    def __init__(self, id:int, time_list, handler:callable, args:Vars=None) -> None:
        self.id=id
        self.handler=handler
        self.time_list=time_list
        self.scheduller=schedule.Scheduler()
        
    def init_args(self):
        for t in self.time_list:
            self.scheduller.every().day.at(t).do(self.handler, self.args)

    def __call__(self):
        try:
            self.scheduller.run_pending()
        except Exception as e:
            raise myexceptions.ProgrammException(f'Exc in channel {self.id} handler:{self.handler.__name__} raise {e}')
    
    def toDictFull(self):
        return self.toDict()

    def toDict(self):
        result= { 'channelType':self.channelType,
                'id':self.id,
                'handler':self.handler.__name__}
        if self.args:
            result.update({'args':self.args.toDict()})
        return result
    
    def exec(self):
        return self.__call__()

    def __str__(self):
        return f'Programm id:{self.id}, handler:{self.handler}'+ f'\n  args:\n{self.args}' if self.args else ''

CHANNELS_CLASSES={  'channels':'channels.Channel',           # соответствие имени класса для корректной привязки в аргументах Vars 
                    'nodes':'channels.Node', 
                    'programms':'channels.Programm', 
                    'dbquie':'channels.DBQuie',  
                    'scheduler':'channels.Scheduler',
                    # 'dbconnector':'channels.DBConnector',
                    # 'message':'channels.message',
                } 

def testVars():
    print('Test Vars class:')
    Cl=type('Cl',(),{'a':44})
    c=Cl()
    v=Vars()
    v.addVar('a',55)
    print('add attr a = 55')
    print(v)
    print('add binding to inst c <-> attr a , c.a= 44')
    v.addBindVar('a',c,'a')
    print (f'{v.a=}')
    print(v)
    print('change value of bind attr v.a to 500')
    v.a=500
    print(f'{c.a=}')
    assert(c.a==500)
    v.addVar('obj')
    # v.obj=c
    v.bindObject2Attr('obj',c)
    print(v)
    v.obj.a=65438
    print(f'{c.a=}')


def moduleTests():
    testVars()

if __name__ == '__main__':
    testVars()