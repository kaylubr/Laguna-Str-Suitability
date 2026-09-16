import geopandas as gpd
import pandas as pd

from str_suitability.suitability.validate import validate_suitability_inputs

CELL_ID_COLUMN = "cell_id"
GRID_FILENAME = "grid_features.parquet"
PREDICTED_COLUMNS = ("predicted_revenue", "predicted_occupancy")


def join_predictions(
    grid: gpd.GeoDataFrame, predictions: dict[str, pd.DataFrame]
) -> gpd.GeoDataFrame:
    assert grid[CELL_ID_COLUMN].is_unique, "the grid must hold one row per cell before joining"
    assert grid[CELL_ID_COLUMN].notna().all(), "the grid contains a null cell identifier"

    joined = grid
    for column, frame in predictions.items():
        assert CELL_ID_COLUMN in frame.columns, (
            f"{column} carries no {CELL_ID_COLUMN} column, so it can only be aligned by row order"
        )
        assert column in frame.columns, f"{column} is absent from its own prediction table"
        assert frame[CELL_ID_COLUMN].notna().all(), f"{column} contains a null cell identifier"
        assert frame[CELL_ID_COLUMN].is_unique, f"{column} repeats a cell identifier"
        assert set(frame[CELL_ID_COLUMN]) == set(grid[CELL_ID_COLUMN]), (
            f"{column} covers a different set of cells than the grid"
        )
        joined = joined.merge(frame, on=CELL_ID_COLUMN, how="left", validate="one_to_one")

    return gpd.GeoDataFrame(joined, geometry="geometry", crs=grid.crs)


def load_scoring_input(processed_dir) -> gpd.GeoDataFrame:
    grid = gpd.read_parquet(processed_dir / GRID_FILENAME)
    predictions = {
        column: pd.read_parquet(processed_dir / f"{column}.parquet")
        for column in PREDICTED_COLUMNS
    }
    joined = join_predictions(grid, predictions)
    validate_suitability_inputs(joined)
    return joined
