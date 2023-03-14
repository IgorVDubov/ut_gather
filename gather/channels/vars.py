import inspect
from typing import Type

from .. import myexceptions


class Vars:
    '''
    Binds dynamic added self instsnce attribute to another instance attribute
    can bins subobject attr in format 'instance_attr.a'
    '''

    def __init__(self):
        self.__class__=type(self.__class__.__name__,(self.__class__,), {})
        self.vars=[]

    def __str__(self):
        s=''
        for i, (name, obj, objAttrName, parent) in enumerate(self.vars):
            s+=f'    {name}'+(f'<-->{parent.id if hasattr(parent,"id") else parent}.{objAttrName}' if obj else '')+f'={getattr(self,name)}'
            if i < len(self.vars)-1 :
                s+='\n'
        return s
    
    # def __repr__(self):
    #     return self.__str__()

    # def add(self,name:str, obj:type, objAttrName:str):
    #     return self._add(name, obj, objAttrName)
    @staticmethod
    def _getSubObjectAttr(obj:Type, attr:str):
        '''
        return  subobjects instance and  attribute name for getattr
        obj - class instance
        attr - attributes: example 'a', 'vars.b' if vars instance of Var with attr 'b'
        return (subobj:Type, name:str)
        example: getSubObjectAttr(someObj,'vars.b') returns (vars_instance,'b')
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

    def _add(self, name:str, obj:Type, objAttrName:str):
    # def add(self, name:str, obj:Type, objAttrName:str, readonly=False):
        '''
        adds self attribute (name) bindig to instance (obj) attribute  (objAttrName)
        '''
        if obj !=None:
            parent=obj
            obj, objAttrName=self._getSubObjectAttr(obj, objAttrName)
        if not ((inspect.isclass(type(obj)) and not type(obj) == type )
                and isinstance( objAttrName, str) 
                and isinstance( name, str)):
            raise myexceptions.ConfigException(f'Wrong argument type adding binding, args: {name=}, {obj=}, {objAttrName=}')
        if not hasattr(obj, objAttrName):
            raise myexceptions.ConfigException(f'Instance {obj}  has no attribute {objAttrName}')

        fget = lambda self: self._getProperty( name )
        fset = lambda self, value: self._setProperty( name, value )
        
        setattr( self, '_' + name, getattr(obj,objAttrName) )
        setattr( self.__class__, name, property( fget = fget, fset = fset ) )
        # setattr( self, name, property( fget = fget, fset = fset ) )
        try:
            if found:=next(filter(lambda var: var[0] == name, self.vars)):
                attrName, _obj, _objAttr, _parent = found
                self.vars.remove(found)
                self.vars.append((attrName, obj, objAttrName, parent))
                return 
        except StopIteration:
            pass
        self.vars.append((name, obj, objAttrName, parent))

    def bindVar(self, name:str, obj:Type, objAttrName:str):
        '''
        adds self attribute (name) bindig to instance (obj) attribute  (objAttrName)
        '''
        self._add(name, obj, objAttrName)
    

    def addBindVar(self, name:str, obj:Type, objAttrName:str):
        '''
        adds self attribute (name) bindig to instance (obj) attribute  (objAttrName)
        '''
        self._add(name, obj, objAttrName)

    def bindObject2Attr(self, name:str, obj:Type):
        '''
        adds arg binding to inctance
        name - argumrnt namr
        obj - binding instance
        '''
        
        setattr( self, '_' + name, obj )
        try:
            if found:=next(filter(lambda var: var[0] == name, self.vars)):
                attrName, _obj, _objAttr, _parent = found
                self.vars.remove(found)
                self.vars.append((attrName, obj, None, obj))
                return 
        except StopIteration:
            pass
        self.vars.append((name, obj, None, obj))

    def addVar(self, name, defaultValue=None):
        '''
        adds attribute to instance NO BINDING
        name:str  attribute name
        [defaultValue]:Any   default Value
        '''
        if not isinstance( name, str):
            raise myexceptions.ConfigException(f'Wrong argument type adding arg: {name=}')
        fget = lambda self: self._getAttrProperty( name )
        fset = lambda self, value: self._setAttrProperty( name, value )
        
        setattr( self, '_' + name, defaultValue)
        setattr( self.__class__, name, property( fget = fget, fset = fset ) )
        self.vars.append((name, None, None, None))
        
    def toDict(self):
        result=dict()
        for name, obj, attr, parent in self.vars:
            result.update({name:getattr(self,name)})
        return result
   
    def _getBinding(self, name):
        try:
            
            if found:=next(filter(lambda var: var[0] == name, self.vars)):
                attrName, obj, objAttr, parent = found
                # return found.obj, found.objAttrName, found.readonly
                return obj, objAttr
        except StopIteration:
            found=None
        return None, None
        # return None, None, None

    def _setAttrProperty( self, name, value ):
        setattr( self, '_' + name, value )
    
    def _getAttrProperty( self, name ):
        return getattr( self, '_' + name )

    def _setProperty( self, name, value ):
        setattr( self, '_' + name, value )
        obj, objAttrName= self._getBinding(name)
        setattr( obj, objAttrName, value )
        # obj, objAttrName, readonly= self._getBinding(name)
        # if not readonly:
        #     setattr( obj, objAttrName, value )

    def _getProperty( self, name ):
        obj, objAttrName= self._getBinding(name)
        # return getattr( self, '_' + name )
        return getattr( obj, objAttrName )
