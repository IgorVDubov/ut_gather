from typing import TypedDict


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
