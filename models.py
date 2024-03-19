from typing import TypedDict
from dataclasses import dataclass
from datetime import datetime


class User(TypedDict):
    id: int
    name: str
    m_name: str
    s_name: str
    login: str
    password: str


class Operator(TypedDict):
    operator_id: int
    machine_id: str
    login: str
    logout: str
    
class CurrentStateProtocol(TypedDict):
    machine: int
    state: int | None
    begin_time: str | None  # formatted to YYYY-MM-DDTHH:mm:ss
    cause_id: int | None
    cause_time: str | None  # formatted to YYYY-MM-DDTHH:mm:ss
    cause_set_time: str | None  # formatted to YYYY-MM-DDTHH:mm:ss

@dataclass
class Idle():
    state: int                         # текущее состояние
    tech_idle: int                     # техпростой, сек
    begin_time: datetime | None               # начало текущего состояния
    operator: int | None               # оператор id
    cause: int | None                  # id причина простоя
    # начало действия причины (может быть не равно begin_time если сменв причины без смены состояния)
    cause_time: datetime | None
    cause_set_time: datetime | None    # время установки причины
    length: int | None                 # длительность нахождения в текущей причине простоя

@dataclass
class TempIdle():
    machine_id: int
    state: int                         # текущее состояние
    tech_idle: int                     # техпростой, сек
    begin_time: datetime | None               # начало текущего состояния
    operator_id: int | None               # оператор id
    cause_id: int | None                  # id причина простоя
    cause_time: datetime | None
    cause_set_time: datetime | None    # время установки причины
    length: int | None                 # длительность нахождения в текущей причине простоя


class M_Idles(TypedDict):
    machine_id: int
    idle: Idle
