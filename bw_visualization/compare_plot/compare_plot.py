import warnings
import textwrap
import pandas as pd
import numpy as np
import bw2data as bd
import matplotlib.pyplot as plt
import ipywidgets as widgets
import seaborn as sns
from IPython.display import display

from utils import lca_comparison, contributions_df, act_topscore

# define standard color palette:
COLORS = ["#F08C2E", "#7f6000", "#72AF42", "#A32683"]
COLORS.extend(COLORS)

# create longer color list for complex figures
ColorDivYlBr = sns.color_palette('YlOrBr', 6)
ColorSeqGreen = sns.color_palette('Greens', 6)
ColorSeqRdPu = sns.color_palette('RdPu', 6)
ColorSeqOrg = sns.color_palette('Oranges', 5)


# the 2 following methods come directly from the library lca_algebraic from stats.py :
# https://github.com/oie-mines-paristech/lca_algebraic/blob/master/lca_algebraic/stats.py
def _display_tabs(titles_and_contentf):
    """Generate tabs"""
    tabs = []
    titles = []
    for title, content_f in titles_and_contentf:
        titles.append(title)

        tab = widgets.Output()
        with tab:
            content_f()
        tabs.append(tab)

    res = widgets.Tab(children=tabs)
    for i, title in enumerate(titles):
        res.set_title(i, title)
    display(res)


def display_with_export_button(df):
    """Display dataframe with option to export"""

    button = widgets.Button(description="Export data")
    button.style.button_color = "lightgray"

    def click(e):
        df.to_csv("out.csv")
        button.description = "exported as 'out.csv'"

    dfout = widgets.Output()
    with dfout:
        display(df)

    button.on_click(click)

    display(widgets.VBox([button, dfout]))


def compare(fu, methods, reference_category=None, sharex=True, cols=2, func_unit="kg"):
    """Compare several activities for several impact categories

    Parameters
    ----------
    fu : dictionary of the activity/activities to compare associated with its/their associated reference flow/s
    methods : set of methods,
    reference_category : method used for normalization (None by default)
    sharex: Shared X axes ? True by default
    cols: number of columns to plot
    func_unit : functionnal unit (kg by default)
    """
    if reference_category is None:  # if no reference method is given, the first method is chosen by default.
        reference_category = methods[0]

    df = lca_comparison(fu, methods, method_ref=reference_category)

    def graph_method_ref():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fig, axes = plt.subplots(figsize=(20, 10))
            sns.set_style("white")
            df[reference_category].plot(
                ax=axes, sharex=sharex,
                legend=None,
                rot=0,
                kind='bar',
                alpha=0.8,
                fontsize=20,
                color=COLORS
            )

            axes.set_yticklabels(["0"])  # to remove all the graduations and keep only the zero
            axes.set_ylabel(reference_category[1], fontsize=20)
            # add each score of components, the text color is white if the figure is dark and vice versa
            r, g, b, _ = fig.get_facecolor()
            if r + g + b > 1:
                c = 'black'
            else:
                c = 'white'

            # Hide edges of the frame
            for spine in axes.spines.values():
                if spine.spine_type == 'bottom':
                    spine.set_visible(True)
                else:
                    spine.set_visible(False)

            for patch in axes.patches:
                axes.text(
                    # Put the text in the middle of each bar. get_x returns the start
                    # so we add half the width to get to the middle.
                    patch.get_x() + patch.get_width() / 2,
                    # Vertically, add the height of the bar to the start of the bar,
                    # along with the offset.
                    patch.get_height() + 1.02 * patch.get_y(),
                    # This is actual value we'll show.
                    str(f'{patch.get_height():.2e}') + '\n' + bd.methods[reference_category]['unit'],
                    # Center the labels and style them a bit.
                    ha='center',
                    color=c,
                    alpha=0.8,
                    size=15,
                )

            plt.xticks(range(len(df)), ['\n'.join(textwrap.wrap(label, 20)) for label in df.index])

            # add a suptitle
            fig.suptitle("Comparison of different LCA on " + bd.Method(reference_category).name[1], fontsize=30,
                         fontweight='bold', ha='center')  # centered title in bold
            # add a subtitle
            axes.set_title("for 1 " + func_unit, fontsize=17, ha='center', y=1.1, color='gray')
            plt.tight_layout()
            plt.show(fig)

    def graph_multi():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            nb_rows = int(np.ceil(len(methods) / cols))
            fig, axes = plt.subplots(figsize=(20, 15))
            sns.set_style("white")
            plt.subplots_adjust(None, None, None, None, 0.5, 0.5)

            axes = df.plot(
                ax=axes, sharex=sharex, subplots=True,
                layout=(nb_rows, cols),
                legend=None,
                rot=0,
                kind='bar',
                alpha=0.8,
                fontsize=15,
                color=COLORS)
            axes = axes.flatten()
            for ax, m in zip(axes, methods):
                ax.set_yticklabels(["0"])  # to remove all the graduations and keep only the zero
                ax.set_ylabel('\n'.join(textwrap.wrap(bd.Method(m).name[1], 20)), fontsize=15)
                ax.set_xticks(range(len(df)), ['\n'.join(textwrap.wrap(label, 20)) for label in df.index])
                ax.set_title('')

                # Hide edges of the frame
                for spine in ax.spines.values():
                    if spine.spine_type == 'bottom':
                        spine.set_visible(True)
                    else:
                        spine.set_visible(False)
                # add each score of components, the color is white if the figure is dark and vice versa
                r, g, b, _ = fig.get_facecolor()
                if r + g + b > 1:
                    c = 'black'
                else:
                    c = 'white'
                for patch in ax.patches:
                    ax.text(
                        # Put the text in the middle of each bar. get_x returns the start
                        # so we add half the width to get to the middle.
                        patch.get_x() + patch.get_width() / 2,
                        # Vertically, add the height of the bar to the start of the bar,
                        # along with the offset.
                        patch.get_height() + 1.02 * patch.get_y(),
                        # This is actual value we'll show.
                        str(f'{patch.get_height():.1e}') + '\n' + bd.methods[m]['unit'],
                        # Center the labels and style them a bit.
                        ha='center',
                        color=c,
                        alpha=0.7,
                        size=12,
                    )

            fig.suptitle("Comparison of different LCA on several impact categories", fontsize=30, fontweight='bold',
                         ha='center', y=1.03)  # centered title in bold
            fig.text(0.5, 0.99, "for 1 " + func_unit, fontsize=17, ha='center', color='gray')
            plt.tight_layout()
            plt.show(fig)

            display_with_export_button(df)

    _display_tabs([
        ("Reference indicator", graph_method_ref),
        ("All indicators", graph_multi),
    ])


