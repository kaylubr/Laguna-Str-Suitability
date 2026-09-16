import geopandas as gpd
import numpy as np
import pandas as pd

from str_suitability.spatial.haversine import haversine_km

DISTANCE_CHUNK_ROWS = 250


def distance_to_nearest_km(
    origin_longitude: np.ndarray,
    origin_latitude: np.ndarray,
    target_longitude: np.ndarray,
    target_latitude: np.ndarray,
) -> np.ndarray:
    if len(target_longitude) == 0:
        return np.full(len(origin_longitude), np.nan)
    distances = np.empty(len(origin_longitude), dtype=float)
    for start in range(0, len(origin_longitude), DISTANCE_CHUNK_ROWS):
        stop = start + DISTANCE_CHUNK_ROWS
        block = haversine_km(
            origin_longitude[start:stop, None],
            origin_latitude[start:stop, None],
            target_longitude[None, :],
            target_latitude[None, :],
        )
        distances[start:stop] = block.min(axis=1)
    return distances


def add_accessibility_distances(
    grid: gpd.GeoDataFrame,
    transport_facilities: gpd.GeoDataFrame,
    tourist_attractions: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    enriched = grid.copy()
    enriched["distance_to_nearest_transportation_facility"] = distance_to_nearest_km(
        enriched["longitude"].to_numpy(),
        enriched["latitude"].to_numpy(),
        transport_facilities["longitude"].to_numpy(),
        transport_facilities["latitude"].to_numpy(),
    )
    enriched["distance_to_nearest_tourist_attraction"] = distance_to_nearest_km(
        enriched["longitude"].to_numpy(),
        enriched["latitude"].to_numpy(),
        tourist_attractions["longitude"].to_numpy(),
        tourist_attractions["latitude"].to_numpy(),
    )
    return gpd.GeoDataFrame(enriched, geometry="geometry", crs=grid.crs)


def add_tourism_features(
    grid: gpd.GeoDataFrame, tourist_attractions: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    enriched = grid.copy()
    joined = gpd.sjoin(
        tourist_attractions[["osm_id", "geometry"]].to_crs(grid.crs),
        grid[["cell_id", "geometry"]],
        predicate="within",
        how="inner",
    )
    counts = joined.groupby("cell_id")["osm_id"].count().rename("tourist_attraction_count")
    enriched = enriched.merge(counts.reset_index(), on="cell_id", how="left")
    enriched["tourist_attraction_count"] = enriched["tourist_attraction_count"].fillna(0).astype(int)
    enriched["tourist_attraction_density"] = (
        enriched["tourist_attraction_count"] / (enriched["cell_area_m2"] / 1_000_000)
    )
    return gpd.GeoDataFrame(enriched, geometry="geometry", crs=grid.crs)


def add_demographic_features(grid: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    enriched = grid.copy()
    enriched["population_density_per_km2"] = pd.to_numeric(
        enriched["population_density_per_km2"], errors="coerce"
    )
    return gpd.GeoDataFrame(enriched, geometry="geometry", crs=grid.crs)
