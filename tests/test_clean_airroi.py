import pandas as pd
import pytest

from str_suitability.preprocess.clean_airroi import (
    build_target_dataset,
    summarize_target_dataset,
    validate_target_dataset,
)


def make_listings(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


LISTING_COLUMNS = [
    "listing_id",
    "municipality",
    "psgc_code",
    "latitude",
    "longitude",
    "ttm_revenue",
    "ttm_occupancy",
]


def listing(listing_id, revenue, occupancy, month_count):
    return (
        {
            "listing_id": listing_id,
            "municipality": "Calamba",
            "psgc_code": "PH0403405",
            "latitude": 14.2,
            "longitude": 121.2,
            "ttm_revenue": revenue,
            "ttm_occupancy": occupancy,
        },
        month_count,
    )


PANEL_COLUMNS = ["listing_id", "month", "revenue", "occupancy", "average_daily_rate", "months_requested"]


def make_panel(specs: list[tuple[str, int, float]]) -> pd.DataFrame:
    records = []
    for listing_id, month_count, revenue in specs:
        for month in range(month_count):
            records.append(
                {
                    "listing_id": listing_id,
                    "month": f"2026-{month + 1:02d}",
                    "revenue": revenue if month == 0 else 0.0,
                    "occupancy": 0.1,
                    "average_daily_rate": 1000.0,
                    "months_requested": month_count,
                }
            )
    return pd.DataFrame.from_records(records, columns=PANEL_COLUMNS)


def test_dormant_listings_are_flagged_and_excluded():
    listings = make_listings(
        [
            {"listing_id": "a", "municipality": "Calamba", "psgc_code": "x", "latitude": 14.2, "longitude": 121.2, "ttm_revenue": 0.0, "ttm_occupancy": 0.0},
            {"listing_id": "b", "municipality": "Calamba", "psgc_code": "x", "latitude": 14.2, "longitude": 121.2, "ttm_revenue": 150000.0, "ttm_occupancy": 0.4},
        ]
    )
    panel = make_panel([("b", 12, 150000.0)])
    dataset = build_target_dataset(listings, panel)
    dormant = dataset.set_index("listing_id")["is_dormant"]
    training = dataset.set_index("listing_id")["in_training_population"]
    assert dormant["a"] and not dormant["b"]
    assert not training["a"] and training["b"]


def test_positive_revenue_without_corroboration_is_excluded():
    listings = make_listings(
        [
            {"listing_id": "a", "municipality": "Calamba", "psgc_code": "x", "latitude": 14.2, "longitude": 121.2, "ttm_revenue": 11544.0, "ttm_occupancy": 0.05},
        ]
    )
    panel = make_panel([])
    dataset = build_target_dataset(listings, panel)
    row = dataset.iloc[0]
    assert not row["is_dormant"]
    assert not row["is_corroborated"]
    assert not row["in_training_population"]


def test_zero_revenue_months_do_not_corroborate():
    listings = make_listings(
        [
            {"listing_id": "a", "municipality": "Calamba", "psgc_code": "x", "latitude": 14.2, "longitude": 121.2, "ttm_revenue": 9000.0, "ttm_occupancy": 0.02},
        ]
    )
    panel = make_panel([("a", 12, 0.0)])
    dataset = build_target_dataset(listings, panel)
    assert not dataset.iloc[0]["in_training_population"]


def test_partial_window_with_positive_month_is_corroborated():
    listings = make_listings(
        [
            {"listing_id": "a", "municipality": "Calamba", "psgc_code": "x", "latitude": 14.2, "longitude": 121.2, "ttm_revenue": 9000.0, "ttm_occupancy": 0.02},
        ]
    )
    panel = make_panel([("a", 8, 4000.0)])
    dataset = build_target_dataset(listings, panel)
    row = dataset.iloc[0]
    assert row["window_month_count"] == 8
    assert row["in_training_population"]


def test_validation_flags_reported_zero_with_positive_window():
    listings = make_listings(
        [
            {"listing_id": "a", "municipality": "Calamba", "psgc_code": "x", "latitude": 14.2, "longitude": 121.2, "ttm_revenue": 0.0, "ttm_occupancy": 0.0},
        ]
    )
    panel = make_panel([("a", 12, 5000.0)])
    dataset = build_target_dataset(listings, panel)
    checks = validate_target_dataset(dataset)
    assert checks["no_reported_zero_with_positive_window_revenue"] is False


def test_validation_passes_on_clean_input():
    listings = make_listings(
        [
            {"listing_id": "a", "municipality": "Calamba", "psgc_code": "x", "latitude": 14.2, "longitude": 121.2, "ttm_revenue": 0.0, "ttm_occupancy": 0.0},
            {"listing_id": "b", "municipality": "Calamba", "psgc_code": "x", "latitude": 14.2, "longitude": 121.2, "ttm_revenue": 150000.0, "ttm_occupancy": 0.4},
        ]
    )
    panel = make_panel([("b", 12, 150000.0)])
    dataset = build_target_dataset(listings, panel)
    checks = validate_target_dataset(dataset)
    assert all(checks.values())


def test_summary_reports_population_and_distribution():
    listings = make_listings(
        [
            {"listing_id": "a", "municipality": "Calamba", "psgc_code": "x", "latitude": 14.2, "longitude": 121.2, "ttm_revenue": 0.0, "ttm_occupancy": 0.0},
            {"listing_id": "b", "municipality": "Calamba", "psgc_code": "x", "latitude": 14.2, "longitude": 121.2, "ttm_revenue": 150000.0, "ttm_occupancy": 0.4},
            {"listing_id": "c", "municipality": "Bay", "psgc_code": "y", "latitude": 14.1, "longitude": 121.3, "ttm_revenue": 80000.0, "ttm_occupancy": 0.3},
        ]
    )
    panel = make_panel([("b", 12, 150000.0), ("c", 12, 80000.0)])
    dataset = build_target_dataset(listings, panel)
    summary = summarize_target_dataset(dataset)
    assert summary["total_listings"] == 3
    assert summary["dormant"] == 1
    assert summary["training_population"] == 2
    assert len(summary["by_municipality"]) == 2