def hotspots(fu, methods, reference_category=None, limit=0.05, func_unit="kg"):
    """Plot the contribution analysis of an activity for several impact categories and display the associated DataFrame
    ready to export. If the number of activities is too large, the figure is not displayed.

    Parameters
    ----------
    fu : dictionary of the single activity with its associated amount
    methods : set of impact category methods
    reference_category : method used for normalization (None by default)
    limit: relative threshold of the total lca score from which contributors are displayed (0.05 by default)
    func_unit : functionnal unit (kg by default)
    """
    if reference_category is None:  # if no reference method is given, the first method is chosen by default.
        reference_category = methods[0]

    df = lca_comparison(fu, methods, method_ref=reference_category)

    # to have one color by method, we define a dataframe:
    df_color = pd.DataFrame(index=methods, data=[COLORS[c] for c in range(len(methods))]).T

    def contributions(act, method):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_contrib = contributions_df(act, method, limit=limit)

            # Instead of keys we prefer using  activity names
            names = []
            for c in df_contrib.index:
                names.append(bd.get_activity(c)['name'])

            # Add a row for the other contributors
            df_contrib.loc['Others'] = [df[method][act['name']] - df_contrib[c].sum() for c in df_contrib.columns]

            # Add the names
            df_contrib['Activity'] = names + ['Others']

            fig, axes = plt.subplots(figsize=(20, 10))
            sns.set_style("white")
            plt.subplots_adjust(None, None, None, None, 0.5, 0.5)
            plt.barh(df_contrib.index, df_contrib[method], alpha=0.8, color=df_color[method])
            axes.set_title(f'Contribution analysis of LCA on {method[1]}', fontsize=20)
            axes.set_xlabel(bd.Method(method).name[1], fontsize=20)
            axes.set_xticks([])
            axes.set_yticks(range(len(df_contrib)),
                            ['\n'.join(textwrap.wrap(label, 40)) for label in df_contrib['Activity']], fontsize=15)
            # add each score of components
            for patch in axes.patches:
                y_offset = patch.get_width() / 100
                r, g, b, _ = patch.get_facecolor()  # the color is white if the bar is dark and vice versa
                if r + g + b > 1.8:
                    c = 'black'
                else:
                    c = 'white'

                if patch.get_width() > 0:
                    axes.text(
                        patch.get_x() + y_offset,
                        patch.get_y() + patch.get_height() / 2,
                        str(f'{patch.get_width():.2e}') + ' ' + bd.methods[method]['unit'],
                        ha='left',
                        color=c,
                        alpha=0.8,
                        size=15,
                    )
                else:
                    axes.text(
                        patch.get_x() + patch.get_width(),
                        patch.get_y() + patch.get_height() / 2,
                        str(f'{patch.get_width():.2e}') + ' ' + bd.methods[reference_category]['unit'],
                        ha='left',
                        color=c,
                        alpha=0.8,
                        size=15,
                    )
            # Hide edges of the frame
            for spine in axes.spines.values():
                if spine.spine_type == 'left':
                    spine.set_visible(True)
                else:
                    spine.set_visible(False)

            fig.suptitle("Contribution analysis of " + act['name'] + "\n", fontsize=30, fontweight='bold', ha='center',
                         x=axes.get_position().x0 + 0.5, y=1.02)  # centered title in bold
            plt.tight_layout()
            plt.show()
            display_with_export_button(df_contrib)

    if len(fu) > 7:
        print('The number of activities is too large to plot the contributions for each of them')
    else:
        for act in list(fu.keys()):
            _display_tabs([("on " + str(i[1]), contributions(act, i)) for i in methods])


