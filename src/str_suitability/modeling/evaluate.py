import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def regression_metrics(observed, predicted) -> dict[str, float]:
    observed_array = np.asarray(observed, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)
    return {
        "mae": float(mean_absolute_error(observed_array, predicted_array)),
        "rmse": float(np.sqrt(mean_squared_error(observed_array, predicted_array))),
        "r2": float(r2_score(observed_array, predicted_array)),
        "n": int(len(observed_array)),
    }


def evaluate_on_test(model, features_test, target_test) -> dict[str, float]:
    return regression_metrics(target_test, model.predict(features_test))


def evaluate_on_train(model, features_train, target_train) -> dict[str, float]:
    return regression_metrics(target_train, model.predict(features_train))


def describe_target(target) -> dict[str, float]:
    series = np.asarray(target, dtype=float)
    return {
        "count": int(len(series)),
        "mean": float(np.mean(series)),
        "std": float(np.std(series, ddof=1)),
        "min": float(np.min(series)),
        "p25": float(np.percentile(series, 25)),
        "median": float(np.percentile(series, 50)),
        "p75": float(np.percentile(series, 75)),
        "p95": float(np.percentile(series, 95)),
        "max": float(np.max(series)),
        "skew": float(_skewness(series)),
    }


def _skewness(series: np.ndarray) -> float:
    centered = series - series.mean()
    standard_deviation = series.std(ddof=0)
    if standard_deviation == 0:
        return 0.0
    return float(np.mean(centered**3) / standard_deviation**3)
