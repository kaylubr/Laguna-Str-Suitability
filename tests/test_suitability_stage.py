import warnings

import numpy as np
import pandas as pd
import pytest

from str_suitability.suitability.classify import (
    CLASS_LABELS,
    SUITABILITY_CLASS_COLUMN,
    classify_suitability,
)
from str_suitability.suitability.composite_score import (
    COMPOSITE_SCORE_COLUMN,
    composite_suitability_score,
)
from str_suitability.suitability.entropy_weights import (
    diversification_degrees,
    entropy_values,
    entropy_weights,
    indicator_proportions,
    weights_from_normalized,
)
from str_suitability.suitability.normalize import (
    indicator_from_normalized,
    minimum_maximum_normalize,
    normalized_column,
)
from str_suitability.suitability.stage import compute_suitability

INDICATORS = (
    "predicted_revenue",
    "predicted_occupancy",
    "poi_density_total",
    "distance_to_nearest_tourist_attraction",
    "distance_to_nearest_transportation_facility",
)


def make_frame(**columns) -> pd.DataFrame:
    frame = pd.DataFrame({"cell_id": [f"c{index}" for index in range(len(next(iter(columns.values()))))]})
    return frame.assign(**columns)


def make_grid(rows: int = 10) -> pd.DataFrame:
    return make_frame(
        predicted_revenue=[1000.0 + 100 * index for index in range(rows)],
        predicted_occupancy=[0.1 + 0.01 * index for index in range(rows)],
        poi_density_total=[1.0 + index for index in range(rows)],
        distance_to_nearest_tourist_attraction=[10.0 - index for index in range(rows)],
        distance_to_nearest_transportation_facility=[5.0 - 0.5 * index for index in range(rows)],
    )


def test_positive_indicators_use_min_max_normalization():
    grid = make_grid(3)
    grid["predicted_revenue"] = [10.0, 20.0, 30.0]
    normalized = minimum_maximum_normalize(grid)
    assert normalized[normalized_column("predicted_revenue")].tolist() == [0.0, 0.5, 1.0]


def test_negative_indicators_use_reverse_min_max_normalization():
    grid = make_grid(3)
    grid["distance_to_nearest_tourist_attraction"] = [0.0, 10.0, 20.0]
    normalized = minimum_maximum_normalize(grid)
    assert normalized[normalized_column("distance_to_nearest_tourist_attraction")].tolist() == [
        1.0,
        0.5,
        0.0,
    ]


def test_normalized_values_stay_within_the_unit_interval():
    normalized = minimum_maximum_normalize(make_grid(25))
    assert normalized.shape[1] == 5
    assert normalized.min().min() >= 0.0
    assert normalized.max().max() <= 1.0


def test_normalized_columns_are_named_for_their_indicator():
    normalized = minimum_maximum_normalize(make_grid(4))
    assert list(normalized.columns) == [normalized_column(name) for name in INDICATORS]
    assert indicator_from_normalized(normalized_column("poi_density_total")) == "poi_density_total"


def test_zero_variance_indicator_is_rejected_rather_than_divided_by_zero():
    grid = make_grid(5)
    grid["poi_density_total"] = 7.0
    with pytest.raises(AssertionError, match="no span to divide by"):
        minimum_maximum_normalize(grid)


def test_proportions_sum_to_one_within_each_indicator():
    normalized = minimum_maximum_normalize(make_grid(8))
    proportions = indicator_proportions(normalized)
    assert np.allclose(proportions.sum(axis=0).to_numpy(), 1.0)


def test_uniform_proportions_have_maximum_entropy():
    proportions = pd.DataFrame({"z": [1 / 3, 1 / 3, 1 / 3]})
    assert entropy_values(proportions)["z"] == pytest.approx(1.0)


def test_concentrated_proportions_have_zero_entropy():
    proportions = pd.DataFrame({"z": [1.0, 0.0, 0.0]})
    assert entropy_values(proportions)["z"] == pytest.approx(0.0)


def test_zero_proportion_contributes_nothing_and_raises_no_log_error():
    proportions = pd.DataFrame({"z": [0.5, 0.5, 0.0, 0.0]})
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        entropy = entropy_values(proportions)
    assert np.isfinite(entropy["z"])
    assert entropy["z"] == pytest.approx(np.log(2.0) / np.log(4.0))


def test_entropy_matches_an_independently_computed_value():
    proportions = pd.DataFrame({"z": [0.2, 0.3, 0.5]})
    expected = -(1.0 / np.log(3.0)) * sum(
        value * np.log(value) for value in [0.2, 0.3, 0.5]
    )
    assert entropy_values(proportions)["z"] == pytest.approx(expected)


