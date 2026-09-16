import numpy as np
import pandas as pd

from str_suitability.config import SUITABILITY_INDICATOR_DIRECTIONS, SUITABILITY_INDICATORS
from str_suitability.suitability.validate import (
    assert_within_unit_interval,
    validate_suitability_inputs,
)

NORMALIZED_PREFIX = "normalized_"
POSITIVE_DIRECTION = "positive"
NEGATIVE_DIRECTION = "negative"


def normalized_column(indicator: str) -> str:
    return f"{NORMALIZED_PREFIX}{indicator}"


def indicator_from_normalized(column: str) -> str:
    return column.removeprefix(NORMALIZED_PREFIX)


def minimum_maximum_normalize(grid: pd.DataFrame) -> pd.DataFrame:
    validate_suitability_inputs(grid)

    normalized = pd.DataFrame(index=grid.index)
    for indicator in SUITABILITY_INDICATORS:
        values = pd.to_numeric(grid[indicator], errors="raise").astype(float)
        minimum = float(values.min())
        maximum = float(values.max())
        assert maximum > minimum, (
            f"indicator {indicator} takes the single value {minimum} across all cells, "
            "so min-max normalization has no span to divide by"
        )

        span = maximum - minimum
        direction = SUITABILITY_INDICATOR_DIRECTIONS[indicator]
        if direction == NEGATIVE_DIRECTION:
            normalized[normalized_column(indicator)] = (maximum - values) / span
        elif direction == POSITIVE_DIRECTION:
            normalized[normalized_column(indicator)] = (values - minimum) / span
        else:
            raise ValueError(f"indicator {indicator} has an unknown direction: {direction}")

    assert_within_unit_interval(normalized, list(normalized.columns))
    return normalized
