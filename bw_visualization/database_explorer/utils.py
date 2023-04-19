# modified version of the AssumeDiagonalGraphTraversal.
# includes separate calculation of positive and negative impact
import warnings
import math

from heapq import heappop, heappush
import numpy as np
import pandas as pd
from bw2calc import spsolve
import bw2data as bd
import plotly.graph_objects as go
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc


class JRCAssumedDiagonalGraphTraversal:
    """
    Traverse a supply chain, following paths of greatest impact. This implementation uses a queue of datasets to
    assess. As the supply chain is traversed, datasets inputs are added to a list sorted by LCA score. Each activity
    in the sorted list is assessed, and added to the supply chain graph, as long as its impact is above a certain
    threshold, and the maximum number of calculations has not been exceeded. Because the next dataset assessed is
    chosen by its impact, not its position in the graph, this is neither a breadth-first nor a depth-first search,
    but rather "importance-first". This class is written in a functional style - no variables are stored in *self*,
    only methods. Should be used by calling the ``calculate`` method.

    .. warning:: Graph traversal with multioutput
    processes only works when other inputs are substituted (see `Multioutput processes in LCA
    <http://chris.mutel.org/multioutput.html>`__ for a description of multioutput process math in LCA).
    """

    def calculate(self, lca, cutoff=0.005, max_calc=1e5, skip_coproducts=False):
        """Traverse the supply chain graph.

        Parameters
        ----------
        lca : dict
            An instance of ``bw2calc.lca.LCA``.
        cutoff : float (default=0.005)
            Cutoff criteria to stop LCA calculations. Relative score of total, i.e. 0.005 will cutoff if
            a dataset has a score less than 0.5 percent of the total.
        max_calc : int (default=10000)
            Maximum number of LCA calculations to perform.

        Returns
        -------
        dict
            Dictionary of nodes, edges, and number of LCA calculations.
        """
        if not hasattr(lca, "supply_array"):
            lca.lci()
        if not hasattr(lca, "characterized_inventory"):
            lca.lcia()

        supply = lca.supply_array.copy()
        score = lca.score

        if score == 0:
            raise ValueError("Zero total LCA score makes traversal impossible")

        # Create matrix of LCIA CFs times biosphere flows, as these don't
        # change. This is also the unit score of each activity.
        characterized_biosphere = np.array(
            (lca.characterization_matrix * lca.biosphere_matrix).sum(axis=0)
        ).ravel()
        characterized_biosphere_neg = characterized_biosphere.copy()
        characterized_biosphere_neg[characterized_biosphere_neg > 0] = 0
        characterized_biosphere_pos = characterized_biosphere.copy()
        characterized_biosphere_pos[characterized_biosphere_pos < 0] = 0

        heap, nodes, edges = self.initialize_heap(
            lca,
            supply,
            characterized_biosphere,
            characterized_biosphere_neg,
            characterized_biosphere_pos,
        )
        nodes, edges, counter = self.traverse(
            heap,
            nodes,
            edges,
            0,
            max_calc,
            cutoff,
            score,
            supply,
            characterized_biosphere,
            characterized_biosphere_neg,
            characterized_biosphere_pos,
            lca,
            skip_coproducts,
        )

        return {
            "nodes": nodes,
            "edges": edges,
            "counter": counter,
        }

    def initialize_heap(
        self,
        lca,
        supply,
        characterized_biosphere,
        characterized_biosphere_neg,
        characterized_biosphere_pos,
    ):
        """Create a `priority queue <http://docs.python.org/2/library/heapq.html>`_ or ``heap`` to store inventory
        datasets, sorted by LCA score. Populates the heap with each activity in ``demand``. Initial nodes are the
        *functional unit*, i.e. the complete demand, and each activity in the *functional unit*. Initial edges are
        inputs from each activity into the *functional unit*. The *functional unit* is an abstract dataset (as it
        doesn't exist in the matrix), and is assigned the index ``-1``.
        """
        heap, edges = [], []
        nodes = {-1: {"amount": 1, "cum": lca.score, "ind": 1e-6 * lca.score}}
        for index, amount in enumerate(lca.demand_array):
            if amount == 0:
                continue
            cum_score, cum_score_neg, cum_score_pos = self.cumulative_score(
                index,
                supply,
                characterized_biosphere,
                characterized_biosphere_neg,
                characterized_biosphere_pos,
                lca,
            )
            heappush(heap, (abs(1 / cum_score), index, str(index)))
            nodes[index] = {
                "amount": float(supply[index]),
                "cum": cum_score,
                "cum_neg": cum_score_neg,
                "cum_pos": cum_score_pos,
                "ind": self.unit_score(index, supply, characterized_biosphere),
            }
            edges.append(
                {
                    "to": -1,
                    "from": str(index),
                    "amount": amount,
                    "exc_amount": amount,
                    "impact": cum_score * amount / float(supply[index]),
                    "impact_neg": cum_score_neg * amount / float(supply[index]),
                    "impact_pos": cum_score_pos * amount / float(supply[index]),
                }
            )
        return heap, nodes, edges

    def cumulative_score(
        self,
        index,
        supply,
        characterized_biosphere,
        characterized_biosphere_neg,
        characterized_biosphere_pos,
        lca,
    ):
        """Compute cumulative LCA score for a given activity"""
        demand = np.zeros((supply.shape[0],))
        demand[index] = (
            supply[index]
            *
            # Normalize by the production amount
            lca.technosphere_matrix[index, index]
        )
        solved_tech = spsolve(lca.technosphere_matrix, demand)
        return (
            float((characterized_biosphere * solved_tech).sum()),
            float((characterized_biosphere_neg * solved_tech).sum()),
            float((characterized_biosphere_pos * solved_tech).sum()),
        )

    def unit_score(self, index, supply, characterized_biosphere):
        """Compute the LCA impact caused by the direct emissions and resource consumption of a given activity"""
        return float(characterized_biosphere[index] * supply[index])

    def traverse(
        self,
        heap,
        nodes,
        edges,
        counter,
        max_calc,
        cutoff,
        total_score,
        supply,
        characterized_biosphere,
        characterized_biosphere_neg,
        characterized_biosphere_pos,
        lca,
        skip_coproducts,
    ):
        """
        Build a directed graph by traversing the supply chain.
        Node ids are actually technosphere row/col indices, which makes lookup easier.

        Returns
        ----------
        tuple
            a tuple of (nodes, edges, number of calculations)
        """
        # static_databases = {name for name in databases if databases[name].get("static")}
        # reverse = lca.dicts.activity.reversed

        while heap:
            if counter >= max_calc:
                warnings.warn("Stopping traversal due to calculation count.")
                break
            parent = heappop(heap)
            parent_index = parent[1]
            full_path_parent = parent[2]
            # Skip links from static databases
            # if static_databases and reverse[parent_index][0] in static_databases:
            #     continue

            # Assume that this activity produces its reference product
            scale_value = lca.technosphere_matrix[parent_index, parent_index]
            if scale_value == 0:
                raise ValueError(
                    "Can't rescale activities that produce zero reference product"
                )
            col = lca.technosphere_matrix[:, parent_index].tocoo()
            # Multiply by -1 because technosphere values are negative
            # (consumption of inputs) and rescale
            children = [
                (int(col.row[i]), float(-1 * col.data[i] / scale_value))
                for i in range(col.row.shape[0])
            ]
            for activity, amount in children:
                # Skip values on technosphere diagonal
                if activity == parent_index:
                    continue
                # Skip negative coproducts
                if skip_coproducts and amount <= 0:
                    continue
                counter += 1
                full_path_id = full_path_parent + "-" + str(activity)
                cumulative_score, cum_score_neg, cum_score_pos = self.cumulative_score(
                    activity,
                    supply,
                    characterized_biosphere,
                    characterized_biosphere_neg,
                    characterized_biosphere_pos,
                    lca,
                )
                if abs(cumulative_score) < abs(total_score * cutoff):
                    continue

                # flow between activity and parent (Multiply by -1 because technosphere values are negative)
                flow = (
                    -1.0
                    * lca.technosphere_matrix[activity, parent_index]
                    * supply[parent_index]
                )
                total_activity_output = (
                    lca.technosphere_matrix[activity, activity] * supply[activity]
                )

                # Edge format is (to, from, mass amount, cumulative impact)
                edges.append(
                    {
                        "to": full_path_parent,
                        "from": full_path_id,
                        # "full_path_id": full_path_id,
                        # Amount of this link * amount of parent demanding link
                        "amount": flow,
                        # Raw exchange value
                        "exc_amount": amount,
                        # Impact related to this flow
                        "impact": flow / total_activity_output * cumulative_score,
                        "impact_neg": flow / total_activity_output * cum_score_neg,
                        "impact_pos": flow / total_activity_output * cum_score_pos,
                    }
                )
                # Want multiple incoming edges, but don't add existing node
                if activity in nodes:
                    continue
                nodes[activity] = {
                    # Total amount of this flow supplied
                    "amount": total_activity_output,
                    # Cumulative score from all flows of this activity
                    "cum": cumulative_score,
                    "cum_neg": cum_score_neg,
                    "cum_pos": cum_score_pos,
                    # Individual score attributable to environmental flows
                    # coming directory from or to this activity
                    "ind": self.unit_score(activity, supply, characterized_biosphere),
                }
                heappush(heap, (abs(1 / cumulative_score), activity, full_path_id))

        return nodes, edges, counter


