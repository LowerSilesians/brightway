from bw_visualization.sankertainpy import plot

import bw2data as bd
import bw2io as bi
bd.projects.set_current("graphics-fixture")
bi.useeio11()

eidb = bd.Database('USEEIO-1.1').random({"name": "Cutlery and handtools; at manufacturer",
                                         'code': '1fb0a77a-d49c-3557-810c-a4db0e73bab6'})
method = bd.methods.random()
result = plot(eidb, method)
result.show()

