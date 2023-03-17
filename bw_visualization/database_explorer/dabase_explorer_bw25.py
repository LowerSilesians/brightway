# -*- coding: utf-8 -*-
"""
Created on Mon May  2 16:14:57 2022

@author: romai
"""
# Importing libraries
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("ggplot")
import matplotlib.backends.backend_pdf
import plotly.graph_objects as go
import plotly.express as px
import bw2data as bwd
import bw2calc as bwc
from IPython.display import display

# Default impact categories
METHODS_EF = [
    m
    for m in bwd.methods
    if "EF v3.0 EN15804" in str(m)
       and "no LT" not in str(m)
       and "obsolete" not in str(m)
]
METHODS_CC = [m for m in METHODS_EF if "climate" in str(m)]
METHOD_CC = METHODS_CC[0]


class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def contribution_analysis_by_substances(lca, ratio=0.8, length_max=10):
    """Function returning a dataframe giving the impact contribution by substances"""
    df_characterized_inventory = lca.to_dataframe(
        matrix_label="characterized_inventory"
    )
    df_ca_substance = df_characterized_inventory.groupby("row_name")[["amount"]].sum()
    df_ca_substance = df_ca_substance.sort_values(by="amount", ascending=False)

    impact = lca.score
    impact_i = 0
    i = 0
    while impact_i < ratio * impact:
        impact_i += df_ca_substance.iloc[i]["amount"]
        i += 1

    i = np.min([i, length_max])
    df_ca_substance = df_ca_substance.iloc[0:i]
    df_ca_substance.loc["Other"] = impact - df_ca_substance.amount.sum()
    df_ca_substance["percentage"] = df_ca_substance.amount / impact * 100

    return df_ca_substance


def contribution_analysis_by_activities(lca, ratio=0.8, length_max=10):
    """Function returning a dataframe giving the impact contribution by activities"""
    df_characterized_inventory = lca.to_dataframe(
        matrix_label="characterized_inventory"
    )
    df_ca_activity = df_characterized_inventory.groupby("col_name")[["amount"]].sum()
    df_ca_activity = df_ca_activity.sort_values(by="amount", ascending=False)

    impact = lca.score
    impact_i = 0
    i = 0
    while impact_i < ratio * impact:
        impact_i += df_ca_activity.iloc[i]["amount"]
        i += 1

    i = np.min([i, length_max])
    df_ca_activity = df_ca_activity.iloc[0:i]
    df_ca_activity.loc["Other"] = impact - df_ca_activity.amount.sum()
    df_ca_activity["percentage"] = df_ca_activity.amount / impact * 100

    return df_ca_activity


