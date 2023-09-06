import bw2calc as bc
import numpy as np
import pandas as pd
import bw2analyzer as ba


def lca_comparison(fu, methods, method_ref=None):
    """
    Compare several activities for several impact categories and return a DataFrame with the impact score for each
    categories and each activities.

    Parameters
    ----------
    fu : dict
        Dictionary of the activity/activities to compare associated with its/their associated reference flow/s.
    methods : tuple
        Set of methods.
    method_ref : tuple
        Method used for normalization (by default, None).

    Returns
    -------
    pd.DataFrame
        LCA comparison dataframe
    """
    if method_ref is None:  # if no reference method is given, the first method is chosen by default.
        method_ref = methods[0]

    scores = []
    names = []
    if len(methods) > 1:  # for multi impact categories
        for act, q in zip(fu.keys(), fu.values()):
            lca = bc.LCA({act: q}, methods[0])
            lca.lci()
            lca.lcia()
            res = []
            for m in methods:
                lca.switch_method(m)
                lca.lcia()
                res.append(lca.score)
            scores.append(res)
            names.append(act['name'])
    else:
        for act, q in zip(fu.keys(), fu.values()):
            lca = bc.LCA({act: q}, methods[0])
            lca.lci()
            lca.lcia()
            scores.append(lca.score)
            names.append(act['name'])

    return pd.DataFrame(index=names, data=scores, columns=methods).sort_values(by=[method_ref], ascending=False)


def act_topscore(fu, method_ref):
    """
    Give the activity which has the highest score the reference method

    Parameters
    ----------
    fu : dict
        Dictionary of the activity/activities to compare associated with its/their associated reference flow/s.
    method_ref : tuple
        Method used for normalization.

    Returns
    -------
    dict
        Highest score activity.
    """
    activities = list(fu.keys())
    scores = []

    for act, q in zip(activities, fu.values()):
        lca = bc.LCA({act: q}, method_ref)
        lca.lci()
        lca.lcia()
        scores.append(lca.score)

    max_index = scores.index(max(scores))

    return activities[max_index]


def contributions_df(activity, method, limit=0.01, limit_type='percent', group_by_other=False, norm=False):
    """Gather in a dataframe the main contributors of the lca score

    Parameters
    ----------
    activity : dict
        Activity to be analyzed.
    method : tuple
        Impact category method.
    limit: float, optional
        Relative threshold of the total lca score from which contributors are displayed : (0.01 by default).
    limit_type : str, optional
        Percentage or number for the threshold ('percent' by default).
    group_by_other : bool, optional
        Group the other contributors into an 'other' category (True by default).
    norm : bool, optional
        Norm the contributions (False by default).

    Returns
    -------
    pd.DataFrame
        main contributors to the lca score.
    """

    ca = ba.ContributionAnalysis()
    # we compute the top contributors for the impact category
    lca = bc.LCA({activity: 1}, method)
    lca.lci()
    lca.lcia()
    # returns a list of tuples: (lca score, supply amount, activity name)
    contrib = ca.annotated_top_processes(lca, limit=limit, limit_type=limit_type)

    names = [i[2]['name'] + ' [' + i[2]['location'] + ']' for i in
             contrib]  # for each impact category we concatenate all names
    codes = [i[2]['code'] for i in contrib]
    scores = [i[0] for i in contrib]  # for each impact category we add a new tuple for the scores

    if group_by_other:
        names.append('Others')
        codes.append('Others')
        scores.append(lca.score - np.sum(scores))

    if norm:
        scores = [s / lca.score * 100 for s in scores]

    return pd.DataFrame(index=codes, data=scores, columns=[method]).sort_values(by=[method], ascending=True)
