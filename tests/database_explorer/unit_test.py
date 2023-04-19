from pprint import pprint
import pytest

from bw_visualization.database_explorer.utils import (
    JRCAssumedDiagonalGraphTraversal,
)
from bw_visualization.database_explorer.database_explorer import (
    ListAct,
)
import numpy as np
import pandas as pd

from .utils import sample_1


LCA, ACT, METHODS_EF, METHODS_CC, DB = sample_1()


@pytest.mark.parametrize(
    ('lca', 'expected'),
    [
        (LCA, None)
    ]
)
def test_calculate_success(lca, expected):
    result = JRCAssumedDiagonalGraphTraversal().calculate(lca)
    assert result.get('counter') is not None
    assert result.get('edges') is not None
    assert result.get('nodes') is not None


@pytest.mark.parametrize(
    ('lca', 'expected'),
    [
        (LCA, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_calculate_fail(lca, expected):
    result = JRCAssumedDiagonalGraphTraversal().calculate(lca)
    assert result.get('counter') is None
    assert result.get('edges') is None
    assert result.get('nodes') is None


@pytest.mark.parametrize(
    ('lca', 'expected'),
    [
        (LCA, None)
    ]
)
def test_initialize_heap_success(lca, expected):
    supply = lca.supply_array.copy()
    characterized_biosphere = np.array(
        (lca.characterization_matrix * lca.biosphere_matrix).sum(axis=0)
    ).ravel()
    characterized_biosphere_neg = characterized_biosphere.copy()
    characterized_biosphere_neg[characterized_biosphere_neg > 0] = 0
    characterized_biosphere_pos = characterized_biosphere.copy()
    characterized_biosphere_pos[characterized_biosphere_pos < 0] = 0
    result = JRCAssumedDiagonalGraphTraversal().initialize_heap(lca, supply, characterized_biosphere,
                                                                characterized_biosphere_neg, characterized_biosphere_pos)
    assert result[0] is not None
    assert result[1] is not None
    assert result[2] is not None


@pytest.mark.parametrize(
    ('lca', 'expected'),
    [
        (LCA, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_initialize_heap_fail(lca, expected):
    supply = lca.supply_array.copy()
    characterized_biosphere = np.array(
        (lca.characterization_matrix * lca.biosphere_matrix).sum(axis=0)
    ).ravel()
    characterized_biosphere_neg = characterized_biosphere.copy()
    characterized_biosphere_neg[characterized_biosphere_neg > 0] = 0
    characterized_biosphere_pos = characterized_biosphere.copy()
    characterized_biosphere_pos[characterized_biosphere_pos < 0] = 0
    result = JRCAssumedDiagonalGraphTraversal().initialize_heap(lca, supply, characterized_biosphere,
                                                                characterized_biosphere_neg, characterized_biosphere_pos)
    assert result[0] is None
    assert result[1] is None
    assert result[2] is None


@pytest.mark.parametrize(
    ('lca', 'expected'),
    [
        (LCA, None)
    ]
)
def test_cumulative_score_success(lca, expected):
    supply = lca.supply_array.copy()
    characterized_biosphere = np.array(
        (lca.characterization_matrix * lca.biosphere_matrix).sum(axis=0)
    ).ravel()
    characterized_biosphere_neg = characterized_biosphere.copy()
    characterized_biosphere_neg[characterized_biosphere_neg > 0] = 0
    characterized_biosphere_pos = characterized_biosphere.copy()
    characterized_biosphere_pos[characterized_biosphere_pos < 0] = 0
    result = JRCAssumedDiagonalGraphTraversal().cumulative_score(0, supply, characterized_biosphere,
                                                                characterized_biosphere_neg, characterized_biosphere_pos, lca)
    assert result[0] is not None
    assert result[1] is not None
    assert result[2] is not None


@pytest.mark.parametrize(
    ('lca', 'expected'),
    [
        (LCA, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_cumulative_score_fail(lca, expected):
    supply = lca.supply_array.copy()
    characterized_biosphere = np.array(
        (lca.characterization_matrix * lca.biosphere_matrix).sum(axis=0)
    ).ravel()
    characterized_biosphere_neg = characterized_biosphere.copy()
    characterized_biosphere_neg[characterized_biosphere_neg > 0] = 0
    characterized_biosphere_pos = characterized_biosphere.copy()
    characterized_biosphere_pos[characterized_biosphere_pos < 0] = 0
    result = JRCAssumedDiagonalGraphTraversal().cumulative_score(0, supply, characterized_biosphere,
                                                                characterized_biosphere_neg, characterized_biosphere_pos, lca)
    assert result[0] is None
    assert result[1] is None
    assert result[2] is None


@pytest.mark.parametrize(
    ('lca', 'expected'),
    [
        (LCA, None)
    ]
)
def test_unit_score_success(lca, expected):
    supply = lca.supply_array.copy()
    characterized_biosphere = np.array(
        (lca.characterization_matrix * lca.biosphere_matrix).sum(axis=0)
    ).ravel()
    result = JRCAssumedDiagonalGraphTraversal().unit_score(0, supply, characterized_biosphere)
    assert result is not None


@pytest.mark.parametrize(
    ('lca', 'expected'),
    [
        (LCA, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_unit_score_fail(lca, expected):
    supply = lca.supply_array.copy()
    characterized_biosphere = np.array(
        (lca.characterization_matrix * lca.biosphere_matrix).sum(axis=0)
    ).ravel()
    result = JRCAssumedDiagonalGraphTraversal().unit_score(0, supply, characterized_biosphere)
    assert result is None


@pytest.mark.parametrize(
    ('lca', 'expected'),
    [
        (LCA, None)
    ]
)
def test_traverse_success(lca, expected):
    supply = lca.supply_array.copy()
    score = lca.score
    characterized_biosphere = np.array(
        (lca.characterization_matrix * lca.biosphere_matrix).sum(axis=0)
    ).ravel()
    characterized_biosphere_neg = characterized_biosphere.copy()
    characterized_biosphere_neg[characterized_biosphere_neg > 0] = 0
    characterized_biosphere_pos = characterized_biosphere.copy()
    characterized_biosphere_pos[characterized_biosphere_pos < 0] = 0
    result = JRCAssumedDiagonalGraphTraversal().traverse(
        [], {}, [], 0, 1e5, 0.005, score, supply, characterized_biosphere, characterized_biosphere_neg, characterized_biosphere_pos, lca, False
    )
    assert result[0] is not None
    assert result[1] is not None
    assert result[2] is not None


@pytest.mark.parametrize(
    ('lca', 'expected'),
    [
        (LCA, None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_traverse_fail(lca, expected):
    supply = lca.supply_array.copy()
    score = lca.score
    characterized_biosphere = np.array(
        (lca.characterization_matrix * lca.biosphere_matrix).sum(axis=0)
    ).ravel()
    characterized_biosphere_neg = characterized_biosphere.copy()
    characterized_biosphere_neg[characterized_biosphere_neg > 0] = 0
    characterized_biosphere_pos = characterized_biosphere.copy()
    characterized_biosphere_pos[characterized_biosphere_pos < 0] = 0
    result = JRCAssumedDiagonalGraphTraversal().traverse(
        [], {}, [], 0, 1e5, 0.005, score, supply, characterized_biosphere, characterized_biosphere_neg, characterized_biosphere_pos, lca, False
    )
    assert result[0] is None
    assert result[1] is None
    assert result[2] is None


@pytest.mark.parametrize(
    ('list_act', 'expected'),
    [
        (ListAct(DB, ACT['name'], METHODS_EF, METHODS_EF, ACT['location'], ACT['unit']), [ACT])
    ]
)
def test_list_act_search_success(list_act, expected):
    list_act.search()
    result = list_act.list_act
    assert result == expected


@pytest.mark.parametrize(
    ('list_act', 'expected'),
    [
        (ListAct(DB, ACT['name'], METHODS_EF, METHODS_EF, ACT['location'], ACT['unit']), [])
    ]
)
@pytest.mark.xfail(strict=True)
def test_list_act_search_fail(list_act, expected):
    list_act.search()
    result = list_act.list_act
    assert result == expected


@pytest.mark.parametrize(
    ('list_act', 'expected'),
    [
        (ListAct(DB, ACT['name'], METHODS_EF, METHODS_EF, ACT['location'], ACT['unit']), {ACT['name'], })
    ]
)
def test_list_act_get_list_success(list_act, expected):
    list_act.search()
    result = list_act.get_list('name')
    assert result == expected


@pytest.mark.parametrize(
    ('list_act', 'expected'),
    [
        (ListAct(DB, ACT['name'], METHODS_EF, METHODS_EF, ACT['location'], ACT['unit']), {})
    ]
)
@pytest.mark.xfail(strict=True)
def test_list_act_get_list_fail(list_act, expected):
    list_act.search()
    result = list_act.get_list('name')
    assert result == expected


@pytest.mark.parametrize(
    ('list_act', 'expected'),
    [
        (ListAct(DB, ACT['name'], METHODS_EF, METHODS_EF, ACT['location'], ACT['unit']), ACT['name'])
    ]
)
def test_list_act_get_inventory_success(list_act, expected):
    list_act.search()
    result = list_act.get_inventory(0)
    assert expected in list(result['source_name'])


@pytest.mark.parametrize(
    ('list_act', 'expected'),
    [
        (ListAct(DB, ACT['name'], METHODS_EF, METHODS_EF, ACT['location'], ACT['unit']), '')
    ]
)
@pytest.mark.xfail(strict=True)
def test_list_act_get_inventory_fail(list_act, expected):
    list_act.search()
    result = list_act.get_inventory(0)
    assert expected in list(result['source_name'])


@pytest.mark.parametrize(
    ('list_act', 'expected'),
    [
        (ListAct(DB, ACT['name'], METHODS_EF, METHODS_EF, ACT['location'], ACT['unit']), None)
    ]
)
def test_list_act_get_inventories_success(list_act, expected):
    list_act.search()
    list_act.get_inventories()
    result = list_act.dataframe
    assert result is not None


@pytest.mark.parametrize(
    ('list_act', 'expected'),
    [
        (ListAct(DB, ACT['name'], METHODS_EF, METHODS_EF, ACT['location'], ACT['unit']), None)
    ]
)
@pytest.mark.xfail(strict=True)
def test_list_act_get_inventories_fail(list_act, expected):
    list_act.search()
    list_act.get_inventories()
    result = list_act.dataframe
    assert result is None
