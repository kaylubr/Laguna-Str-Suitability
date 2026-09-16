import pandas as pd

COMPOSITE_SCORE_COLUMN = "composite_suitability_score"


def composite_suitability_score(normalized: pd.DataFrame, weights: pd.Series) -> pd.Series:
    aligned = weights.reindex(normalized.columns)
    assert aligned.notna().all(), (
        f"normalized indicators without an entropy weight: {aligned[aligned.isna()].index.tolist()}"
    )
    scores = (normalized * aligned).sum(axis=1)
    assert scores.notna().all(), "composite suitability score contains missing values"
    return scores
