import pandas as pd
from sklearn.inspection import permutation_importance

from str_suitability.config import RANDOM_STATE


def permutation_importance_table(
    model,
    features_test: pd.DataFrame,
    target_test: pd.Series,
    n_repeats: int = 30,
) -> pd.DataFrame:
    result = permutation_importance(
        model,
        features_test,
        target_test,
        n_repeats=n_repeats,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        scoring="neg_root_mean_squared_error",
    )
    table = pd.DataFrame(
        {
            "feature": features_test.columns,
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    )
    return table.sort_values("importance_mean", ascending=False).reset_index(drop=True)
