import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from str_suitability.config import PROJECTED_CRS
from str_suitability.suitability.inputs import join_predictions, load_scoring_input

CELL_IDS = ["c0", "c1", "c2"]
EXPECTED = {"c0": (100.0, 0.1), "c1": (200.0, 0.2), "c2": (300.0, 0.3)}


def make_grid() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {
            "cell_id": CELL_IDS,
            "poi_density_total": [1.0, 2.0, 3.0],
            "distance_to_nearest_tourist_attraction": [1.0, 2.0, 3.0],
            "distance_to_nearest_transportation_facility": [1.0, 2.0, 3.0],
            "geometry": [box(0, 0, 1, 1), box(1, 0, 2, 1), box(2, 0, 3, 1)],
        },
        geometry="geometry",
        crs=PROJECTED_CRS,
    )


def make_predictions() -> dict[str, pd.DataFrame]:
    return {
        "predicted_revenue": pd.DataFrame(
            {"cell_id": CELL_IDS, "predicted_revenue": [100.0, 200.0, 300.0]}
        ),
        "predicted_occupancy": pd.DataFrame(
            {"cell_id": CELL_IDS, "predicted_occupancy": [0.1, 0.2, 0.3]}
        ),
    }


def assert_mapping(joined: gpd.GeoDataFrame) -> None:
    for cell_id, (revenue, occupancy) in EXPECTED.items():
        row = joined[joined["cell_id"] == cell_id].iloc[0]
        assert row["predicted_revenue"] == revenue
        assert row["predicted_occupancy"] == occupancy


def test_join_attaches_predictions_by_key():
    joined = join_predictions(make_grid(), make_predictions())
    assert len(joined) == 3
    assert_mapping(joined)


def test_reversed_prediction_rows_still_land_on_the_right_cell():
    predictions = {column: frame.iloc[::-1].reset_index(drop=True) for column, frame in make_predictions().items()}
    assert predictions["predicted_revenue"]["cell_id"].tolist() == ["c2", "c1", "c0"]
    assert_mapping(join_predictions(make_grid(), predictions))


def test_shuffled_prediction_rows_still_land_on_the_right_cell():
    predictions = {
        column: frame.sample(frac=1.0, random_state=7).reset_index(drop=True)
        for column, frame in make_predictions().items()
    }
    assert_mapping(join_predictions(make_grid(), predictions))


def test_prediction_rows_shuffled_independently_of_each_other():
    predictions = make_predictions()
    predictions["predicted_revenue"] = predictions["predicted_revenue"].iloc[::-1].reset_index(drop=True)
    predictions["predicted_occupancy"] = predictions["predicted_occupancy"].sample(
        frac=1.0, random_state=3
    ).reset_index(drop=True)
    assert_mapping(join_predictions(make_grid(), predictions))


def test_shuffled_grid_rows_keep_the_mapping():
    shuffled_grid = make_grid().sample(frac=1.0, random_state=11).reset_index(drop=True)
    assert_mapping(join_predictions(shuffled_grid, make_predictions()))


def test_join_preserves_geometry_and_crs():
    joined = join_predictions(make_grid(), make_predictions())
    assert joined.crs == PROJECTED_CRS
    assert joined.geometry.notna().all()


def test_keyless_predictions_are_rejected_rather_than_aligned_by_position():
    keyless = {"predicted_revenue": pd.DataFrame({"predicted_revenue": [100.0, 200.0, 300.0]})}
    with pytest.raises(AssertionError, match="aligned by row order"):
        join_predictions(make_grid(), keyless)


def test_duplicate_cell_ids_in_predictions_are_rejected():
    predictions = make_predictions()
    predictions["predicted_revenue"].loc[1, "cell_id"] = "c0"
    with pytest.raises(AssertionError, match="repeats a cell identifier"):
        join_predictions(make_grid(), predictions)


def test_predictions_covering_other_cells_are_rejected():
    predictions = make_predictions()
    predictions["predicted_revenue"].loc[2, "cell_id"] = "c9"
    with pytest.raises(AssertionError, match="different set of cells"):
        join_predictions(make_grid(), predictions)


def test_null_cell_id_in_predictions_is_rejected():
    predictions = make_predictions()
    predictions["predicted_revenue"].loc[0, "cell_id"] = None
    with pytest.raises(AssertionError, match="null cell identifier"):
        join_predictions(make_grid(), predictions)


def test_loading_from_disk_uses_the_key(tmp_path):
    make_grid().to_parquet(tmp_path / "grid_features.parquet", index=False)
    for column, frame in make_predictions().items():
        frame.to_parquet(tmp_path / f"{column}.parquet", index=False)

    loaded = load_scoring_input(tmp_path)
    assert len(loaded) == 3
    assert_mapping(loaded)


def test_loading_from_disk_ignores_row_order(tmp_path):
    make_grid().to_parquet(tmp_path / "grid_features.parquet", index=False)
    for column, frame in make_predictions().items():
        frame.iloc[::-1].reset_index(drop=True).to_parquet(
            tmp_path / f"{column}.parquet", index=False
        )

    assert_mapping(load_scoring_input(tmp_path))


def test_loading_rejects_a_keyless_prediction_file_on_disk(tmp_path):
    make_grid().to_parquet(tmp_path / "grid_features.parquet", index=False)
    pd.DataFrame({"predicted_revenue": [100.0, 200.0, 300.0]}).to_parquet(
        tmp_path / "predicted_revenue.parquet", index=False
    )
    make_predictions()["predicted_occupancy"].to_parquet(
        tmp_path / "predicted_occupancy.parquet", index=False
    )
    with pytest.raises(AssertionError, match="aligned by row order"):
        load_scoring_input(tmp_path)
