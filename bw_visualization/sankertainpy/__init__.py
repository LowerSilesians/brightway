from .sankertainpy import recursive_calculation_to_plotly, generate_sankey


def plot(data):
    result = recursive_calculation_to_plotly(**data)
    fig = generate_sankey(result, type=1)
    return fig
