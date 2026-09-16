import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Polygon, box

from str_suitability.config import PROJECTED_CRS
from str_suitability.spatial.grid import build_grid, derive_land_boundary
from str_suitability.spatial.haversine import haversine_km, nearest_distance_km


def test_haversine_zero_distance():
    assert haversine_km(121.0, 14.0, 121.0, 14.0) == pytest.approx(0.0)


def test_haversine_matches_known_meridian_degree():
    distance = haversine_km(121.0, 14.0, 121.0, 15.0)
    assert distance == pytest.approx(111.19, abs=0.05)


def test_haversine_matches_known_equatorial_degree():
    distance = haversine_km(0.0, 0.0, 1.0, 0.0)
    assert distance == pytest.approx(111.19, abs=0.05)


def test_haversine_is_symmetric():
    forward = haversine_km(121.01, 13.99, 121.60, 14.56)
    backward = haversine_km(121.60, 14.56, 121.01, 13.99)
    assert forward == pytest.approx(backward)


def test_nearest_distance_picks_the_closest_target():
    distances = nearest_distance_km(
        np.array([121.0]), np.array([14.0]), np.array([121.5, 121.01]), np.array([14.5, 14.0])
    )
    assert distances[0] == pytest.approx(haversine_km(121.0, 14.0, 121.01, 14.0))


def test_nearest_distance_without_targets_is_nan():
    distances = nearest_distance_km(
        np.array([121.0]), np.array([14.0]), np.array([]), np.array([])
    )
    assert np.isnan(distances[0])


def square(x, y, size):
    return Polygon([(x, y), (x + size, y), (x + size, y + size), (x, y + size)])


def test_derive_land_boundary_subtracts_water():
    province = gpd.GeoDataFrame(
        {"name": ["px"]}, geometry=[box(0, 0, 1000, 1000)], crs=PROJECTED_CRS
    )
    water = gpd.GeoDataFrame(
        {"name": ["lake"]}, geometry=[box(0, 0, 500, 1000)], crs=PROJECTED_CRS
    )
    land = derive_land_boundary(province, water)
    assert land.area == pytest.approx(500_000)


def test_build_grid_keeps_only_majority_land_cells():
    land = square(0, 0, 2000)
    grid = build_grid(land, cell_size_m=1000)
    assert len(grid) == 4
    assert set(grid["land_coverage"].round(4)) == {1.0}


def test_build_grid_drops_cells_below_coverage_threshold():
    land = box(0, 0, 1000, 1000).union(box(1000, 0, 1200, 1000))
    grid = build_grid(land, cell_size_m=1000)
    assert len(grid) == 1
    assert grid["cell_id"].tolist() == ["r0000c0000"]


def test_build_grid_records_partial_coverage_and_clips_area():
    land = box(0, 0, 1000, 1000).union(box(1000, 0, 1700, 1000))
    grid = build_grid(land, cell_size_m=1000)
    partial = grid[grid["cell_id"] == "r0000c0001"].iloc[0]
    assert partial["land_coverage"] == pytest.approx(0.7)
    assert partial.geometry.area == pytest.approx(700_000)


def test_build_grid_cells_are_one_square_kilometre_of_cell_area():
    land = square(0, 0, 2000)
    grid = build_grid(land, cell_size_m=1000)
    assert set(grid["cell_area_m2"]) == {1_000_000.0}


def test_grids_at_different_sizes_nest():
    land = square(0, 0, 4000)
    coarse = build_grid(land, cell_size_m=2000)
    fine = build_grid(land, cell_size_m=500)
    coarse_min_x = coarse.total_bounds[0]
    fine_min_x = fine.total_bounds[0]
    assert coarse_min_x == pytest.approx(fine_min_x)
    assert (fine.total_bounds[2] - fine.total_bounds[0]) % 2000 == pytest.approx(0.0)


def test_grid_has_no_duplicate_cell_ids():
    land = square(0, 0, 3000)
    grid = build_grid(land, cell_size_m=1000)
    assert grid["cell_id"].is_unique
