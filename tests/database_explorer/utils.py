import bw2data as bd
import bw2calc as bc
# import bw2io as bi

from ..conftest import restore_database_useeio


def sample_1():
    restore_database_useeio()
    eidb = bd.Database('US EEIO 1.1')

    methods = [method for method in bd.methods][0: 2]

    acts = []
    i = 0
    for act in eidb:
        if 'location' in act:
            acts.append(act)
            i += 1
        if i == 2:
            break

    lca = bc.LCA({acts[0]: 1}, methods[0])
    lca.lci()
    lca.lcia()

    return acts, methods, eidb, lca
