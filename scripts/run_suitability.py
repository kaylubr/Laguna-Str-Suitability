import json

import geopandas as gpd
import pandas as pd

from str_suitability import config
from str_suitability.suitability.stage import compute_suitability

PREDICTED_COLUMNS = ("predicted_revenue", "predicted_occupancy")


def load_scoring_input() -> gpd.GeoDataFrame:
    grid = gpd.read_parquet(config.PROCESSED_DIR / "grid_features.parquet")
    predictions = {
        column: pd.read_parquet(config.PROCESSED_DIR / f"{column}.parquet")[column]
        for column in PREDICTED_COLUMNS
    }
    for column, values in predictions.items():
        assert len(values) == len(grid), (
            f"{column} holds {len(values)} rows against {len(grid)} grid rows; the prediction files "
            "carry no cell identifier and align to the grid by row order alone"
        )
    return grid.assign(
        **{column: values.to_numpy() for column, values in predictions.items()}
    )


if __name__ == "__main__":
    scored, report = compute_suitability(load_scoring_input())

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    scored.to_parquet(config.PROCESSED_DIR / "grid_suitability.parquet", index=False)
    (config.PROCESSED_DIR / "suitability_summary.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