def separate_multiple_parent(df):
    """Separate impacts from activities that have multiple parents to each branch"""
    # add some helpful columns
    df["act_id"] = df["ids"].apply(lambda x: x.split("-")[-1])
    df["parent_act_id"] = df["parent_ids"].apply(lambda x: x.split("-")[-1])
    df["depth"] = df["ids"].apply(lambda x: len(x.split("-")))
    df["scaled_pos_impact"] = df["impact_pos"]
    df["scaled_neg_impact"] = df["impact_neg"]

    # calculate the overall impact of activities with multiple parents
    # if the same id is found several times, the impacts will be summed
    grouped = df.groupby("act_id")
    multi_parent_pos_sum = grouped["impact_pos"].sum()
    multi_parent_neg_sum = grouped["impact_neg"].sum()
    # get only the activities that have multiple parents sorting by depth allows us to traverse this later in
    # ascending order (start with activities close to the functional unit). This might not be strictly neccessary
    multi_parents = pd.concat(g for _, g in grouped if len(g) > 1).sort_values(
        by="depth"
    )
    # and add the total impact
    multi_parents["impact_pos_sum"] = multi_parents["act_id"].apply(
        lambda x: multi_parent_pos_sum[x]
    )
    multi_parents["impact_neg_sum"] = multi_parents["act_id"].apply(
        lambda x: multi_parent_neg_sum[x]
    )

    # display(multi_parents)

    # apply a user defined scale here we cheat a bit by flooring the value because sometimes the sums of the children
    # are bigger than the parent there is definitely a better way to do this - the best would be to separate the
    # chains from the beginning in the GraphTraversal
    def apply_scale(number, scale):
        # return number * scale
        return math.floor(number * scale * 100) / 100

    # recursive function that scales all children to the share of this branch
    def scale_children(multi_parent_id, scale):
        child_rows = df.eval("parent_ids == @multi_parent_id")
        df.loc[child_rows, "scaled_pos_impact"] = df.loc[
            child_rows, "scaled_pos_impact"
        ].apply(lambda x: apply_scale(x, scale))
        # double negative to make floor work in the right way
        df.loc[child_rows, "scaled_neg_impact"] = df.loc[
            child_rows, "scaled_neg_impact"
        ].apply(lambda x: -apply_scale(-x, scale))
        # repeat for all children: children become new parents
        new_parents = df.loc[child_rows, "ids"]
        for new_parent in new_parents:
            scale_children(new_parent, scale)

    for parent, impact, impact_sum in zip(
            multi_parents["ids"],
            multi_parents["impact_pos"],
            multi_parents["impact_pos_sum"],
    ):
        # print(parent)
        scale_children(parent, impact / impact_sum)
    return df


