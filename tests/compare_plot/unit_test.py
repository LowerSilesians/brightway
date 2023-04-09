import pytest

from bw_visualization.compare_plot.utils import (
    lca_comparison,
    act_topscore,
    contributions_df,
)

from .utils import sample_1

FU, METHODS, METHOD_REF = sample_1()


@pytest.mark.parametrize(
    ('fu', 'methods', 'method_ref', 'expected'),
    [
        (FU, METHODS, METHOD_REF, set(METHODS)),
    ]
)
def test_lca_comparison_success(fu, methods, method_ref, expected):
    result = lca_comparison(fu, methods, method_ref)
    assert expected == set(result.to_dict().keys())


@pytest.mark.parametrize(
    ('fu', 'methods', 'method_ref', 'expected'),
    [
        (FU, METHODS[1:], METHOD_REF, set(METHODS))
    ]
)
@pytest.mark.xfail(strict=True)
def test_lca_comparison_fail(fu, methods, method_ref, expected):
    result = lca_comparison(fu, methods, method_ref)
    assert expected == set(result.to_dict().keys())


@pytest.mark.parametrize(
    ('fu', 'method_ref', 'expected'),
    [
        (FU, METHOD_REF, list(FU.keys())[1]),
    ]
)
def test_act_topscore_success(fu, method_ref, expected):
    result = act_topscore(fu, method_ref)
    assert expected == result


@pytest.mark.parametrize(
    ('fu', 'method_ref', 'expected'),
    [
        (FU, METHOD_REF, list(FU.keys())[0])
    ]
)
@pytest.mark.xfail(strict=True)
def test_act_topscore_fail(fu, method_ref, expected):
    result = act_topscore(fu, method_ref)
    assert expected == result


@pytest.mark.parametrize(
    ('activity', 'method', 'expected'),
    [
        (list(FU.keys())[0], METHOD_REF, METHOD_REF)
    ]
)
def test_contributions_df_success(activity, method, expected):
    result = contributions_df(activity, method)
    assert expected == list(result.to_dict().keys())[0]


@pytest.mark.parametrize(
    ('activity', 'method', 'expected'),
    [
        (list(FU.keys())[0], METHODS[2], METHOD_REF)
    ]
)
@pytest.mark.xfail(strict=True)
def test_contributions_df_fail(activity, method, expected):
    result = contributions_df(activity, method)
    assert expected == list(result.to_dict().keys())[0]
