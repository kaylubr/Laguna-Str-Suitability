import pandas as pd
import pytest

from str_suitability.taxonomy import (
    PoiCategory,
    categorize_poi,
    is_poi,
    is_tourist_attraction,
    is_transport_facility,
)


def test_restaurant_and_commercial_and_recreation_are_separated():
    assert categorize_poi({"amenity": "cafe"}) == PoiCategory.RESTAURANTS
    assert categorize_poi({"shop": "hardware"}) == PoiCategory.COMMERCIAL
    assert categorize_poi({"leisure": "park"}) == PoiCategory.RECREATION


def test_transportation_takes_precedence_over_commercial():
    assert categorize_poi({"amenity": "fuel", "shop": "convenience"}) == PoiCategory.TRANSPORTATION


def test_tourist_attraction_precedes_recreation():
    assert categorize_poi({"tourism": "viewpoint", "leisure": "park"}) == PoiCategory.TOURIST_ATTRACTION


def test_poi_without_specific_category_falls_to_other_facilities():
    assert categorize_poi({"amenity": "pharmacy"}) == PoiCategory.OTHER_FACILITIES


def test_non_poi_tags_are_rejected():
    assert not is_poi({"highway": "residential"})
    assert categorize_poi({"highway": "residential"}) is None
    assert categorize_poi({"natural": "water"}) is None


def test_bus_stop_is_a_poi_but_not_a_transport_facility():
    assert categorize_poi({"highway": "bus_stop"}) == PoiCategory.TRANSPORTATION
    assert not is_transport_facility({"highway": "bus_stop"})
    assert is_transport_facility({"amenity": "bus_station"})


def test_tourist_attraction_whitelist_excludes_accommodation_tags():
    assert is_tourist_attraction({"tourism": "museum"})
    assert is_tourist_attraction({"historic": "ruins"})
    assert not is_tourist_attraction({"tourism": "hotel"})
    assert not is_tourist_attraction({"tourism": "camp_site"})


def test_empty_tags_are_not_a_poi():
    assert categorize_poi({}) is None


@pytest.mark.parametrize("value", ["restaurant", "bar", "fast_food"])
def test_restaurant_variants(value):
    assert categorize_poi({"amenity": value}) == PoiCategory.RESTAURANTS


def test_taxonomy_is_pure_and_does_not_mutate_input():
    tags = {"amenity": "cafe"}
    categorize_poi(tags)
    assert tags == {"amenity": "cafe"}


def test_categorize_poi_returns_none_for_empty_frame_like_input():
    assert categorize_poi(pd.Series(dtype=object).to_dict()) is None
