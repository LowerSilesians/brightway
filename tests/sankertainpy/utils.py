import bw2data as bd
from ..conftest import restore_database


# TBD: This should be a pytest fixture

def sample_1():
    restore_database()
    act = bd.get_node(name="Cutlery and handtools; at manufacturer")
    method = bd.methods.random()
    return act, method
