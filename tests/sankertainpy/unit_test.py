from pprint import pprint
import pytest

from bw_visualization.sankertainpy.utils import (
    update_or_create_nodes,
    calculate_score,
    recursive_calculation_to_plotly,
)
from bw_visualization.sankertainpy.sankertainpy import (
    cut_off_flows,
    add_emissions,
    calc_emissions,
    calc_quantile_flows,
    calc_colors,
    flip_negativ_values,
    adjust_data,
)

from .utils import sample_1


ACT, METHOD = sample_1()


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
def test_update_or_create_nodes_success(act, method, expected):
    result = update_or_create_nodes(None, act, None, None, None, None, None)

    assert result[0] is not None
    assert result[1] is not None
    assert result[2] is not None
    assert result[3] is not None
    assert result[4] is not None
    assert result[5] is not None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_update_or_create_nodes_fail(act, method, expected):
    result = update_or_create_nodes(None, act, None, None, None, None, None)

    assert result[0] is None
    assert result[1] is None
    assert result[2] is None
    assert result[3] is None
    assert result[4] is None
    assert result[5] is None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
def test_calculate_score_success(act, method, expected):
    result = calculate_score(act, None, False, 1, method, 100, None, 1e-2)

    assert result[0] is not None
    assert result[1] is not None
    assert result[2] is not None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_calculate_score_fail(act, method, expected):
    result = calculate_score(act, None, False, 1, method, 100, None, 1e-2)

    assert result[0] is None
    assert result[1] is None
    assert result[2] is None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
def test_recursive_calculation_to_plotly_success(act, method, expected):
    result = recursive_calculation_to_plotly(act, method)

    assert result['targets'] is not None
    assert result['sources'] is not None
    assert result['scores'] is not None
    assert result['nodes'] is not None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_recursive_calculation_to_plotly_fail(act, method, expected):
    result = recursive_calculation_to_plotly(act, method)

    assert result['targets'] is None
    assert result['sources'] is None
    assert result['scores'] is None
    assert result['nodes'] is None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
def test_cut_off_flows_success(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    label_list = [data['nodes'][nod]['name'] for nod in data['nodes']]
    result = cut_off_flows(data, label_list, 0.05)

    assert result[0] is not None
    assert result[1] is not None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_cut_off_flows_fail(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    label_list = [data['nodes'][nod]['name'] for nod in data['nodes']]
    result = cut_off_flows(data, label_list, 0.05)

    assert result[0] is None
    assert result[1] is None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
def test_adjust_data_success(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    data['metadata'] = {'method': method, 'activity': data['nodes'][0]['name']}
    result = adjust_data(data, 1, 0.05, True, True)

    assert result[0] is not None
    assert result[1] is not None
    assert result[2] is not None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_adjust_data_fail(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    data['metadata'] = {'method': method, 'activity': data['nodes'][0]['name']}
    result = adjust_data(data, 1, 0.05, True, True)

    assert result[0] is None
    assert result[1] is None
    assert result[2] is None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
def test_add_emissions_success(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    label_list = [data['nodes'][nod]['name'] for nod in data['nodes']]
    result = add_emissions(0, data, label_list, len(label_list), len(label_list))

    assert result[0] is not None
    assert result[1] is not None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_add_emissions_fail(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    label_list = [data['nodes'][nod]['name'] for nod in data['nodes']]
    result = add_emissions(0, data, label_list, len(label_list), len(label_list))

    assert result[0] is None
    assert result[1] is None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
def test_calc_emissions_success(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    label_list = [data['nodes'][nod]['name'] for nod in data['nodes']]
    result = calc_emissions(data, label_list)

    assert result[0] is not None
    assert result[1] is not None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_calc_emissions_fail(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    label_list = [data['nodes'][nod]['name'] for nod in data['nodes']]
    result = calc_emissions(data, label_list)

    assert result[0] is None
    assert result[1] is None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
def test_calc_quantile_flows_success(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    data['metadata'] = {'method': method, 'activity': data['nodes'][0]['name']}
    result = calc_quantile_flows(data, 0.05, True)

    assert result[0] is not None
    assert result[1] is not None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_calc_quantile_flows_fail(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    data['metadata'] = {'method': method, 'activity': data['nodes'][0]['name']}
    result = calc_quantile_flows(data, 0.05, True)

    assert result[0] is None
    assert result[1] is None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
def test_calc_colors_success(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    result = calc_colors(data, 0.05, True)

    assert result[0] is not None
    assert result[1] is not None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_calc_colors_fail(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    result = calc_colors(data, 0.05, True)

    assert result[0] is None
    assert result[1] is None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
def test_flip_negativ_values_success(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    result = flip_negativ_values(data)

    assert result is not None


@pytest.mark.parametrize(
    ('act', 'method', 'expected'),
    [
        (ACT, METHOD, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_flip_negativ_values_fail(act, method, expected):
    data = recursive_calculation_to_plotly(act, method)
    result = flip_negativ_values(data)

    assert result is None
