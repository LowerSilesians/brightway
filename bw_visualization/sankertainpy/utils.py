from warnings import warn
import bw2calc as bc
import numpy as np
from bw2data import get_activity


def update_or_create_nodes(nodes, activity, actual_node, parent_node, source, target, scores):
    """
    Update or create nodes dictionary

    Parameters
    ----------
    nodes : dict
        Dictionary containing information about the nodes. Keys are int values
        regarding the source/target values.
    activity : Activity
        Starting point of the supply chain graph.
    actual_node : int
        Actual node.
    parent_node : int
        Parent node.
    source : list
        List of int regarding the keys from 'nodes'.
    target : list
        List of int regarding the keys from 'nodes'.
    scores : list
        List of floats/list containing the weight of the links between the nodes from 'nodes'.

    Returns
    -------
    tuple
        Nodes.
    """
    if nodes is None:
        nodes = {0: {"act": activity, 'name': f"{activity['name']}, {activity['location']}"},
                 1: {"act": activity, 'name': f"{activity['name']}, {activity['location']}"}}
        actual_node = 1
        parent_node = 0
        source = []
        target = []
        scores = []
    else:
        nodes[actual_node] = {"act": activity, 'name': f"{activity['name']}, {activity['location']}"}

    return nodes, actual_node, parent_node, source, target, scores


def calculate_score(activity, lca_obj, mc, amount, lcia_method, mc_number, total_score, cutoff):
    """
    Calculate LCA score

    Parameters
    ----------
    activity : Activity
        Starting point of the supply chain graph.
    lca_obj : LCA
        LCA object
    mc : bool
        Wether Monte Carlo simulation should carry out or not.
    amount : int
        Amount of activity to assess.
    lcia_method : tuple
        LCIA method to use when traversing supply chain graph.
    mc_number : int
        Iterations of the monte carlo simulations
    total_score : float
        LCA total score
    cutoff : float
        Fraction of total score to use as cutoff when deciding whether to traverse deeper and
        if Monte Carlo simulation should be carried out.

    Returns
    -------
    tuple
        LCA score.
    """
    if lca_obj is None:
        if mc:
            lca_obj = bc.LCA({activity: amount}, lcia_method, use_distributions=True)
            lca_obj.lci()
            lca_obj.lcia()
            mc_result = [lca_obj.score for _ in zip(range(mc_number), lca_obj)]
            total_score = np.median(mc_result)
            score = mc_result

        else:
            lca_obj = bc.LCA({activity: amount}, lcia_method)
            lca_obj.lci()
            lca_obj.lcia()
            total_score = lca_obj.score
            score = total_score

    elif total_score is None:
        raise ValueError
    else:
        if mc:
            lca_obj.redo_lcia({activity.id: amount})
            score = lca_obj.score
            if abs(score) > abs(total_score * cutoff):
                lca_obj.redo_lcia({activity.id: amount})
                score = [lca_obj.score for _ in zip(range(mc_number), lca_obj)]

        else:
            lca_obj.redo_lcia({activity.id: amount})
            score = lca_obj.score

    return lca_obj, total_score, score


def recursive_calculation_to_plotly(
        activity,
        lcia_method,
        amount=1,
        max_level=3,
        cutoff=1e-2,
        mc=False,
        mc_number=100,
        lca_obj=None,
        total_score=None,
        result_list=None,
        level=0,
        nodes=None,
        source=None,
        target=None,
        actual_node=None,
        scores=None,
        parent_node=None,

):
    """
    Traverse a supply chain graph, and calculate the LCA scores of each component.
    Adds a dictionary to result_list of the form.

    Parameters
    ----------
    activity: Activity
        Starting point of the supply chain graph.
    lcia_method: tuple
        LCIA method to use when traversing supply chain graph.
    amount: int
        Amount of activity to assess.
    max_level: int
        Maximum depth to traverse.
    cutoff: float
        Fraction of total score to use as cutoff when deciding whether to traverse deeper and
        if Monte Carlo simulation should be carried out.
    mc: bool
        wether Monte Carlo simulation should carry out or not.
    mc_number: int
        Iterations of the monte carlo simulations.

    Internal args (used during recursion, do not touch)
    ---------------------------------------------------
    result_list
    level
    nodes
    source
    target
    actual_node
    scores
    parent_node

    Returns
    -------
    dict
        Dictionary of the following lists:
            sources: List of int regarding the keys from 'nodes'.
            targets: List of int regarding the keys from 'nodes'.
            scores: List of floats/list containing the weight of the links between the nodes from 'nodes'.
                    Monte Carlo results are wrapped in a nested list.
            nodes: Dictionary containing information about the nodes. Keys are int values
                   regarding the source/target values.
    """

    activity = get_activity(activity)

    nodes, actual_node, parent_node, source, target, scores = update_or_create_nodes(
        nodes, activity, actual_node, parent_node, source, target, scores)
    lca_obj, total_score, score = calculate_score(
        activity, lca_obj, mc, amount, lcia_method, mc_number, total_score, cutoff
    )

    target.append(parent_node)
    source.append(actual_node)
    scores.append(score)

    if level < max_level and abs(lca_obj.score) > abs(total_score * cutoff):
        prod_exchanges = list(activity.production())
        if not prod_exchanges:
            prod_amount = 1
        elif len(prod_exchanges) > 1:
            warn(f"Hit multiple production exchanges for {activity}; aborting in this branch")
            return None
        else:
            prod_amount = lca_obj.technosphere_matrix[
                lca_obj.dicts.product[prod_exchanges[0].input.id],
                lca_obj.dicts.activity[prod_exchanges[0].output.id],
            ]
        actual_node_static = actual_node

        for exc in activity.technosphere():
            if exc.input.id == exc.output.id:
                continue

            tm_amount = exc["amount"]

            target, source, scores, nodes, actual_node = recursive_calculation_to_plotly(
                activity=exc.input,
                lcia_method=lcia_method,
                amount=amount * tm_amount / prod_amount,
                max_level=max_level,
                cutoff=cutoff,
                mc=mc,
                mc_number=mc_number,
                result_list=result_list,
                lca_obj=lca_obj,
                total_score=total_score,
                level=level + 1,
                nodes=nodes,
                source=source,
                target=target,
                actual_node=actual_node + 1,
                scores=scores,
                parent_node=actual_node_static,
            )
    if level == 0:
        return {'targets': target, 'sources': source, 'scores': scores, 'nodes': nodes}
    return target, source, scores, nodes, actual_node
