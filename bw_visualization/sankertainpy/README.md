# sankertainpy

### Visualize uncertainty with sankey diagrams.


This is a python package written for the depart de sentier [Sustainability assessment visualization contest](https://github.com/Depart-de-Sentier/visualization-contest-2022) to visualize brightway2 Monte Carlo LCA results with [plotly sankey diagrams](https://plotly.com/python/sankey-diagram/). sankertainpy is using an adjusted version of the [bw2analyzer function "recursive_calculation_to_object()"](https://github.com/brightway-lca/brightway2-analyzer/blob/main/bw2analyzer/utils.py) to generate the plotly compatible graph traversal LCA data. With the function generate_sankey(), direct emission impact can be calculated, flows smaller than the cutoff value are bundled to single nodes, and the uncertainty visualisation is generated. It is tested with brightway2 and ecoinvent 3.8 cut-off.  

![example_image](/images/example_diagram.png)

## Getting started:

Clone the repository and start:


```python
import bw2data as bd
from bw_to_plotly import recursive_calculation_to_plotly
import sankertainpy as sc

activity= bd.Database('database name').random()
method= bd.methods.random()

result = recursive_calculation_to_plotly(activity,method)

fig= sp.generate_sankey(result, type=1)

fig.show()
```
Note: depending on the number of monte carlo iterations and the level depth, the calculation can take some time!

## Background:

Inspired by the paper *"Visualization approaches for understanding uncertainty in flow diagrams"* from Vosough et al (2019):
https://doi.org/10.1016/j.cola.2019.03.002




