import pandas as pd

from str_suitability.config import SUITABILITY_INDICATOR_DIRECTIONS, SUITABILITY_INDICATORS
from str_suitability.spatial.grid import assert_one_row_per_cell

EXPECTED_INDICATOR_COUNT = 5


def validate_suitability_inputs(grid: pd.DataFrame) -> dict[str, object]:
    assert_one_row_per_cell(grid)
    assert len(SUITABILITY_INDICATORS) == EXPECTED_INDICATOR_COUNT, (
        f"the methodology specifies {EXPECTED_INDICATOR_COUNT} indicators, "
        f"found {len(SUITABILITY_INDICATORS)}"
    )

    absent = [name for name in SUITABILITY_INDICATORS if name not in grid.columns]
    assert not absent, f"missing suitability indicators: {absent}"

    null_counts = grid[list(SUITABILITY_INDICATORS)].isna().sum()
    incomplete = {name: int(count) for name, count in null_counts.items() if count > 0}
    assert not incomplete, f"suitability indicators are incomplete: {incomplete}"

    return {
        "cells": int(len(grid)),
        "indicators": list(SUITABILITY_INDICATORS),
        "directions": dict(SUITABILITY_INDICATOR_DIRECTIONS),
    }


def assert_within_unit_interval(frame: pd.DataFrame, columns: list[str]) -> None:
    for column in columns:
        values = pd.to_numeric(frame[column], errors="coerce")
        assert values.notna().all(), f"normalized indicator {column} contains nulls"
        assert values.min() >= 0.0, f"normalized indicator {column} below 0: {values.min()}"
        assert values.max() <= 1.0, f"normalized indicator {column} above 1: {values.max()}"
