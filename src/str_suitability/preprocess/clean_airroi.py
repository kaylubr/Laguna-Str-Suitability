import pandas as pd

from str_suitability.config import OCCUPANCY_TARGET, REVENUE_TARGET
from str_suitability.ingest.load_airroi import load_airroi_listings, load_history_panel

TARGET_COLUMNS = [
    "listing_id",
    "municipality",
    "psgc_code",
    "latitude",
    "longitude",
    REVENUE_TARGET,
    OCCUPANCY_TARGET,
    "window_month_count",
    "window_revenue",
    "window_occupancy",
    "is_dormant",
    "is_corroborated",
    "in_training_population",
]


def build_target_dataset(listings: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    zero_revenue = listings[REVENUE_TARGET].fillna(0).eq(0)
    zero_occupancy = listings[OCCUPANCY_TARGET].fillna(0).eq(0)
    listings = listings.assign(is_dormant=zero_revenue & zero_occupancy)

    window = (
        panel.groupby("listing_id")
        .agg(
            window_month_count=("month", "size"),
            window_revenue=("revenue", "sum"),
            window_occupancy=("occupancy", "mean"),
        )
        .reindex(listings["listing_id"])
        .fillna({"window_month_count": 0, "window_revenue": 0.0, "window_occupancy": 0.0})
        .reset_index()
    )

    dataset = listings.merge(window, on="listing_id", how="left")
    positive_window_month = dataset["window_revenue"].gt(0)
    dataset = dataset.assign(
        is_corroborated=positive_window_month,
        in_training_population=~dataset["is_dormant"] & positive_window_month,
    )
    return dataset[TARGET_COLUMNS]


def build_target_dataset_from_paths(
    listings_path, history_dir, window: tuple[str, str]
) -> pd.DataFrame:
    listings = load_airroi_listings(listings_path)
    panel = load_history_panel(history_dir, window)
    return build_target_dataset(listings, panel)


def validate_target_dataset(dataset: pd.DataFrame) -> dict[str, object]:
    checks = {}
    checks["unique_listing_ids"] = dataset["listing_id"].is_unique
    checks["no_null_coordinates"] = not dataset[["latitude", "longitude"]].isna().any().any()
    checks["coordinates_within_laguna_extent"] = bool(
        dataset["latitude"].between(13.9, 14.7).all() and dataset["longitude"].between(120.9, 121.7).all()
    )
    checks["dormant_and_training_disjoint"] = not (
        dataset["is_dormant"] & dataset["in_training_population"]
    ).any()
    reported_zero = dataset[REVENUE_TARGET].fillna(0).eq(0)
    checks["no_reported_zero_with_positive_window_revenue"] = not (
        reported_zero & dataset["window_revenue"].gt(0)
    ).any()
    reported_positive = dataset[REVENUE_TARGET].fillna(0).gt(0)
    complete_window = dataset["window_month_count"].eq(12)
    checks["no_complete_window_with_zero_revenue"] = not (
        reported_positive & complete_window & dataset["window_revenue"].eq(0)
    ).any()
    checks["training_population_matches_corroborated"] = bool(
        dataset["in_training_population"].sum() == dataset["is_corroborated"].sum()
    )
    return checks


def summarize_target_dataset(dataset: pd.DataFrame) -> dict[str, object]:
    training = dataset[dataset["in_training_population"]]
    dormant = dataset[dataset["is_dormant"]]
    uncorroborated = dataset[~dataset["is_dormant"] & ~dataset["is_corroborated"]]
    by_municipality = (
        dataset.groupby("municipality")
        .agg(
            listings=("listing_id", "size"),
            dormant=("is_dormant", "sum"),
            excluded_total=("in_training_population", lambda values: int((~values).sum())),
            training_population=("in_training_population", "sum"),
        )
        .reset_index()
    )
    by_municipality["excluded_share"] = (
        by_municipality["excluded_total"] / by_municipality["listings"]
    )
    return {
        "total_listings": int(len(dataset)),
        "dormant": int(len(dormant)),
        "uncorroborated": int(len(uncorroborated)),
        "training_population": int(len(training)),
        "excluded_share": float((len(dataset) - len(training)) / len(dataset)),
        "revenue": training[REVENUE_TARGET].describe(percentiles=[0.25, 0.5, 0.75, 0.95]).to_dict(),
        "occupancy": training[OCCUPANCY_TARGET].describe(percentiles=[0.25, 0.5, 0.75, 0.95]).to_dict(),
        "by_municipality": by_municipality.to_dict(orient="records"),
    }
