import numpy as np
import pandas as pd

WEIGHT_SUM_TOLERANCE = 1e-9
MINIMUM_SPATIAL_UNITS = 2


def indicator_proportions(normalized: pd.DataFrame) -> pd.DataFrame:
    totals = normalized.sum(axis=0)
    assert (totals > 0).all(), (
        "indicators with no positive normalized value to form a proportion: "
        f"{totals[totals <= 0].index.tolist()}"
    )
    return normalized.divide(totals, axis=1)


def entropy_values(proportions: pd.DataFrame) -> pd.Series:
    spatial_units = len(proportions)
    assert spatial_units >= MINIMUM_SPATIAL_UNITS, (
        f"entropy weighting needs at least {MINIMUM_SPATIAL_UNITS} spatial units, found {spatial_units}"
    )

    constant = 1.0 / np.log(spatial_units)
    positive = proportions > 0
    logarithms = pd.DataFrame(
        np.where(positive, np.log(proportions.where(positive, 1.0)), 0.0),
        index=proportions.index,
        columns=proportions.columns,
    )
    return -constant * (proportions * logarithms).sum(axis=0)


def diversification_degrees(entropy: pd.Series) -> pd.Series:
    return 1.0 - entropy


def entropy_weights(entropy: pd.Series) -> pd.Series:
    diversification = diversification_degrees(entropy)
    total = float(diversification.sum())
    assert total > 0, "every indicator has zero diversification, so no weights can be derived"

    weights = diversification / total
    assert abs(float(weights.sum()) - 1.0) <= WEIGHT_SUM_TOLERANCE, (
        f"entropy weights sum to {weights.sum()}, expected 1 within {WEIGHT_SUM_TOLERANCE}"
    )
    assert (weights >= 0.0).all(), "entropy weights must not be negative"
    return weights


def weights_from_normalized(normalized: pd.DataFrame) -> pd.Series:
    return entropy_weights(entropy_values(indicator_proportions(normalized)))
