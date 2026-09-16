import pytest

from str_suitability.modeling.evaluate import describe_target, regression_metrics


def test_regression_metrics_match_hand_computed_values():
    metrics = regression_metrics([1.0, 2.0, 3.0], [1.0, 2.0, 4.0])
    assert metrics["mae"] == pytest.approx(1 / 3)
    assert metrics["rmse"] == pytest.approx((1 / 3) ** 0.5)
    assert metrics["r2"] == pytest.approx(0.5)
    assert metrics["n"] == 3


def test_perfect_prediction_gives_zero_error_and_unit_r2():
    metrics = regression_metrics([10.0, 20.0, 30.0], [10.0, 20.0, 30.0])
    assert metrics["mae"] == 0.0
    assert metrics["rmse"] == 0.0
    assert metrics["r2"] == 1.0


def test_rmse_is_never_below_mae():
    observed = [1.0, 2.0, 3.0, 4.0]
    predicted = [1.5, 2.5, 2.0, 5.0]
    metrics = regression_metrics(observed, predicted)
    assert metrics["rmse"] >= metrics["mae"]


def test_describe_target_reports_untrimmed_extremes():
    description = describe_target([100.0, 200.0, 300.0, 10000.0])
    assert description["max"] == 10000.0
    assert description["count"] == 4
    assert description["skew"] > 0


def test_describe_target_handles_constant_series():
    description = describe_target([5.0, 5.0, 5.0])
    assert description["skew"] == 0.0
