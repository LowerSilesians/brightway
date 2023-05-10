import numpy as np
import plotly.graph_objects as go
import matplotlib


def cut_off_flows(data, label_list, cutoff):
    # Combine flows < cutoff to one node:
    total_score = np.mean(data['scores'][0])
    label_list.append('Activities< cutoff')
    upstream = len(label_list) - 1
    label_list.append('Activities< cutoff downstream')
    downstream = len(label_list) - 1

    for i, flow in enumerate(data['scores']):
        if abs(np.mean(flow)) / abs(total_score) < cutoff:
            if np.mean(flow) > 0:
                data['sources'][i] = upstream
            else:
                data['sources'][i] = downstream
    return data, label_list


def add_emissions(i, data, label_list, upstream, downstream):
    inp = 0
    out = 0
    for n, scr in enumerate(data['scores']):
        if data['sources'][n] == i:
            out = out + np.mean(scr)

        if data['targets'][n] == i:
            inp = inp + np.mean(scr)

    if inp != 0 and out != 0 and inp != out:

        if out > 0:
            data['scores'].append(out - inp)
            data['sources'].append(upstream)
            data['targets'].append(i)
        else:
            data['scores'].append(out - inp)
            data['sources'].append(downstream)
            data['targets'].append(i)

    return data, label_list


def calc_emissions(data, label_list):
    # iterate through nodes and link emissions to additional node
    label_list.append('Emissions')
    upstream = len(label_list) - 1
    label_list.append('Emissions downstream')
    downstream = len(label_list) - 1
    data['nodes'][len(label_list) - 1] = {'name': 'Emissions'}

    for _, (i, _) in enumerate(data['nodes'].items()):
        data, label_list = add_emissions(i, data, label_list, upstream, downstream)

    return data, label_list


def calc_quantile_flows(data, cutoff, barrier_free):
    # Split flows with list of Monte Carlo datas into different quantiles
    total_score = np.mean(data['scores'][0])
    cmap = matplotlib.cm.get_cmap('RdYlGn')  # PRGn#RdYlGn
    if barrier_free:
        cmap = matplotlib.cm.get_cmap('BrBG')  # PRGn#RdYlGn
    cmap_basic = matplotlib.cm.get_cmap('Blues')
    quantiles = np.arange(0.125, 0.925, 0.05)
    # neg_quantiles= np.arange(0.9,0.9,0.1)
    new_targets, new_sources, new_scores, colors = [], [], [], []
    hoverlabel = []
    for i, flow in enumerate(data['scores']):
        if np.mean(flow) <= 0:
            act_quantiles = np.flip(quantiles)
        else:
            act_quantiles = quantiles
        if isinstance(flow, list) and abs(np.mean(flow) / total_score) > cutoff:
            old_qu_score = 0
            for _, qu in enumerate(act_quantiles):

                new_scores.append(np.quantile(flow, qu) - old_qu_score)
                new_targets.append(data['targets'][i])
                new_sources.append(data['sources'][i])
                if old_qu_score == 0:
                    colors.append('rgba' + str(cmap_basic(0.5, 0.6)))
                    hoverlabel.append('score < 0.125 quantile')
                else:
                    if np.mean(flow) <= 0:
                        colors.append('rgba' + str(cmap(qu - 0.025, 0.9)))
                    else:
                        colors.append('rgba' + str(cmap(1 - qu, 0.9)))
                    hoverlabel.append(
                        f'score between {round(qu - 0.05, 4)} quantile and {round(qu, 4)}'
                        f' quantile ({round(np.quantile(flow, qu), 5)})')

                old_qu_score = np.quantile(flow, qu)

        else:  # Add flows without Monte Carlo datas
            new_scores.append(np.mean(flow))
            new_targets.append(data['targets'][i])
            new_sources.append(data['sources'][i])
            colors.append('rgba' + str(cmap_basic(0.5, 0.6)))
            for _, qu in enumerate(act_quantiles):
                hoverlabel.append(f'score without MonteCarlo calculation ({round(np.quantile(flow, qu), 4)})')
    new_data = {'targets': new_targets, 'sources': new_sources, 'scores': new_scores, 'nodes': data['nodes'],
                'colors': colors, 'metadata': data['metadata']}
    return new_data, hoverlabel


