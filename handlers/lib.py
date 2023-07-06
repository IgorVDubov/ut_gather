import collections


def bits_to_word(vars):
    '''
    bits to 2 byte 
    vars:
        b1..b32:bool
    '''
    result=0
    for i,bit in enumerate( [vars.b1, vars.b2, vars.b3, vars.b4, vars.b5, vars.b6, vars.b7, vars.b8, vars.b9, vars.b10,
                            vars.b11, vars.b12, vars.b13, vars.b14, vars.b15, vars.b16] ):
        result+=bit*2**i
    vars.result=result

def middle(vars):
    '''
    бегущее среднее из MAX_VALUES значений
    STORED
        deque
    '''
    if vars.resultIn==None:
        vars.resultIn=0
    if not vars.deque:
        vars.deque=collections.deque([vars.resultIn for r in range(vars.MAX_VALUES)],vars.MAX_VALUES)
        
    vars.deque.append(vars.resultIn)
    vars.resultOut=sum(vars.deque)/vars.MAX_VALUES
    
def mult(vars):
    '''
    multiplicator
    arg.output = arg.input * arg.k
    '''
    if vars.input is not None:
        if isinstance(vars.input, list):
            input=vars.input[0]
        else:
            input=vars.input
        vars.output = input * vars.k