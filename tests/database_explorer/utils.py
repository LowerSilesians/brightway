import bw2data as bd
import bw2calc as bc
import bw2io as bi

from ..conftest import restore_database_ecoinvent


def sample_1():
    restore_database_ecoinvent()
    print(bd.databases)
    eidb = bd.Database('ecoInvent 3.8')

    # Default impact categories
    methods_EF = [
        m
        for m in bd.methods
        if "EF v3.0 EN15804" in str(m)
        and not "no LT" in str(m)
        and not "obsolete" in str(m)
    ]
    methods_CC = [m for m in methods_EF if "climate" in str(m)]
    act = bd.get_node(name="biomethane production, high pressure from synthetic gas, wood, fluidised technology")
    method = ('IPCC 2013', 'climate change', 'GWP 100a')
    lca = bc.LCA({act: 1}, method = method)
    lca.lci()
    lca.lcia()

    return lca, act, methods_EF, methods_CC, eidb