class ListAct:
    def __init__(self, database, name, location="", unit="", list_act_input=None):
        self.database = database
        self.name = name
        self.list_act = list_act_input
        self.location = location
        self.unit = unit

    def search(self, strict=False):
        if not self.list_act:
            list_act = [
                act
                for act in self.database
                if self.name in act["name"]
                and self.location in act["location"]
                and self.unit in act["unit"]
            ]
            if strict:
                list_act = [act for act in list_act if act["name"] == self.name]
            self.list_act = list_act

    def get_list(self, field):
        return {act[field] for act in self.list_act}

    def get_lists(self):
        self.list_name = self.get_list(field="name")
        self.list_location = self.get_list(field="location")
        self.list_unit = self.get_list(field="unit")

    def print_lists(self):
        print(Color.BOLD + Color.UNDERLINE + "List of names:" + Color.END)
        display(self.list_name)
        print(Color.BOLD + Color.UNDERLINE + "List of locations:" + Color.END)
        display(self.list_location)
        print(Color.BOLD + Color.UNDERLINE + "List of units:" + Color.END)
        display(self.list_unit)

    def get_comment(self, i):
        act = self.list_act[i]
        print(Color.BOLD + Color.UNDERLINE + str(act) + Color.END)
        display(act["comment"])

    def get_comments(self):
        for i, _ in enumerate(self.list_act):
            self.get_comment(i)
            print("\n")

    def get_inventory(self, i):
        df = (
            self.list_act[i]
                .exchanges()
                .to_dataframe()[
                [
                    "source_name",
                    "source_location",
                    "source_unit",
                    "edge_amount",
                    "edge_type",
                ]
            ]
        )

        df["edge_type"] = pd.Categorical(
            df["edge_type"], ["production", "technosphere", "biosphere"]
        )
        df = df.sort_values("edge_type")
        return df

    def get_inventories(self, index_name="name"):
        dataframe = pd.DataFrame()
        for i, act in enumerate(self.list_act[0:5]):
            print(i)
            print(act)
            df = self.get_inventory(act)
            df = df.groupby("source_name")["edge_amount"].sum()
            dataframe[i] = df
        if index_name == "location":
            dataframe.columns = [act["location"] for act in self.list_act]
        if index_name == "name":
            dataframe.columns = [act["name"] + "_" + act["location"] for act in self.list_act]
        self.dataframe = dataframe

    def get_impacts(self, methods=METHODS_EF):
        list_inv = [{act: 1} for act in self.list_act]
        bwd.calculation_setups["multiLCA"] = {"inv": list_inv, "ia": methods}
        my_multi_lca = bwc.MultiLCA("multiLCA")
        df_impacts = pd.DataFrame(data=my_multi_lca.results)
        df_impacts.columns = [f"{m[1]} \n {m[2]}" for m in methods]
        df_impacts.index = [
            f"{act['name']} [{act['location']}]" for act in self.list_act
        ]

        self.impacts = df_impacts
        self.methods = methods
        return df_impacts

    def plot_impact_climate(self):
        df = self.impacts

        list_col = [col for col in df.columns if "climate change" in col]
        df = df[list_col]
        max_value = df.max().max()

        fig, ax = plt.subplots(figsize=(10, 4))
        ax2 = ax.twinx()
        df.T.plot(ax=ax, kind="bar", alpha=0.6, rot=15)
        ax2.set_zorder(-1)
        (df.T / max_value * 100).plot(ax=ax2, kind="bar", alpha=0.0, rot=15)
        ax2.set_ylabel("Percentage of maximum value (%)")
        if len(self.list_unit) == 1:
            ax.set_ylabel(f"kg$CO_2$eq/{list(self.list_unit)[0]}")
        else:
            ax.set_ylabel(f"kg$CO_2$eq/{self.list_unit}")
        ax.set_title(f"Carbon footprint of {self.name}")
        return fig, ax

    def plot_impacts(self, double_axis=True):
        fig, ax = plt.subplots(5, 4, sharex=True, figsize=(16, 12))
        fig.subplots_adjust(hspace=0.4, wspace=0.6)
        ax = ax.ravel()
        for axi in ax[self.impacts.shape[1]:]:
            axi.axis("off")
        ax = ax[0: self.impacts.shape[1]]
        if double_axis:
            ax2 = [axi.twinx() for axi in ax]
        self.impacts.plot(
            ax=ax,
            legend=False,
            subplots=True,
            kind="bar",
            alpha=0.6,
        )
        if double_axis:
            (self.impacts / self.impacts.max() * 100).plot(
                ax=ax2, legend=False, subplots=True, kind="bar", alpha=0
            )
        for i, axi in enumerate(ax):
            if double_axis:
                ax2[i].set_zorder(-1)
                ax2[i].set_ylabel("% of max value")
                ax2[i].set_title("")
            m = self.methods[i]
            # m = m[1]+'\n'+m[2]
            axi.set_title(m[1].replace(":", "\n"), fontsize=13)
            # TODO: I'm not sure from where bw should came from
            axi.set_ylabel(bwd.Method(self.methods[i]).metadata["unit"])

        return fig, ax

    def explore(self, strict=False, comments=False):
        self.search(strict=strict)
        if comments:
            display(self.list_act)
            print()
        self.get_lists()
        self.print_lists()
        if comments:
            self.get_comments()

    def analyse(self, methods_cc=METHODS_CC, methods_ef=METHODS_EF, print_data=True):
        self.get_inventories()
        if print_data:
            print(Color.BOLD + Color.UNDERLINE + "All flows:" + Color.END)
            display(self.dataframe)
        self.get_impacts(methods=methods_cc)
        if print_data:
            print(Color.BOLD + Color.UNDERLINE + "Carbon footprint:" + Color.END)
            display(self.impacts)
        self.get_impacts(methods_ef)
        if print_data:
            print(Color.BOLD + Color.UNDERLINE + "All impacts:" + Color.END)
            display(self.impacts)
        _, _ = self.plot_impact_climate()
        _, _ = self.plot_impacts()

    def calculate_contribution_analysis(
            self, act, method, ratio=0.8, length_max=10, amount=1
    ):
        lca = bwc.LCA({act: amount}, method)
        lca.lci()
        lca.lcia()

        # TODO: ask Chris about CA_Elem_flow and CA_Process
        df_cae = CA_Elem_Flow(lca=lca, ratio=ratio, length_max=length_max)
        df_cap = CA_Process(lca=lca, ratio=ratio, length_max=length_max)
        self.df_CAe = df_cae
        self.df_CAp = df_cap
        self.lca_score = lca.score

    def plot_contribution_analysis(self, act, method, amount):
        fig, ax = plt.subplots(2, 1, figsize=(16, 7), sharex=True)
        self.df_CAe[["percentage"]].T.plot(
            ax=ax[0], kind="barh", stacked=True, alpha=0.6, rot=90
        )
        ax[0].set_title("Contribution per substances")
        ax[0].set_xlabel("Percentage (%)")
        ax[0].legend(bbox_to_anchor=(1.173, 1))

        self.df_CAp[["percentage"]].T.plot(
            ax=ax[1], kind="barh", stacked=True, alpha=0.6, rot=90
        )
        ax[1].legend(bbox_to_anchor=(1, 1))
        ax[1].set_title("Contribution per activities")
        ax[1].set_xlabel("Percentage (%)")

        m = bwd.Method(method)
        title = (
            f'Contribution analysis for "{act["name"]}"'
            + f"\n for the impact category: {str(method)}"
            + f"\n Total impact = {self.lca_score:0.2g} {m.metadata['unit']}/ {amount:0.f} {act['unit']}"
        )
        plt.suptitle(title, fontsize=20, y=1.07)
        return fig

    def contribution_analysis(
            self, i, methods, ratio=0.8, length_max=10, amount=1, save=False
    ):
        act = self.list_act[i]
        print(act)
        if save:
            pdf = matplotlib.backends.backend_pdf.PdfPages(
                "output_contribution_analysis.pdf"
            )
        for method in methods:
            print(method)
            self.calculate_contribution_analysis(
                act=act,
                method=method,
                ratio=ratio,
                length_max=length_max,
                amount=amount,
            )
            fig = self.plot_contribution_analysis(act=act, method=method, amount=amount)
            if save:
                pdf.savefig(fig, bbox_inches="tight")
        if save:
            pdf.close()

    def plot_sankey(self, i, method, cutoff, amount=1):
        act = self.list_act[i]
        lca = bwc.LCA({act: amount}, method)
        lca.lci()
        lca.lcia()
        impact = lca.score
        unit = bwd.Method(method).metadata["unit"]

        gt = bwc.GraphTraversal().calculate({act: amount}, method=method, cutoff=cutoff)

        acts = gt["lca"].activity_dict
        id_to_key = {v: k for k, v in acts.items()}
        # labels = {k: bw.get_activity(v)["name"] for k in gt["nodes"].values()}
        ids = list(gt["nodes"].keys())
        labels = [bwd.get_activity(id_to_key[id])["name"] for id in ids[1:]]
        labels = ["root"] + labels
        id_to_idx = {id: idx for idx, id in enumerate(ids)}
        edges = gt["edges"]
        edges_plot = dict(
            target=[id_to_idx[edge["to"]] for edge in edges],
            source=[id_to_idx[edge["from"]] for edge in edges],
            value=[edge["impact"] / impact * 100 for edge in edges],
        )

        fig = go.Figure(
            data=[
                go.Sankey(
                    valueformat=".0f",
                    valuesuffix=" %",
                    node=dict(label=labels),
                    link=edges_plot,
                ),
            ],
        )

        fig.update_layout(
            title_text=f"{str(method)} : \n{impact:0.3f} {unit}/{amount:0.f} {act['unit']}",
            title_x=0.5,
            font_size=12,
            width=800,
            height=500,
        )

        return fig

    def plot_sankeys(self, i, methods, cutoff, amount=1, save=True):
        with open("output_Sankey.html", "a", encoding='utf-8') as f:
            for method in methods:
                fig = self.plot_sankey(i=i, method=method, cutoff=cutoff, amount=amount)
                if save:
                    f.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))
                else:
                    fig.show()

    def plot_sunburst(self, i, method, cutoff, amount=1):
        act = self.list_act[i]
        lca = bwc.LCA({act: amount}, method)
        lca.lci()
        lca.lcia()
        impact = lca.score
        unit = bwd.Method(method).metadata["unit"]

        gt = bwc.GraphTraversal().calculate({act: amount}, method=method, cutoff=cutoff)

        # Label
        acts = gt["lca"].activity_dict
        id_to_key = {v: k for k, v in acts.items()}

        ids = list(gt["nodes"].keys())
        labels = [bwd.get_activity(id_to_key[id])["name"] for id in ids[1:]]
        labels_loc = [bwd.get_activity(id_to_key[id])["location"] for id in ids[1:]]
        labels = [
            label + " " + label_loc for label, label_loc in zip(labels, labels_loc)
        ]
        # Source
        edges = gt["edges"]
        edges = edges[: len(labels)]
        ids_source = [edge["to"] for edge in edges]
        ids_source = [
            bwd.get_activity(id_to_key[id])["name"]
            + " "
            + bwd.get_activity(id_to_key[id])["location"]
            for id in ids_source[1:]
        ]
        ids_source = [""] + ids_source
        # Value
        value = [edge["impact"] for edge in edges]
        # Data dictionary
        data = dict(label=labels, location=labels_loc, parent=ids_source, value=value)
        df = pd.DataFrame.from_dict(data)
        # Percentage data
        df["value_pct"] = df.value / impact * 100
        # Flooring percentage value to avoid sum of childs slightly higher than parents, and calculating value from
        # floored pct
        df.value_pct = (df.value_pct * 10).apply(math.floor) / 10
        df.value = df.value_pct / 100 * impact
        df.value = df.value.apply(lambda x: round(x, 3))

        # Filtering negative value
        list_label_negatif = list(df[df.value <= 0].label.unique())

        def is_parent_or_child_negative(row):
            if (row.label in list_label_negatif) or (row.parent in list_label_negatif):
                return True
            return False

        df["is_negative"] = df.apply(is_parent_or_child_negative, axis=1)
        df_p = df[df.is_negative is False]
        df_n = df[df.is_negative is True]

        data_p = df_p.to_dict()
        _ = df_n.to_dict()

        # Sunburst for positive value
        fig = px.sunburst(
            data_p,
            names="label",
            parents="parent",
            values="value",
            branchvalues="total",
            color="value_pct",
            color_continuous_scale="algae",
            hover_data=["location"],
            # valueformat = '.0f',
        )
        fig.update_traces(textinfo="percent parent")
        # fig.update_layout(uniformtext = dict(minsize=8, mode='hide'))

        title = f"{act['name'].capitalize()}: {impact:.2g} {unit}/{amount:2g}{act['unit']}\n <br> Method: {str(method)}"
        fig.update_layout(autosize=True, title_text=title, title_x=0.5, font_size=10)
        # fig.show()
        return fig

    def plot_sunbursts(self, i, methods, cutoff, amount=1, save=True):
        with open("output_Sunburst.html", "a", encoding='utf-8') as f:
            for method in methods:
                fig = self.plot_sunburst(
                    i=i, method=method, cutoff=cutoff, amount=amount
                )
                if save:
                    f.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))
                else:
                    fig.show()
