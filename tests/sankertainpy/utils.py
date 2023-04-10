import bw2data as bd
import bw2io as bi
import bw2calc as bc


def sample_1():
    bd.projects.set_current('sankertainpy-test')
    bi.useeio11()

    act = bd.Database('USEEIO-1.1').random({"name": "Cutlery and handtools; at manufacturer",
                                            'code': '1fb0a77a-d49c-3557-810c-a4db0e73bab6'})
    method = bd.methods.random()

    return act, method
