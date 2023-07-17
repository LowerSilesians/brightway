from plotly.graph_objects import Figure

from .sankertainpy import generate_sankey
from .utils import recursive_calculation_to_plotly


def plot(data, method) -> Figure:
    result = recursive_calculation_to_plotly(data, method)
    return generate_sankey(result, type=1)


__all__ = ['plot', 'generate_sankey', 'recursive_calculation_to_plotly']