def plot_sankey(df, unit):
    # Put the data in a Sankey format. Strangely it didn't work with ids, so we just put integers as ids.
    data_sankey = df.query('parent_ids != ""').to_dict(orient="list")
    nodes, numbers = [], {}
    counter = 0
    for id in data_sankey["ids"]:
        numbers[id] = counter
        nodes.append(data_sankey["label"][counter])
        counter += 1
    counter2 = 0
    for id in data_sankey["parent_ids"]:
        numbers[id] = counter
        nodes.append(data_sankey["parent"][counter2])
        counter += 1
        counter2 += 1

    links = dict(
        source=[numbers[id] for id in data_sankey["ids"]],
        target=[numbers[id] for id in data_sankey["parent_ids"]],
        value=data_sankey["impact"],
        hovertemplate="<b>%{source.label}</b> to <b>%{target.label}</b><br>Impact: %{value:.2} "
                      + unit,
    )
    # print(links, numbers, nodes)
    fig_sankey = go.Figure(
        data=[
            go.Sankey(
                link=links,
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=nodes,
                    color="blue",
                    hovertemplate="%{label}<br>Total impact: %{value:.2} " + unit,
                ),
                valueformat=".0f",
            )
        ]
    )
    fig_sankey.update_layout(
        title_text="Sankey Diagram of impact contributions", font_size=10, height=700
    )
    return fig_sankey


