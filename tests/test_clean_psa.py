import pandas as pd

from str_suitability.preprocess.clean_psa import (
    attach_psgc_codes,
    fill_missing_psgc_refs,
    load_psa_population,
    normalize_municipality_name,
    reconcile_with_boundaries,
    validate_psa_population,
)


def test_normalization_handles_diacritics_and_case():
    assert normalize_municipality_name("Los Baños") == "los banos"
    assert normalize_municipality_name("BIÑAN") == "binan"
    assert normalize_municipality_name("  Santa  Rosa ") == "santa rosa"


def test_normalization_matches_city_and_municipality_forms():
    assert normalize_municipality_name("City of Biñan") == normalize_municipality_name("Biñan")


def test_reconciliation_reports_both_directions():
    population = pd.DataFrame(
        {
            "municipality": ["Bay", "Los Baños"],
            "normalized_name": ["bay", "los banos"],
            "population": [69802, 117030],
        }
    )
    result = reconcile_with_boundaries(population, ["Bay", "Los Baños", "Pakil"])
    assert result["matched"] == ["bay", "los banos"]
    assert result["missing_from_population"] == ["pakil"]
    assert result["missing_from_boundaries"] == []


def test_validation_detects_total_mismatch():
    frame = pd.DataFrame({"municipality": ["Bay", "Biñan"], "normalized_name": ["bay", "binan"], "population": [10, 20]})
    checks = validate_psa_population(frame, expected_total=999)
    assert checks["municipalities_sum_to_provincial_total"] is False
    assert validate_psa_population(frame, expected_total=30)[
        "municipalities_sum_to_provincial_total"
    ]


def test_fill_missing_psgc_refs_uses_psa_reference_for_known_gaps():
    municipalities = pd.DataFrame(
        {
            "name": ["Bay", "Pila", "Victoria"],
            "psgc_ref": ["0403402000", None, None],
        }
    )
    filled, report = fill_missing_psgc_refs(municipalities)
    assert filled["psgc_ref"].tolist() == ["0403402000", "0403422000", "0403430000"]
    assert report["from_osm"] == 1
    assert report["from_reference"] == 2
    assert report["still_missing"] == []


def test_fill_missing_psgc_refs_leaves_unknown_municipalities_missing():
    municipalities = pd.DataFrame({"name": ["Atlantis"], "psgc_ref": [None]})
    filled, report = fill_missing_psgc_refs(municipalities)
    assert filled["psgc_ref"].isna().all()
    assert report["still_missing"] == ["Atlantis"]


def test_attach_psgc_codes_covers_every_municipality():
    municipalities = pd.DataFrame(
        {"name": ["Bay", "Pila"], "psgc_ref": ["0403402000", None]}
    )
    population = pd.DataFrame(
        {
            "municipality": ["Bay", "Pila"],
            "normalized_name": ["bay", "pila"],
            "population": [10, 20],
        }
    )
    attached, report = attach_psgc_codes(population, municipalities)
    assert report["attached"] == 2
    assert report["unmatched"] == []
    assert attached["psgc_ref"].tolist() == ["0403402000", "0403422000"]
