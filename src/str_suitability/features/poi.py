import geopandas as gpd
import numpy as np
import pandas as pd

from str_suitability.taxonomy import PoiCategory


def poi_counts_per_cell(grid: gpd.GeoDataFrame, pois: gpd.GeoDataFrame) -> pd.DataFrame:
    categories = list(PoiCategory)
    joined = gpd.sjoin(
        pois[["osm_id", "category", "geometry"]].to_crs(grid.crs),
        grid[["cell_id", "geometry"]],
        predicate="within",
        how="inner",
    )
    counts = (
        joined.pivot_table(
            index="cell_id", columns="category", values="osm_id", aggfunc="count", fill_value=0
        )
        .reindex(columns=[str(category) for category in categories], fill_value=0)
        .reindex(grid["cell_id"], fill_value=0)
        .fillna(0)
        .astype(int)
    )
    counts.columns = [f"poi_count_{column}" for column in counts.columns]
    counts["poi_count_total"] = counts.sum(axis=1)
    return counts.reset_index()


def add_poi_density(
    grid: gpd.GeoDataFrame, pois: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    counts = poi_counts_per_cell(grid, pois)
    enriched = grid.merge(counts, on="cell_id", how="left").fillna(
        {column: 0 for column in counts.columns if column != "cell_id"}
    )
    count_columns = [column for column in enriched.columns if column.startswith("poi_count_")]
    cell_area_km2 = enriched["cell_area_m2"] / 1_000_000
    for column in count_columns:
        density_column = column.replace("poi_count_", "poi_density_")
        enriched[density_column] = enriched[column] / cell_area_km2
    return gpd.GeoDataFrame(enriched, geometry="geometry", crs=grid.crs)