def plot_sunbursts(df, unit):
    data_sunburst = df  # .query('depth < 5')
    ids = list(data_sunburst["ids"])
    parents = list(data_sunburst["parent_ids"])
    labels = list(data_sunburst["label"])
    labels_short = [label[:18] for label in labels]
    values_pos = list(data_sunburst["scaled_pos_impact"])
    values_neg = list(-data_sunburst["scaled_neg_impact"])

    def create_sunburst(values, colorscale, title, valuesign):
        fig = go.Figure(
            go.Sunburst(
                # data,
                ids=ids,
                labels=labels_short,
                parents=parents,
                values=values,
                branchvalues="total",
                customdata=labels,
                # color='labels_short',
                marker=dict(colorscale=colorscale),
                # color_continuous_scale='algae',
                hovertemplate="<b>%{customdata} </b> <br> Impact: "
                              + valuesign
                              + "%{value:.2} "
                              + unit
                              + "<br> %{percentParent:.2%} of %{parent}",
                # maxdepth=2
            )
        )
        fig.update_layout(
            title=title,
            autosize=True,
            margin=dict(t=0, b=0, l=0, r=0),
            coloraxis=None,
            height=700,
        )
        return fig

    fig_sunburst_pos = create_sunburst(values_pos, "Burg", "Emissions", "")
    fig_sunburst_neg = create_sunburst(values_neg, "algae", "Absorptions", "-")
    return fig_sunburst_pos, fig_sunburst_neg


def plot_waterfall(trav, unit):
    main_edge = trav["edges"][0]
    fig_waterfall = go.Figure(
        go.Waterfall(
            orientation="v",
            measure=["relative", "relative", "total"],
            x=["Emissions", "Absorptions", "Total"],
            y=[main_edge["impact_pos"], main_edge["impact_neg"], main_edge["impact"]],
            decreasing={"marker": {"color": "aquamarine"}},
            increasing={"marker": {"color": "lightcoral"}},
        )
    )
    fig_waterfall.update_layout(title="Overall life cycle impact", yaxis_title=unit)
    return fig_waterfall


