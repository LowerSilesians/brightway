import bw2data as bd
import bw2calc as bc
from ..conftest import restore_database


def sample_1():
    restore_database()
    eidb = bd.Database('USEEIO-1.1-noproducts')
    methods = list(bd.methods)

    methods_EF = methods
    methods_CC = methods
    act = bd.get_node(name="Funds, trusts, and financial vehicles")
    lca = bc.LCA({act: 1}, methods[0])
    lca.lci()

    return lca, act, methods_EF, methods_CC, eidb
