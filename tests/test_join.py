import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from str_suitability.config import PROJECTED_CRS
from str_suitability.spatial.grid import assert_one_row_per_cell
from str_suitability.spatial.join import (
    assign_dominant_municipality,
    assign_listings_to_cells,
    build_municipality_table,
    join_demographics,
    normalise_listing_psgc,
    normalize_psgc,
)


def test_normalize_psgc_expands_short_listing_codes():
    assert normalize_psgc("PH0403428") == "0403428000"
    assert normalize_psgc("PH0403401") == "0403401000"


def test_normalize_psgc_leaves_full_boundary_codes_unchanged():
    assert normalize_psgc("0403428000") == "0403428000"


def test_normalize_psgc_handles_missing_values():
    assert normalize_psgc(None) is None
    assert normalize_psgc(float("nan")) is None


def test_listing_and_boundary_codes_agree():
    listing_codes = ["PH0403401", "PH0403428", "PH0403405"]
    boundary_codes = ["0403401000", "0403428000", "0403405000"]
    assert [normalize_psgc(code) for code in listing_codes] == boundary_codes


def test_normalise_listing_psgc_adds_column():
    listings = pd.DataFrame({"psgc_code": ["PH0403401"]})
    assert normalise_listing_psgc(listings)["psgc_ref"].tolist() == ["0403401000"]


def make_grid():
    return gpd.GeoDataFrame(
        {
            "cell_id": ["r0000c0000", "r0000c0001"],
            "geometry": [box(0, 0, 1000, 1000), box(1000, 0, 2000, 1000)],
        },
        geometry="geometry",
        crs=PROJECTED_CRS,
    )


def test_assign_listings_to_cells_maps_points_to_containing_cell():
    listings = pd.DataFrame(
        {
            "listing_id": ["a", "b"],
            "longitude": [121.0, 121.5],
            "latitude": [14.0, 14.5],
        }
    )
    grid = gpd.GeoDataFrame(
        {
            "cell_id": ["west", "east"],
            "geometry": [
                box(120.5, 13.5, 121.2, 14.8),
                box(121.2, 13.5, 121.8, 14.8),
            ],
        },
        geometry="geometry",
        crs="EPSG:4326",
    ).to_crs(PROJECTED_CRS)
    assigned, report = assign_listings_to_cells(listings, grid)
    assert assigned.set_index("listing_id")["cell_id"].to_dict() == {"a": "west", "b": "east"}
    assert report["unassigned_to_cell"] == 0


def test_assign_listings_reports_unmatched_points():
    listings = pd.DataFrame(
        {"listing_id": ["a"], "longitude": [10.0], "latitude": [10.0]}
    )
    grid = gpd.GeoDataFrame({"cell_id": ["x"], "geometry": [box(0, 0, 1, 1)]}, crs="EPSG:4326")
    _, report = assign_listings_to_cells(listings, grid)
    assert report["unassigned_to_cell"] == 1


def test_build_municipality_table_joins_population_by_code():
    municipalities = gpd.GeoDataFrame(
        {
            "name": ["Bay"],
            "psgc_ref": ["0403402000"],
            "geometry": [box(0, 0, 1000, 1000)],
        },
        geometry="geometry",
        crs=PROJECTED_CRS,
    )
    population = pd.DataFrame(
        {"municipality": ["Bay"], "normalized_name": ["bay"], "psgc_ref": ["0403402000"], "population": [1000]}
    )
    table = build_municipality_table(municipalities, population)
    assert table["population"].iloc[0] == 1000
    assert table["population_density_per_km2"].iloc[0] == pytest.approx(1000.0)