def calc_colors(data, cutoff, barrier_free):
    total_score = np.mean(data['scores'][0])
    if barrier_free:
        cmap_mc = matplotlib.cm.get_cmap('copper')
    else:
        cmap_mc = matplotlib.cm.get_cmap('YlOrRd')
    cmap_smc = matplotlib.cm.get_cmap('Blues')

    max_std = max(np.std(fl) for fl in data['scores'])

    data['colors'] = [0] * len(data['scores'])
    hoverlabel = [0] * len(data['scores'])
    for i, flow in enumerate(data['scores']):
        if isinstance(flow, list) and np.mean(flow) / total_score > cutoff:
            scale = 1 - round(np.std(flow) / max_std, 2)
            color = cmap_mc(scale, 0.9)
            new_color = []
            for k in [0, 1, 2]:
                if color[k] == 1.0:
                    # workaround, because plotly prints the wrong color for "1.0" rgb values:
                    new_color.append(color[k] - 0.000001)
                else:
                    new_color.append(color[k])
            new_color.append(0.9)
            color = tuple(new_color)

        else:  # Add flows without Monte Carlo datas
            color = cmap_smc(0.5, 0.6)
        hoverlabel[i] = f'score: {round(np.mean(flow), 5)}; std: {round(np.std(flow), 5)})'
        data['colors'][i] = 'rgba' + str(color)
        data['scores'][i] = np.mean(flow)
    return data, hoverlabel


def flip_negativ_values(data):
    for i, flow in enumerate(data['scores']):
        if flow <= 0:
            # p= data['targets'][i]
            # data['targets'][i]= data['sources'][i]
            # data['sources'][i]= p
            data['scores'][i] = abs(flow)

    return data


def adjust_data(data, type, cutoff, emission, barrier_free):
    label_list = [data['nodes'][nod]['name'] for nod in data['nodes']]

    data, label_list = cut_off_flows(data, label_list, cutoff)
    if emission:
        data, label_list = calc_emissions(data, label_list)

    if type == 1:
        data, hoverlabel = calc_quantile_flows(data, cutoff, barrier_free)
    elif type == 0:
        data, hoverlabel = calc_colors(data, cutoff, barrier_free)

    # flip negative values:
    data = flip_negativ_values(data)
    return data, label_list, hoverlabel


def generate_sankey(data, type=1, cutoff=0.05, emissions=True, method='', barrier_free=True):
    """Generate a plotly sankey figure with uncertainty. Made for visualizing LCA data from brightway2 activities.

    Parameters
    ----------
    data : dict
        - 'sources': list of int regarding the source nodes from 'nodes'
        - 'targets': list of int regarding the target nodes from 'nodes'
        - 'scores': list of floats/list containing the weight of the links between the nodes from 'nodes'.
            Monte Carlo results are wrapped in a nested list.
        - 'nodes': dictionary containing information about the nodes. Keys are int values.
    type: int
        0 for visualize the uncertainty in form of colored intensity flows in relation to the standard deviation.
        Relative to the highest standard deviation of the links. 1 for visualize the uncertainty by splitting each
        link in several links regarding the ire quantiles with a color scale from low -green to high -red.
    cutoff: float
        Bundle links lower than cutoff value to one target node.
    emissions: bool
        activate or deactivate the emission links. They can be distracting if very low and not relevant.

    Background: https://doi.org/10.1016/j.cola.2019.03.002
    """
    print(data)
    data['metadata'] = {'method': method, 'activity': data['nodes'][0]['name']}

    data, label_list, hoverlabel = adjust_data(data, type, cutoff, emissions, barrier_free)

    # style the figure:
    node_color = ['grey'] * len(label_list)
    node_color[0] = 'white'
    node_line = [dict(color="black", width=0.5)] * len(label_list)
    node_line[0] = dict(color="white", width=0.5)
    label_list[0] = ''

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=80,
            thickness=20,
            line=dict(color="black", width=0.0),
            label=label_list,
            color=node_color,
            customdata=label_list,
            hovertemplate='%{customdata}',
        ),
        link=dict(
            source=data['sources'],
            target=data['targets'],
            value=data['scores'],
            color=data['colors'],
            # arrowlen=10,
            customdata=hoverlabel,
            hovertemplate='%{customdata}',
        ))])

    fig.update_layout(width=1400)
    fig.update_layout(height=800)
    fig.update_layout(title_text=data['metadata']['activity'] + ' - ' + data['metadata']['method'], font_size=12)
    return fig
