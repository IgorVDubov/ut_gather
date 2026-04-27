import collections
import datetime


def bits_to_word(vars):
    """
    bits to 2 byte
    vars:
        b1..b32:bool
    """
    result = 0
    for i, bit in enumerate(
        [
            vars.b1,
            vars.b2,
            vars.b3,
            vars.b4,
            vars.b5,
            vars.b6,
            vars.b7,
            vars.b8,
            vars.b9,
            vars.b10,
            vars.b11,
            vars.b12,
            vars.b13,
            vars.b14,
            vars.b15,
            vars.b16,
            vars.b17 if hasattr(vars, "b17") else 0,
            vars.b18 if hasattr(vars, "b18") else 0,
            vars.b19 if hasattr(vars, "b19") else 0,
            vars.b20 if hasattr(vars, "b20") else 0,
            vars.b21 if hasattr(vars, "b21") else 0,
            vars.b22 if hasattr(vars, "b22") else 0,
            vars.b23 if hasattr(vars, "b23") else 0,
            vars.b24 if hasattr(vars, "b24") else 0,
            vars.b25 if hasattr(vars, "b25") else 0,
            vars.b26 if hasattr(vars, "b26") else 0,
            vars.b27 if hasattr(vars, "b27") else 0,
            vars.b28 if hasattr(vars, "b28") else 0,
            vars.b29 if hasattr(vars, "b29") else 0,
            vars.b30 if hasattr(vars, "b30") else 0,
            vars.b31 if hasattr(vars, "b31") else 0,
            vars.b32 if hasattr(vars, "b32") else 0,
        ]
    ):
        result += bit * 2**i
    vars.result = result


def bits_to_list(vars):
    """
    bits to 2 byte
    vars:
        b1..b32:bool
    """
    vars.result = [
        vars.b1,
        vars.b2,
        vars.b3,
        vars.b4,
        vars.b5,
        vars.b6,
        vars.b7,
        vars.b8,
        vars.b9,
        vars.b10,
        vars.b11,
        vars.b12,
        vars.b13,
        vars.b14,
        vars.b15,
        vars.b16,
    ]


def middle(vars):
    """
    бегущее среднее из MAX_VALUES значений
    STORED
        deque
    """
    if vars.resultIn == None:
        vars.resultIn = 0
    if not vars.deque:
        vars.deque = collections.deque(
            [vars.resultIn for r in range(vars.MAX_VALUES)], vars.MAX_VALUES
        )

    vars.deque.append(vars.resultIn)
    vars.resultOut = sum(vars.deque) / vars.MAX_VALUES


def mult(vars):
    """
    multiplicator
    arg.output = arg.input * arg.k
    """
    if vars.input is not None:
        if isinstance(vars.input, list):
            input = vars.input[0]
        else:
            input = vars.input
        vars.output = input * vars.k


def current_second(vars):
    """
    return current second
    """
    vars.result = datetime.datetime.now().second
