import geopandas as gpd
import pandas as pd

from str_suitability.config import GEOGRAPHIC_CRS, PROJECTED_CRS
from str_suitability.preprocess.clean_psa import fill_missing_psgc_refs

MUNICIPALITY_COLUMNS = [
    "name",
    "psgc_ref",
    "population",
    "population_density_per_km2",
    "municipality_area_km2",
    "geometry",
]


def normalize_psgc(code: str | None) -> str | None:
    if code is None or pd.isna(code):
        return None
    digits = str(code).upper().removeprefix("PH")
    return digits.ljust(10, "0")


def build_municipality_table(
    municipalities: gpd.GeoDataFrame, population: pd.DataFrame
) -> gpd.GeoDataFrame:
    complete, _ = fill_missing_psgc_refs(municipalities)
    projected = complete.to_crs(PROJECTED_CRS)
    osm_columns = [
        column for column in ("population", "population_date") if column in projected.columns
    ]
    projected = projected.rename(columns={column: f"osm_{column}" for column in osm_columns})
    table = projected.assign(municipality_area_km2=projected.geometry.area / 1_000_000)
    table = table.merge(
        population[["psgc_ref", "population", "normalized_name"]],
        on="psgc_ref",
        how="left",
        validate="one_to_one",
    )
    table["population_density_per_km2"] = table["population"] / table["municipality_area_km2"]
    return table


def assign_listings_to_cells(listings: pd.DataFrame, grid: gpd.GeoDataFrame) -> tuple[pd.DataFrame, dict]:
    points = gpd.GeoDataFrame(
        listings.copy(),
        geometry=gpd.points_from_xy(listings["longitude"], listings["latitude"]),
        crs=GEOGRAPHIC_CRS,
    ).to_crs(grid.crs)
    joined = gpd.sjoin(
        points, grid[["cell_id", "geometry"]], predicate="within", how="left"
    ).drop(columns=["index_right"])

    unmatched = int(joined["cell_id"].isna().sum())
    join_report = {
        "listings": int(len(listings)),
        "assigned_to_cell": int(len(joined) - unmatched),
        "unassigned_to_cell": unmatched,
    }
    return pd.DataFrame(joined.drop(columns="geometry")), join_report


def assign_dominant_municipality(
    grid: gpd.GeoDataFrame, municipality_table: gpd.GeoDataFrame
) -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    cells = grid[["cell_id", "projected_area_m2", "geometry"]]
    overlay = gpd.overlay(
        cells, municipality_table[MUNICIPALITY_COLUMNS], how="intersection", keep_geom_type=True
    )
    overlay["overlap_area_m2"] = overlay.geometry.area
    overlay["municipality_overlap_share"] = (
        overlay["overlap_area_m2"] / overlay["projected_area_m2"]
    )
    dominant = (
        overlay.sort_values(["cell_id", "overlap_area_m2"], ascending=[True, False])
        .drop_duplicates("cell_id")
        .drop(columns=["geometry", "projected_area_m2"])
    )
    return dominant.reset_index(drop=True), overlay


def join_demographics(
    grid: gpd.GeoDataFrame, municipality_table: gpd.GeoDataFrame
) -> tuple[gpd.GeoDataFrame, dict]:
    dominant, overlay = assign_dominant_municipality(grid, municipality_table)

    enriched = grid.merge(dominant, on="cell_id", how="left", validate="one_to_one").rename(
        columns={"name": "municipality"}
    )

    matches_per_cell = overlay.groupby("cell_id").size()
    report = {
        "cells": int(len(grid)),
        "cells_with_municipality": int(enriched["municipality"].notna().sum()),
        "cells_without_municipality": int(enriched["municipality"].isna().sum()),
        "cells_with_population": int(enriched["population"].notna().sum()),
        "cells_straddling_municipal_boundaries": int((matches_per_cell > 1).sum()),
        "max_municipalities_per_cell": int(matches_per_cell.max()),
    }
    return gpd.GeoDataFrame(enriched, geometry="geometry", crs=PROJECTED_CRS), report


def normalise_listing_psgc(listings: pd.DataFrame) -> pd.DataFrame:
    return listings.assign(psgc_ref=listings["psgc_code"].map(normalize_psgc))
