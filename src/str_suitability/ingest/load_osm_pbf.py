import json
from datetime import UTC, datetime
from pathlib import Path

import geopandas as gpd
import osmium
import pandas as pd
from shapely.geometry import Polygon

from str_suitability.config import GEOGRAPHIC_CRS
from str_suitability.taxonomy import (
    categorize_poi,
    is_poi,
    is_tourist_attraction,
    is_transport_facility,
)

LAGUNA_BBOX = (120.95, 13.90, 121.75, 14.60)
WATER_VALUES = {"water", "lake", "reservoir", "pond", "riverbank", "basin"}


def _in_bbox(lon: float, lat: float) -> bool:
    min_lon, min_lat, max_lon, max_lat = LAGUNA_BBOX
    return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat


def _tags_to_dict(tags) -> dict[str, str]:
    return {tag.k: tag.v for tag in tags}


def _is_water(tags: dict[str, str]) -> bool:
    if tags.get("natural") == "water":
        return True
    return tags.get("water") in WATER_VALUES


def _poi_record(osm_id: int, osm_type: str, lon: float, lat: float, tags: dict[str, str]) -> dict:
    category = categorize_poi(tags)
    return {
        "osm_id": osm_id,
        "osm_type": osm_type,
        "longitude": lon,
        "latitude": lat,
        "name": tags.get("name"),
        "category": str(category) if category is not None else None,
        "is_tourist_attraction": is_tourist_attraction(tags),
        "is_transport_facility": is_transport_facility(tags),
    }


def extract_features(pbf_path: Path) -> tuple[pd.DataFrame, gpd.GeoDataFrame, list[dict]]:
    node_locations: dict[int, tuple[float, float]] = {}
    poi_records = []

    for element in osmium.FileProcessor(str(pbf_path), osmium.osm.NODE):
        location = element.location
        if not location.valid():
            continue
        if not _in_bbox(location.lon, location.lat):
            continue
        node_locations[element.id] = (location.lon, location.lat)
        tags = _tags_to_dict(element.tags)
        if is_poi(tags):
            poi_records.append(
                _poi_record(element.id, "node", location.lon, location.lat, tags)
            )

    water_polygons = []
    bbox_way_ids = set()
    for element in osmium.FileProcessor(str(pbf_path), osmium.osm.WAY):
        touches_bbox = any(node.ref in node_locations for node in element.nodes)
        if not touches_bbox:
            continue
        bbox_way_ids.add(element.id)

        tags = _tags_to_dict(element.tags)
        if not tags:
            continue
        is_water_way = _is_water(tags)
        is_poi_way = is_poi(tags)
        if not (is_water_way or is_poi_way):
            continue
        coordinates = [
            node_locations[node.ref] for node in element.nodes if node.ref in node_locations
        ]
        if len(coordinates) < 3:
            continue
        if is_water_way and len(coordinates) >= 4 and coordinates[0] == coordinates[-1]:
            water_polygons.append({"osm_id": element.id, "geometry": Polygon(coordinates)})
            continue
        if not is_poi_way:
            continue
        if len(coordinates) >= 4 and coordinates[0] == coordinates[-1]:
            polygon = Polygon(coordinates)
            point = (
                polygon.representative_point()
                if polygon.is_valid and not polygon.is_empty
                else None
            )
            point = (point.x, point.y) if point is not None else None
        else:
            point = (
                sum(coordinate[0] for coordinate in coordinates) / len(coordinates),
                sum(coordinate[1] for coordinate in coordinates) / len(coordinates),
            )
        if point is None or not _in_bbox(*point):
            continue
        poi_records.append(_poi_record(element.id, "way", point[0], point[1], tags))

    tagged_relations = []
    for element in osmium.FileProcessor(str(pbf_path), osmium.osm.RELATION):
        tags = _tags_to_dict(element.tags)
        if not _is_water(tags):
            continue
        touches_bbox = any(
            member.ref in bbox_way_ids for member in element.members if member.type == "w"
        )
        if not touches_bbox:
            continue
        tagged_relations.append(
            {"osm_id": element.id, "kind": "water", "name": tags.get("name")}
        )

    pois = pd.DataFrame.from_records(poi_records)
    water = gpd.GeoDataFrame(water_polygons, geometry="geometry", crs=GEOGRAPHIC_CRS)
    return pois, water, tagged_relations


def fetch_relation_geometries(relation_ids: list[int]) -> gpd.GeoDataFrame:
    from str_suitability.ingest.load_osm import fetch_relation, relation_to_geometry

    records = []
    for relation_id in relation_ids:
        payload = fetch_relation(relation_id, full=True)
        geometry = relation_to_geometry(payload, relation_id)
        if geometry is not None:
            records.append({"osm_id": relation_id, "geometry": geometry})
    return gpd.GeoDataFrame(records, geometry="geometry", crs=GEOGRAPHIC_CRS)


def snapshot_features(pbf_path: Path, boundary_dir: Path, feature_dir: Path) -> dict:
    feature_dir.mkdir(parents=True, exist_ok=True)
    pois, water, tagged_relations = extract_features(pbf_path)

    boundary = gpd.read_file(boundary_dir / "laguna_province.geojson").to_crs(GEOGRAPHIC_CRS)
    province_polygon = boundary.geometry.union_all()

    poi_points = gpd.GeoDataFrame(
        pois, geometry=gpd.points_from_xy(pois["longitude"], pois["latitude"]), crs=GEOGRAPHIC_CRS
    )
    poi_points = poi_points[poi_points.geometry.within(province_polygon)].reset_index(drop=True)
    poi_points.to_parquet(feature_dir / "laguna_pois.parquet", index=False)

    attractions = poi_points[poi_points["is_tourist_attraction"]].reset_index(drop=True)
    attractions.to_parquet(feature_dir / "laguna_tourist_attractions.parquet", index=False)

    water_relation_ids = [item["osm_id"] for item in tagged_relations if item["kind"] == "water"]
    relation_water = (
        fetch_relation_geometries(water_relation_ids)
        if water_relation_ids
        else gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs=GEOGRAPHIC_CRS)
    )
    if not relation_water.empty:
        relation_water = relation_water[relation_water.geometry.intersects(province_polygon)]
    combined_water = gpd.GeoDataFrame(
        pd.concat([water, relation_water], ignore_index=True), geometry="geometry", crs=GEOGRAPHIC_CRS
    )
    combined_water = combined_water[combined_water.geometry.intersects(province_polygon)].reset_index(drop=True)
    combined_water.to_file(feature_dir / "laguna_water.geojson", driver="GeoJSON")

    checksum_path = Path(str(pbf_path) + ".md5")
    metadata = {
        "source": "Geofabrik Philippines extract, https://download.geofabrik.de/asia/philippines-latest.osm.pbf",
        "retrieved_at": datetime.now(UTC).isoformat(),
        "pbf_bytes": pbf_path.stat().st_size,
        "pbf_md5": checksum_path.read_text().split()[0] if checksum_path.exists() else None,
        "extraction_bbox": LAGUNA_BBOX,
        "poi_records_before_boundary_filter": int(len(pois)),
        "poi_records_after_boundary_filter": int(len(poi_points)),
        "tourist_attractions": int(len(attractions)),
        "transport_facilities": int(poi_points["is_transport_facility"].sum()),
        "water_way_polygons": int(len(water)),
        "water_relation_polygons": int(len(relation_water)),
        "water_polygons_total": int(len(combined_water)),
        "poi_category_counts": poi_points["category"].value_counts().to_dict(),
    }
    (feature_dir / "osm_extract.metadata.json").write_text(json.dumps(metadata, indent=2))
    return metadata
