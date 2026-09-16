import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box

from str_suitability.config import (
    GEOGRAPHIC_CRS,
    MIN_LAND_COVERAGE,
    PRIMARY_CELL_SIZE_M,
    PROJECTED_CRS,
)


def derive_land_boundary(province: gpd.GeoDataFrame, water: gpd.GeoDataFrame):
    province_projected = province.to_crs(PROJECTED_CRS)
    province_polygon = province_projected.geometry.union_all()
    if water is None or water.empty:
        return province_polygon
    water_projected = water.to_crs(PROJECTED_CRS)
    water_polygon = water_projected.geometry.union_all()
    return province_polygon.difference(water_polygon)


def grid_anchor(minimum: float, cell_size_m: float) -> float:
    return float(np.floor(minimum / cell_size_m) * cell_size_m)


def candidate_cells(land_polygon, cell_size_m: float) -> gpd.GeoDataFrame:
    min_x, min_y, max_x, max_y = land_polygon.bounds
    anchor_x = grid_anchor(min_x, cell_size_m)
    anchor_y = grid_anchor(min_y, cell_size_m)
    columns = int(np.ceil((max_x - anchor_x) / cell_size_m))
    rows = int(np.ceil((max_y - anchor_y) / cell_size_m))

    records = []
    for row in range(rows):
        for column in range(columns):
            x = anchor_x + column * cell_size_m
            y = anchor_y + row * cell_size_m
            records.append(
                {
                    "row": row,
                    "column": column,
                    "cell_id": f"r{row:04d}c{column:04d}",
                    "geometry": box(x, y, x + cell_size_m, y + cell_size_m),
                }
            )
    return gpd.GeoDataFrame(records, geometry="geometry", crs=PROJECTED_CRS)


def assert_one_row_per_cell(frame: gpd.GeoDataFrame | pd.DataFrame) -> None:
    duplicated = int(frame["cell_id"].duplicated().sum())
    assert duplicated == 0, f"spatial unit table has {duplicated} duplicate cell_id rows"
    assert frame["cell_id"].notna().all(), "spatial unit table has null cell_id rows"


def build_grid(land_polygon, cell_size_m: int = PRIMARY_CELL_SIZE_M) -> gpd.GeoDataFrame:
    candidates = candidate_cells(land_polygon, cell_size_m)
    intersecting = candidates[candidates.geometry.intersects(land_polygon)].reset_index(drop=True)

    cell_area = float(cell_size_m) ** 2
    land_areas = intersecting.geometry.intersection(land_polygon).area
    land_coverage = land_areas / cell_area

    grid = intersecting.assign(
        land_area_m2=land_areas.to_numpy(),
        land_coverage=land_coverage.to_numpy(),
        cell_area_m2=cell_area,
    )
    retained = grid[grid["land_coverage"] >= MIN_LAND_COVERAGE].copy()
    retained["geometry"] = retained.geometry.intersection(land_polygon)
    retained = retained.reset_index(drop=True)

    centroids = retained.geometry.representative_point()
    retained["centroid_x"] = centroids.x.to_numpy()
    retained["centroid_y"] = centroids.y.to_numpy()

    projected = retained.to_crs(PROJECTED_CRS)
    geographic_centroids = gpd.GeoSeries(
        gpd.points_from_xy(retained["centroid_x"], retained["centroid_y"]), crs=PROJECTED_CRS
    ).to_crs(GEOGRAPHIC_CRS)
    retained["longitude"] = geographic_centroids.x.to_numpy()
    retained["latitude"] = geographic_centroids.y.to_numpy()

    return gpd.GeoDataFrame(
        retained[
            [
                "cell_id",
                "row",
                "column",
                "land_area_m2",
                "land_coverage",
                "cell_area_m2",
                "centroid_x",
                "centroid_y",
                "longitude",
                "latitude",
                "geometry",
            ]
        ],
        geometry="geometry",
        crs=PROJECTED_CRS,
    ).assign(projected_area_m2=lambda frame: frame.geometry.area)