def test_diversification_is_one_minus_entropy():
    entropy = pd.Series({"a": 1.0, "b": 0.0, "c": 0.4})
    assert diversification_degrees(entropy).tolist() == [0.0, 1.0, pytest.approx(0.6)]
    assert (diversification_degrees(entropy) + entropy == 1.0).all()


def test_entropy_weights_sum_to_one():
    weights = weights_from_normalized(minimum_maximum_normalize(make_grid(30)))
    assert len(weights) == 5
    assert weights.sum() == pytest.approx(1.0)
    assert (weights >= 0.0).all()


def test_entropy_weights_favour_the_more_varied_indicator():
    entropy = pd.Series({"varied": 0.0, "uniform": 1.0})
    weights = entropy_weights(entropy)
    assert weights["varied"] == pytest.approx(1.0)
    assert weights["uniform"] == pytest.approx(0.0)


def test_entropy_weights_reject_a_degenerate_entropy_vector():
    with pytest.raises(AssertionError, match="zero diversification"):
        entropy_weights(pd.Series({"a": 1.0, "b": 1.0}))


def test_composite_score_is_the_weighted_sum_of_normalized_indicators():
    normalized = pd.DataFrame({"normalized_a": [0.0, 1.0], "normalized_b": [1.0, 0.0]})
    weights = pd.Series({"normalized_a": 0.25, "normalized_b": 0.75})
    scores = composite_suitability_score(normalized, weights)
    assert scores.tolist() == [0.75, 0.25]


def test_composite_score_requires_a_weight_per_indicator():
    normalized = pd.DataFrame({"normalized_a": [0.0, 1.0]})
    with pytest.raises(AssertionError, match="without an entropy weight"):
        composite_suitability_score(normalized, pd.Series({"normalized_b": 1.0}))


def test_classification_returns_exactly_five_classes():
    scores = pd.Series(np.linspace(0.1, 1.0, 20))
    labels, report = classify_suitability(scores)
    assert labels.nunique() == 5
    assert list(CLASS_LABELS) == [
        "Very Low / Unsuitable",
        "Low Suitability",
        "Moderate Suitability",
        "High Suitability",
        "Very High Suitability",
    ]
    assert sum(report["class_counts"].values()) == len(scores)


def test_classification_orders_labels_by_score():
    scores = pd.Series([0.1, 0.2, 0.3, 0.9, 1.0])
    labels, _ = classify_suitability(scores)
    assert labels.iloc[-1] == "Very High Suitability"
    assert labels.iloc[0] == "Very Low / Unsuitable"


def test_stage_scores_and_classifies_every_cell():
    grid = make_grid(20)
    scored, report = compute_suitability(grid)
    assert len(scored) == len(grid)
    assert report["cells_with_score"] == len(grid)
    assert report["cells_with_class"] == len(grid)
    assert scored[COMPOSITE_SCORE_COLUMN].notna().all()
    assert scored[SUITABILITY_CLASS_COLUMN].notna().all()
    assert scored[COMPOSITE_SCORE_COLUMN].min() == pytest.approx(report["score_min"])
    assert scored[COMPOSITE_SCORE_COLUMN].max() == pytest.approx(report["score_max"])


def test_stage_reports_weights_that_sum_to_one():
    _, report = compute_suitability(make_grid(30))
    assert sum(report["weights"].values()) == pytest.approx(1.0)
    assert report["weight_sum"] == pytest.approx(1.0)
    assert set(report["weights"]) == set(INDICATORS)


def test_classification_is_reproducible_across_repeated_calls():
    scores = pd.Series(np.linspace(0.1, 1.0, 60))
    runs = [classify_suitability(scores)[0] for _ in range(5)]
    for labels in runs[1:]:
        pd.testing.assert_series_equal(labels, runs[0])


def test_stage_is_deterministic():
    first, _ = compute_suitability(make_grid(15))
    second, _ = compute_suitability(make_grid(15))
    pd.testing.assert_series_equal(
        first[COMPOSITE_SCORE_COLUMN], second[COMPOSITE_SCORE_COLUMN]
    )
    pd.testing.assert_series_equal(
        first[SUITABILITY_CLASS_COLUMN], second[SUITABILITY_CLASS_COLUMN]
    )


def test_stage_scores_are_bounded_by_the_weights():
    scored, report = compute_suitability(make_grid(20))
    assert scored[COMPOSITE_SCORE_COLUMN].min() >= 0.0
    assert scored[COMPOSITE_SCORE_COLUMN].max() <= 1.0
    assert report["score_min"] >= 0.0
    assert report["score_max"] <= 1.0


def test_stage_keeps_the_indicator_columns_untouched():
    grid = make_grid(12)
    scored, _ = compute_suitability(grid)
    for indicator in INDICATORS:
        pd.testing.assert_series_equal(scored[indicator], grid[indicator])