def test_join_demographics_carries_municipality_onto_cells():
    grid = gpd.GeoDataFrame(
        {
            "cell_id": ["a", "b"],
            "projected_area_m2": [250_000.0, 160_000.0],
            "geometry": [box(0, 0, 500, 500), box(500, 500, 900, 900)],
        },
        geometry="geometry",
        crs=PROJECTED_CRS,
    )
    table = gpd.GeoDataFrame(
        {
            "name": ["Bay"],
            "psgc_ref": ["0403402000"],
            "population": [1000],
            "population_density_per_km2": [500.0],
            "municipality_area_km2": [2.0],
            "geometry": [box(-100, -100, 2000, 2000)],
        },
        geometry="geometry",
        crs=PROJECTED_CRS,
    )
    joined, report = join_demographics(grid, table)
    assert report["cells_with_municipality"] == 2
    assert set(joined["municipality"]) == {"Bay"}
    assert joined["population_density_per_km2"].tolist() == [500.0, 500.0]
    assert len(joined) == joined["cell_id"].nunique()


def make_claiming_grid():
    return gpd.GeoDataFrame(
        {
            "cell_id": ["straddling"],
            "projected_area_m2": [1_000_000.0],
            "geometry": [box(0, 0, 1000, 1000)],
        },
        geometry="geometry",
        crs=PROJECTED_CRS,
    )


def make_two_municipalities():
    return gpd.GeoDataFrame(
        {
            "name": ["Larger", "Smaller"],
            "psgc_ref": ["0403401000", "0403402000"],
            "population": [100, 200],
            "population_density_per_km2": [10.0, 20.0],
            "municipality_area_km2": [10.0, 10.0],
            "geometry": [box(0, 0, 600, 1000), box(500, 0, 1000, 1000)],
        },
        geometry="geometry",
        crs=PROJECTED_CRS,
    )


def test_cell_straddling_two_municipalities_takes_the_larger_overlap():
    dominant, overlay = assign_dominant_municipality(make_claiming_grid(), make_two_municipalities())
    assert len(overlay) == 2
    assert dominant["name"].tolist() == ["Larger"]
    assert dominant["overlap_area_m2"].iloc[0] == pytest.approx(600_000)
    assert dominant["municipality_overlap_share"].iloc[0] == pytest.approx(0.6)


def test_dominant_assignment_yields_one_row_per_cell():
    dominant, _ = assign_dominant_municipality(make_claiming_grid(), make_two_municipalities())
    assert dominant["cell_id"].is_unique


def test_join_demographics_does_not_duplicate_straddling_cells():
    joined, report = join_demographics(make_claiming_grid(), make_two_municipalities())
    assert len(joined) == 1
    assert report["cells_straddling_municipal_boundaries"] == 1
    assert report["max_municipalities_per_cell"] == 2
    assert joined["municipality"].iloc[0] == "Larger"


def test_build_municipality_table_keeps_one_row_per_municipality():
    municipalities = gpd.GeoDataFrame(
        {
            "name": ["Bay", "Pila"],
            "psgc_ref": ["0403402000", None],
            "geometry": [box(0, 0, 1000, 1000), box(1000, 0, 2000, 1000)],
        },
        geometry="geometry",
        crs=PROJECTED_CRS,
    )
    population = pd.DataFrame(
        {
            "municipality": ["Bay", "Pila"],
            "normalized_name": ["bay", "pila"],
            "population": [1000, 2000],
        }
    )
    population = population.assign(psgc_ref=[None, None])
    population.loc[0, "psgc_ref"] = "0403402000"
    population.loc[1, "psgc_ref"] = "0403422000"
    table = build_municipality_table(municipalities, population)
    assert len(table) == len(municipalities)
    assert table["psgc_ref"].is_unique
    assert table["population"].notna().all()


def test_assert_one_row_per_cell_rejects_duplicates():
    frame = pd.DataFrame({"cell_id": ["a", "a", "b"]})
    with pytest.raises(AssertionError, match="duplicate cell_id"):
        assert_one_row_per_cell(frame)


def test_assert_one_row_per_cell_accepts_unique_ids():
    assert_one_row_per_cell(pd.DataFrame({"cell_id": ["a", "b"]}))
