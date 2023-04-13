import bw2data as bd
from ..conftest import restore_database


# TBD: This should be a pytest fixture

def sample_1():
    restore_database()
    eidb = bd.Database('USEEIO-1.1-noproducts')

    methods = list(bd.methods)

    window_metal = [node for node in eidb if node['type'] == 'product' if node['name']
                    == "Metal windows, doors, and architectural products; at manufacturer"][0]
    window_wood = [node for node in eidb if node['type'] == 'product' if node['name']
                   == "Wooden windows, door, and flooring; at manufacturer"][0]

    fu={window_metal: 1, window_wood: 1}

    impact_categories = [methods[0], methods[3], methods[4], methods[6]]

    return fu, impact_categories, impact_categories[0]
