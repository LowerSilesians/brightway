import bw2data as bd
from ..conftest import restore_database_useeio


def sample_1():
    restore_database_useeio()
    methods = list(bd.methods)

    window_metal = bd.get_node(name="Metal windows, doors, and architectural products; at manufacturer")
    window_wood = bd.get_node(name="Wooden windows, door, and flooring; at manufacturer")

    fu = {window_metal: 1, window_wood: 1}

    impact_categories = [methods[0], methods[3], methods[4], methods[6]]

    return fu, impact_categories, impact_categories[0]
