# Database explorer

## Description
Database explorer is a toolbox designed to help explore and analyze the content of a database on a given topic.

This toolbox includes functions to:
- explore the datasets contained into a database
- analyze the difference between those datasets in terms of inventories and impacts
- do some contribution analysis in terms of substances and processes (however, we lose the tree representation on these graphs)
- get an interactive dashboard to analyze the impact chain of an activity. You then get sunburst representations of respectively positive and negative impacts. Those positive and negative impacts are also represented on a waterfall. Finally, you also have an interactive sankey diagram.

## How to use it
```python
from bw_visualization.database_explorer import plot

import bw2data as bd
import bw2io as bi

bd.projects.set_current("E3_database_bw25")
eidb = bd.Database('US EEIO 1.1')

methods = list(set(method for method in bd.methods))[0: 3]

acts = [act for i, act in enumerate(eidb) if 'location' in act and i < 2]

plot(eidb, acts, methods, 0.02)
```

## Visualization

You can find below some data visualization realized with the dbex toolbox.

A graph for a simple comparison of carbon footprint:

![image info](sample_pictures/carbon_footprints_comparison.png)

A graph for a multi criteria LCA comparison:

![image info](sample_pictures/multi_lca_comparison.png)

A graph for contribution analysis by substances and processes:

![image info](sample_pictures/contribution_analysis_example.png)

And finally, an amazing interactive dashboard!!

![image info](sample_pictures/dashboard.png)

The dashboard function is taking a very very long time to run due the adapted GraphTraversal function that should not take that long. So there is a huge potential to improve the calculation and also the features of the visualization!

## Reference
[https://github.com/RomainBes/DataVizChallenge](https://github.com/RomainBes/DataVizChallenge)
