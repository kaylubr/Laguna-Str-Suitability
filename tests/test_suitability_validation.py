import pandas as pd
import pytest

from str_suitability.config import SUITABILITY_INDICATORS
from str_suitability.suitability.validate import (
    assert_within_unit_interval,
    validate_suitability_inputs,
)


def make_grid(overrides: dict | None = None) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "cell_id": ["a", "b"],
            "predicted_revenue": [1000.0, 2000.0],
            "predicted_occupancy": [0.1, 0.2],
            "poi_density_total": [3.0, 4.0],
            "distance_to_nearest_tourist_attraction": [1.5, 2.5],
            "distance_to_nearest_transportation_facility": [0.5, 0.7],
        }
    )
    if overrides:
        frame = frame.assign(**overrides)
    return frame


def test_validation_accepts_a_complete_grid():
    report = validate_suitability_inputs(make_grid())
    assert report["cells"] == 2
    assert len(report["indicators"]) == 5


def test_indicator_set_is_exactly_the_five_thesis_indicators():
    assert len(SUITABILITY_INDICATORS) == 5
    assert "population_density_per_km2" not in SUITABILITY_INDICATORS
    assert "poi_density_total" in SUITABILITY_INDICATORS


def test_validation_rejects_duplicate_cells():
    duplicated = make_grid()
    duplicated.loc[1, "cell_id"] = "a"
    with pytest.raises(AssertionError, match="duplicate cell_id"):
        validate_suitability_inputs(duplicated)


def test_validation_rejects_a_missing_indicator():
    incomplete = make_grid().drop(columns=["poi_density_total"])
    with pytest.raises(AssertionError, match="missing suitability indicators"):
        validate_suitability_inputs(incomplete)


def test_validation_rejects_a_null_indicator():
    incomplete = make_grid({"poi_density_total": [3.0, None]})
    with pytest.raises(AssertionError, match="incomplete"):
        validate_suitability_inputs(incomplete)


def test_unit_interval_assertion_accepts_normalized_values():
    frame = pd.DataFrame({"x": [0.0, 0.5, 1.0]})
    assert_within_unit_interval(frame, ["x"])


def test_unit_interval_assertion_rejects_out_of_range_values():
    with pytest.raises(AssertionError, match="above 1"):
        assert_within_unit_interval(pd.DataFrame({"x": [0.0, 1.4]}), ["x"])
    with pytest.raises(AssertionError, match="below 0"):
        assert_within_unit_interval(pd.DataFrame({"x": [-0.2, 1.0]}), ["x"])


def test_unit_interval_assertion_rejects_nulls():
    with pytest.raises(AssertionError, match="nulls"):
        assert_within_unit_interval(pd.DataFrame({"x": [0.5, None]}), ["x"])
