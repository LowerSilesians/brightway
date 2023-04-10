import bw2data as bd
import bw2io as bi
import bw2calc as bc


def sample_1():
    bd.projects.set_current('database-explorer-test')
    bi.useeio11()

    eidb = bd.Database('USEEIO-1.1')
    methods = list(bd.methods)

    methods_EF = methods
    methods_CC = methods
    acts = [act for act in eidb if act['type']=='process' and act['name']=='Funds, trusts, and financial vehicles']
    act = acts[0]
    lca = bc.LCA({act: 1}, methods[0])
    lca.lci()

    return lca, act, methods_EF, methods_CC, eidb