def impact_transfer(fu, methods, reference_category=None, limit=5, cols=3, func_unit="kg"):
    """Plot the variations of the contribution of the top processes (for the reference method) for each impact category

    Parameters
    ----------
    fu : dictionary of activities with the associated amount
    methods : set of impact category methods
    reference_category : method used for normalization (None by default)
    limit: relative threshold of the total lca score from which contributors are displayed (0.05 by default)
    cols: number of columns to plot
    func_unit : functionnal unit (kg by default)
    """
    if reference_category is None:  # if no reference method is given, the first method is chosen by default.
        reference_category = methods[0]
    df = lca_comparison(fu, methods, method_ref=reference_category)
    act_ref = act_topscore(fu, reference_category)
    df_norm = df.T.apply(lambda x: x / x.max(), axis=1)  # to normalize the results for each impact category

    def heatmap():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fig, axes = plt.subplots(figsize=(20, 10))
            sns.set_style("white")
            sns.heatmap(df_norm, annot=True, cbar=True, ax=axes, cmap='YlOrBr', alpha=0.8, linewidth=0.5,
                        xticklabels=True)
            axes.set_yticklabels([bd.Method(m).name[1] for m in methods], rotation=0, fontsize=20)
            axes.set_xticks(range(len(df_norm.columns)),
                            ['\n'.join(textwrap.wrap(label, 20)) for label in df_norm.columns], rotation=0, fontsize=20,
                            ha="left")
            fig.suptitle("Comparison of different LCA", fontsize=20, fontweight='bold', x=0.44,
                         y=1.02)  # centered title in bold
            axes.set_title("for 1 " + func_unit, fontsize=17, ha='center', y=1.1, color='gray')
            plt.show()
            display_with_export_button(df_norm)

    def transfer_impact():

        act_transfert = [act for act in fu.keys() if act != act_ref][0]
        df_transfer = df_norm[act_transfert['name']] * 100 - df_norm[act_ref['name']] * 100  # %
        df_transfer = df_transfer.sort_values()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sns.set_style("white")
            fig, axes = plt.subplots(figsize=(20, 10))
            plt.bar(range(len(df_transfer)), df_transfer, alpha=0.8, color=COLORS)
            xlabel = [bd.Method(m).name[1] + ' ' + '\n' + bd.methods[m]['unit'] for m in methods]
            plt.xticks(range(len(df_transfer)), ['\n'.join(textwrap.wrap(label, 30)) for label in xlabel], fontsize=15)
            # To remove the frame but keep a horizontal line on 0
            axes.spines['top'].set_visible(False)
            axes.spines['right'].set_visible(False)
            axes.spines['bottom'].set_visible(False)
            axes.spines['left'].set_visible(False)
            axes.axhline(y=0, color='gray', linewidth=1)
            # add each score of components
            for patch in axes.patches:
                if patch.get_height() >= 0:
                    y_offset = -6
                    axes.set_ylabel('Impact Transfer', fontsize=20)
                    fig.suptitle(
                        f'Impact transfer of {act_transfert["name"]} \n compared to {act_ref["name"]}',
                        fontsize=30, fontweight='bold', ha='center')
                else:
                    y_offset = 1
                    axes.set_ylabel('Impact Reduction', fontsize=20)
                    fig.suptitle(
                        f"Impact Reduction of {act_transfert['name']} \n compared to {act_ref['name']}",
                        fontsize=25, fontweight='bold', ha='center')
                r, g, b, _ = patch.get_facecolor()  # the color is white if the bar is dark and vice versa
                if r + g + b > 1.8:
                    c = 'black'
                else:
                    c = 'white'
                axes.text(
                    # Put the text in the middle of each bar. get_x returns the start so we add half the width to get
                    # to the middle.
                    patch.get_x() + patch.get_width() / 2,
                    # Vertically, add the height of the bar to the start of the bar,
                    # along with the offset.
                    patch.get_height() + patch.get_y() + y_offset,
                    # This is actual value we'll show.
                    str(round(patch.get_height())) + ' %',
                    # Center the labels and style them a bit.
                    ha='center',
                    color=c,
                    alpha=0.9,
                    size=20,
                )
            axes.set_yticks([0])  # to remove all the graduations and keep only the zero
            plt.show()

    def reference_contributions(act):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            # Get the top contributors for the reference impact category
            df = contributions_df(act, reference_category, limit=limit, limit_type='number', group_by_other=False,
                                  norm=True)
            top_contributors_reference = list(df.index)

            # Compute the contributors for the other impact categories and gather it into a dictionnary
            contributions_by_category = {}
            for m in methods:
                # very small threshold to get almost every contributors
                contributions_by_category[m] = contributions_df(act, m, limit=0.000001, norm=True)

            # Create an empty dataframe with the top reference contributors as indexes and the impact categories as
            # columns
            result_df = pd.DataFrame(columns=methods, index=top_contributors_reference)

            # For each reference top contributor, check if it appears in the contributions dataframes stored in the
            # dictionary
            for c in top_contributors_reference:
                for m in methods:
                    if c in contributions_by_category[m].index:
                        result_df.at[c, m] = contributions_by_category[m].loc[c][0]
                    else:
                        result_df.at[c, m] = pd.np.nan

            names = []
            for c in result_df.index:
                names.append(bd.get_activity(c)['name'])

            # Add a row for the other contributors
            result_df.loc['Others'] = [100 - result_df[c].sum() for c in result_df.columns]

            result_df['Activities'] = names + ['Others']

            # Plot the dataframe in a horizontal bar chart
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fig, axes = plt.subplots(figsize=(20, 10))
                nb_rows = int(np.ceil(len(methods) / cols))

                sns.set_style("white")
                plt.subplots_adjust(None, None, None, None, 0.5, 0.5)
                axes = result_df.plot(
                    ax=axes, sharey=True, subplots=True,
                    layout=(nb_rows, cols),
                    legend=None,
                    rot=0,
                    kind='barh',
                    alpha=0.8,
                    fontsize=20,
                    color=COLORS)
                axes = axes.flatten()

                for ax, m in zip(axes, methods):
                    ax.set_title(m[1], fontsize=15)
                    ax.set_xticks([])
                    ax.set_yticks(range(len(result_df)),
                                  ['\n'.join(textwrap.wrap(label, 40)) for label in result_df['Activities']],
                                  fontsize=15)
                    # add each score of components
                    for patch in ax.patches:
                        ax.text(
                            patch.get_x() + 1.01 * patch.get_width(),
                            patch.get_y() + patch.get_height() / 3,
                            str(f'{patch.get_width():.0f}') + ' %',
                            ha='left',
                            color='black',
                            alpha=0.8,
                            size=12)

                    # Hide edges of the frame
                    for spine in ax.spines.values():
                        if spine.spine_type == 'left':
                            spine.set_visible(True)
                        else:
                            spine.set_visible(False)

                fig.suptitle("Contribution analysis of " + act['name'] + "\n", fontsize=30, fontweight='bold',
                             ha='center', y=1.02)  # centered title in bold
                plt.tight_layout()
                plt.show()

    if len(fu) == 2:
        _display_tabs([("Impact transfer", transfer_impact), ("Heatmap", heatmap)] +
                      [(j['name'], lambda k=j: reference_contributions(k)) for j in list(fu.keys())]
                      )
    else:
        _display_tabs([("Heatmap", heatmap)] +
                      [(j['name'], lambda k=j: reference_contributions(k)) for j in list(fu.keys())]
                      )


def lca_graphic(fu, methods, reference_category=None, func_unit="kg"):
    """Generic function that calls the other methods to plot :
    - one dashboard that compare the impacts of serveral activites in different impact categories
    - one dashboard for each activity to plot the main contributors for each impact categories
    - one dashboard to plot the variations of the contribution of the top processes (for the
        reference method) for each impact category

    Parameters
    ----------
    fu : dictionary of the activity/activities to compare associated with its/their associated reference flow/s
    methods : set of methods
    reference_category : method used for normalization (None by default)
    func_unit : functionnal unit (kg by default)
    """

    if reference_category is None:  # if no reference method is given, the first method is chosen by default.
        reference_category = methods[0]

    compare(fu, methods, func_unit=func_unit)
    impact_transfer(fu, methods, reference_category=reference_category, limit=5, func_unit=func_unit, cols=2)
    hotspots(fu, methods, limit=0.02)
