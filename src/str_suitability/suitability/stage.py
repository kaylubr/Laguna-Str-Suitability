import pandas as pd

from str_suitability.config import SUITABILITY_INDICATORS
from str_suitability.suitability.classify import (
    CLASS_COUNT,
    CLASS_LABELS,
    CLASSIFICATION_METHOD,
    SUITABILITY_CLASS_COLUMN,
    classify_suitability,
)
from str_suitability.suitability.composite_score import (
    COMPOSITE_SCORE_COLUMN,
    composite_suitability_score,
)
from str_suitability.suitability.entropy_weights import weights_from_normalized
from str_suitability.suitability.normalize import indicator_from_normalized, minimum_maximum_normalize


def compute_suitability(grid: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    normalized = minimum_maximum_normalize(grid)
    weights = weights_from_normalized(normalized)
    scores = composite_suitability_score(normalized, weights)
    labels, classification_report = classify_suitability(scores)

    result = grid.copy()
    for column in normalized.columns:
        result[column] = normalized[column]
    result[COMPOSITE_SCORE_COLUMN] = scores
    result[SUITABILITY_CLASS_COLUMN] = labels

    assert result[COMPOSITE_SCORE_COLUMN].notna().all(), (
        "every retained grid cell must carry a composite suitability score"
    )
    assert result[SUITABILITY_CLASS_COLUMN].notna().all(), (
        "every retained grid cell must carry a suitability class"
    )

    report = {
        "cells": int(len(result)),
        "indicators": list(SUITABILITY_INDICATORS),
        "class_count": CLASS_COUNT,
        "classification_method": CLASSIFICATION_METHOD,
        "weights": {
            indicator_from_normalized(column): float(weight) for column, weight in weights.items()
        },
        "weight_sum": float(weights.sum()),
        "score_min": float(scores.min()),
        "score_max": float(scores.max()),
        "class_labels": list(CLASS_LABELS),
        "cells_with_score": int(result[COMPOSITE_SCORE_COLUMN].notna().sum()),
        "cells_with_class": int(result[SUITABILITY_CLASS_COLUMN].notna().sum()),
        **classification_report,
    }
    return result, report
