import bw2data as bd
import bw2calc as bc
from ..conftest import restore_database


# TBD: This should be a pytest fixture

def sample_1():
    restore_database()
    eidb = bd.Database('USEEIO-1.1-noproducts')
    methods = list(bd.methods)

    methods_EF = methods
    methods_CC = methods
    acts = [act for act in eidb if act['type']=='process' and act['name']=='Funds, trusts, and financial vehicles']
    act = acts[0]
    lca = bc.LCA({act: 1}, methods[0])
    lca.lci()

    return lca, act, methods_EF, methods_CC, eidb