def calculate_dashboard(lca, cutoff):
    trav = JRCAssumedDiagonalGraphTraversal().calculate(lca, cutoff=cutoff)
    print("Trasversal diagonal calculated.")
    # name for the activities from activity_dict
    id_to_key = {v: k for k, v in lca.activity_dict.items()}
    activities = {
        str(id): bd.get_activity(id_to_key[id]) for id in list(trav["nodes"].keys())[1:]
    }

    # put all edge data in a dataframe to be able to scale the children of multi-parent processes
    ids = [edge["from"] for edge in trav["edges"]]
    labels = [
        activities[id.split("-")[-1]]["name"]
        + " ("
        + activities[id.split("-")[-1]]["location"]
        + ")"
        for id in ids
    ]
    parent_ids = [""] + [edge["to"] for edge in trav["edges"]][1:]

    data = dict(
        ids=ids,
        label=labels,
        # location = [act['location'] for act in activities],
        parent_ids=parent_ids,
        parent=[
            activities[id.split("-")[-1]]["name"]
            + " ("
            + activities[id.split("-")[-1]]["location"]
            + ")"
            if id != ""
            else ""
            for id in parent_ids
        ],
        labels_short=[label[:18] for label in labels],
        impact_pos=[edge["impact_pos"] for edge in trav["edges"]],
        impact_neg=[edge["impact_neg"] for edge in trav["edges"]],
        impact=[edge["impact"] for edge in trav["edges"]],
        flow_amount=[edge["amount"] for edge in trav["edges"]]
        # value_pct = value_pct
    )
    df = pd.DataFrame.from_dict(data)

    df = separate_multiple_parent(df)
    print("Multiple parent separated.")

    data = df.to_dict(orient="list")

    method = lca.method
    unit = bd.Method(method).metadata["unit"]

    fig_sunburst_pos, fig_sunburst_neg = plot_sunbursts(df, unit)
    print("Sunburst ready.")

    fig_waterfall = plot_waterfall(trav, unit)
    print("Waterfall redy.")

    fig_sankey = plot_sankey(df, unit)
    print("Sankey ready.")

    return df, lca, fig_sunburst_pos, fig_sunburst_neg, fig_waterfall, fig_sankey


def plot_dashboard(
        df, lca, fig_sunburst_pos, fig_sunburst_neg, fig_waterfall, fig_sankey
):
    method = lca.method
    unit = bd.Method(method).metadata["unit"]

    app = Dash(
        __name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME]
    )

    main_activity = df.query("depth == 1")
    methods = ["-".join(x) for x in bd.methods if "IPCC 2013" in x[0]]

    app.layout = html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader(
                        "Contribution analysis: positive and negative impacts"
                    ),
                    dbc.CardBody(
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Label("Activity"),
                                        dcc.Dropdown(
                                            main_activity["label"],
                                            main_activity["label"][0],
                                            id="activity-select",
                                        ),
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        html.Label("Method"),
                                        dcc.Dropdown(
                                            methods,
                                            "-".join(method),
                                            id="method-select",
                                        ),
                                        html.Div(
                                            [
                                                "All results shown in ",
                                                html.Span(unit, id="unit"),
                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ),
                ],
                style={"zIndex": "808"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                "Emissions",
                                style={"textAlign": "center", "width": "100%"},
                            )
                        ],
                        width=5,
                    ),
                    dbc.Col([], width=2),
                    dbc.Col(
                        [
                            html.Div(
                                "Absorptions",
                                style={"textAlign": "center", "width": "100%"},
                            )
                        ],
                        align="center",
                        width=5,
                    ),
                ],
                justify="center",
                align="center",
                style={
                    "position": "relative",
                    "zIndex": "32000",
                    "margin-bottom": "0px",
                },
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(id="sunburst-pos-graph", figure=fig_sunburst_pos),
                        width=5,
                    ),
                    dbc.Col(
                        dcc.Graph(id="waterfall-graph", figure=fig_waterfall), width=2
                    ),
                    dbc.Col(
                        dcc.Graph(id="sunburst-neg-graph", figure=fig_sunburst_neg),
                        width=5,
                    ),
                ],
                align="center",
                style={"margin-top": "-100px"},
            ),
            dbc.Row(
                [dbc.Col(dcc.Graph(id="sankey-graph", figure=fig_sankey), md=12), ],
                align="center",
            ),
        ],
    )

    return app
