## Submitter
lca_graphic is the result of the collaboration of the experience of Florent Blondin, who spent 10 years on LCA datavizualisation  and the skills of Téo Lavisse, a PhD Student at the University of Grenoble and CEA.

## Description
This tool is designed to provide several **easy-to-understand graphics for everyday LCA practionners to quickly analyze** their LCA results in Brightway. 

The tool offers simple methods to display three dashboards :
1. to compare LCA results in different impact categories on the one hand,
2. to analyze the contributions of each activity in different impact categories on the other hand
3. to plot the variations of the contribution of the top processes (for the reference method) for each impact category to assess an potential impact transfer

The visualisations provided are direct or indirect outcomes from the scientific paper "Investigating Product Designer LCA Preferred Logics and Visualisations" Maud Rio, Florent Blondin, Peggy Zwolinski, Procedia CIRP, 2019, ISSN 2212-8271, https://doi.org/10.1016/j.procir.2019.04.293.
(https://www.sciencedirect.com/science/article/pii/S2212827119309412)

## Database(s) used
- [x] Used example data from the contest repository : US LCI
- [x] Used another database : Ecoinvent

## Links to the code and visualization

### Code

An example of the practical use of our tools can be found in the following [notebook]. Unfortunately, dashboards do not appear in the Github. Thus, the code should be executed on an Jupyter Notebook to see the dashboards for real.

[notebook]: https://github.com/teolvs/lca_graphic/blob/main/visualization_contest.ipynb


And the main functions are gathered in two python files : 
The [utils.py](https://github.com/teolvs/lca_graphic/blob/main/utils.py) file gives useful tool for quickly LCA computations and analyse of the contributions.
The [dashboards.py](https://github.com/teolvs/lca_graphic/blob/main/dashboards.py) provides the methods to gather all the results into three dashboards :
1. ```compare``` to compare LCA results in different impact categories on the one hand,
2. ```impact_transfer``` to plot the variations of the contribution of the top processes (for the reference method) for each impact category to identify the impact transfers,
3. ```hotspots``` to analyze the contributions of each activity in different impact categories on the other hand.
All these methods are generated all at once in the method ```lca_graphic```

### Visualizations
1. ```compare``` https://github.com/teolvs/lca_graphic/blob/main/outputs/compare.gif
2. ```impact_transfer``` https://github.com/teolvs/lca_graphic/blob/main/outputs/impact_transfer.gif
3. ```hotspots``` https://github.com/teolvs/lca_graphic/blob/main/outputs/hotspots.gif.


### Presentation video
https://youtu.be/nhVetFpbGFY


## License
You can find lists of Open Source licenses at [https://opensource.org/licenses/category](https://opensource.org/licenses/category).
You can write here either the _full name_ of the license, or the unique identifier from: [https://spdx.org/licenses/](https://spdx.org/licenses/).
Make sure that the one you specify here is the one you added to the source code.
