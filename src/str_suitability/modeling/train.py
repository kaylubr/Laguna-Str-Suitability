import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, train_test_split

from str_suitability.config import CV_FOLDS, PARAM_GRID, RANDOM_STATE, TEST_SIZE


def split_observations(
    features: pd.DataFrame, target: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(
        features, target, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )


def tune_and_train(
    features: pd.DataFrame, target: pd.Series
) -> tuple[RandomForestRegressor, dict, float]:
    search = GridSearchCV(
        RandomForestRegressor(random_state=RANDOM_STATE),
        PARAM_GRID,
        cv=CV_FOLDS,
        scoring="neg_root_mean_squared_error",
        n_jobs=-1,
    )
    search.fit(features, target)
    return search.best_estimator_, dict(search.best_params_), float(search.best_score_)


def train_model(
    features: pd.DataFrame, target: pd.Series
) -> dict:
    features_train, features_test, target_train, target_test = split_observations(features, target)
    model, best_params, best_cv_score = tune_and_train(features_train, target_train)
    return {
        "model": model,
        "best_params": best_params,
        "best_cv_rmse": -best_cv_score,
        "features_train": features_train,
        "features_test": features_test,
        "target_train": target_train,
        "target_test": target_test,
    }
