# lca_graphic

## Description
This tool is designed to provide several easy-to-understand graphics for everyday LCA practionners to quickly analyze their LCA results in Brightway. 

The [utils.py](https://github.com/teolvs/lca_graphic/blob/main/utils.py) file gives useful tool for quickly LCA computations and analyse of the contributions.
The [dashboards.py](https://github.com/teolvs/lca_graphic/blob/main/dashboards.py) provides the methods to gather all the results into three dashboards :
1. ```compare``` to compare LCA results in different impact categories on the one hand,
2. ```impact_transfer``` to plot the variations of the contribution of the top processes (for the reference method) for each impact category to identify the impact transfers,
3. ```hotspots``` to analyze the contributions of each activity in different impact categories on the other hand.

All these methods are generated all at once in the method ```lca_graphic```

The visualisations provided are direct or indirect outcomes from the scientific paper "Investigating Product Designer LCA Preferred Logics and Visualisations" Maud Rio, Florent Blondin, Peggy Zwolinski, Procedia CIRP, 2019, ISSN 2212-8271, https://doi.org/10.1016/j.procir.2019.04.293. (https://www.sciencedirect.com/science/article/pii/S2212827119309412)

## Installation
The library works with the open-source US EEIO database [US EEIO table](https://github.com/USEPA/USEEIO), and [available here (115MB download)](https://files.brightway.dev/visualization_example_data.zip). 

It works also with Ecoinvent database, and it could be updated for any database.

An example of the practical use of our tools can be found in the following [notebook]. Unfortunately, dashboards do not appear in the Github. Thus, the code should be executed on an Jupyter Notebook to see the dashboards for real. Brightway2.5 is required.

[notebook]: https://github.com/teolvs/lca_graphic/blob/main/visualization_contest.ipynb 


## Contribution
Do not hesitate to contribute to the improvements of this project to implement other features.

## License
[BSD 2-Clause "Simplified" License]

[BSD 2-Clause "Simplified" License]: https://github.com/teolvs/lca_graphic/blob/main/LICENSE.md
