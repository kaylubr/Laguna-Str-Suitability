import json
from datetime import UTC, datetime
from pathlib import Path

import geopandas as gpd
import requests
from shapely.geometry import Polygon
from shapely.ops import unary_union

from str_suitability.config import GEOGRAPHIC_CRS

OSM_API_ROOT = "https://api.openstreetmap.org/api/0.6"
REQUEST_HEADERS = {"User-Agent": "str-suitability-research/0.1 (thesis build)"}
LAGUNA_PROVINCE_RELATION_ID = 1503483


def fetch_relation(relation_id: int, full: bool = True) -> dict:
    suffix = "/full.json" if full else ".json"
    response = requests.get(
        f"{OSM_API_ROOT}/relation/{relation_id}{suffix}",
        headers=REQUEST_HEADERS,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def index_nodes(elements: list[dict]) -> dict[int, tuple[float, float]]:
    return {
        element["id"]: (element["lon"], element["lat"])
        for element in elements
        if element["type"] == "node" and "lon" in element and "lat" in element
    }


def collect_ways(elements: list[dict]) -> dict[int, dict]:
    return {element["id"]: element for element in elements if element["type"] == "way"}


def assemble_rings(way_node_lists: list[list[int]]) -> tuple[list[list[int]], int]:
    pending = [list(way) for way in way_node_lists]
    rings = []
    unclosed = 0
    while pending:
        chain = pending.pop(0)
        closed = False
        while True:
            if chain[0] == chain[-1] and len(chain) > 3:
                closed = True
                break
            matched = False
            for index, way in enumerate(pending):
                if way[0] == chain[-1]:
                    chain.extend(way[1:])
                elif way[-1] == chain[-1]:
                    chain.extend(list(reversed(way))[1:])
                elif way[-1] == chain[0]:
                    chain = way[:-1] + chain
                elif way[0] == chain[0]:
                    chain = list(reversed(way))[:-1] + chain
                else:
                    continue
                pending.pop(index)
                matched = True
                break
            if not matched:
                break
        if closed:
            rings.append(chain)
        else:
            unclosed += 1
    return rings, unclosed


def find_relation(elements: list[dict], relation_id: int) -> dict:
    for element in elements:
        if element["type"] == "relation" and element["id"] == relation_id:
            return element
    raise KeyError(f"relation {relation_id} not present in response")


def relation_to_geometry(payload: dict, relation_id: int):
    elements = payload["elements"]
    relation = find_relation(elements, relation_id)
    nodes = index_nodes(elements)
    ways = collect_ways(elements)

    outer_chains, inner_chains = [], []
    for member in relation["members"]:
        if member["type"] != "way":
            continue
        way = ways.get(member["ref"])
        if way is None:
            continue
        if member["role"] == "inner":
            inner_chains.append(way["nodes"])
        elif member["role"] in ("outer", ""):
            outer_chains.append(way["nodes"])

    if not outer_chains:
        return None

    def to_coordinates(ring: list[int]) -> list[tuple[float, float]]:
        return [nodes[node_id] for node_id in ring if node_id in nodes]

    outer_rings, _ = assemble_rings(outer_chains)
    inner_rings, _ = assemble_rings(inner_chains)
    outer_rings = [to_coordinates(ring) for ring in outer_rings if len(ring) >= 4]
    inner_rings = [to_coordinates(ring) for ring in inner_rings if len(ring) >= 4]
    if not outer_rings:
        return None

    polygons = [Polygon(ring) for ring in outer_rings]
    for hole in inner_rings:
        hole_shape = Polygon(hole)
        for index, polygon in enumerate(polygons):
            if polygon.contains(hole_shape.representative_point()):
                polygons[index] = Polygon(polygon.exterior, [*polygon.interiors, hole])
                break

    return unary_union(polygons)


def relation_metadata(payload: dict, relation_id: int) -> dict:
    relation = find_relation(payload["elements"], relation_id)
    tags = relation.get("tags", {})
    return {
        "osm_relation_id": relation["id"],
        "name": tags.get("name"),
        "admin_level": tags.get("admin_level"),
        "psgc_ref": tags.get("ref"),
        "population": tags.get("population"),
        "population_date": tags.get("population:date"),
        "official_name": tags.get("official_name"),
        "wikidata": tags.get("wikidata"),
    }


def fetch_member_relation_ids(province_payload: dict, province_relation_id: int) -> list[int]:
    relation = find_relation(province_payload["elements"], province_relation_id)
    return [member["ref"] for member in relation["members"] if member["type"] == "relation"]


def build_province_frame(province_relation_id: int) -> gpd.GeoDataFrame:
    payload = fetch_relation(province_relation_id, full=True)
    record = relation_metadata(payload, province_relation_id)
    geometry = relation_to_geometry(payload, province_relation_id)
    return gpd.GeoDataFrame([record], geometry=[geometry], crs=GEOGRAPHIC_CRS)


def build_municipality_frame(province_relation_id: int) -> gpd.GeoDataFrame:
    member_ids = fetch_member_relation_ids(
        fetch_relation(province_relation_id, full=False), province_relation_id
    )
    records = []
    for relation_id in member_ids:
        payload = fetch_relation(relation_id, full=True)
        record = relation_metadata(payload, relation_id)
        record["geometry"] = relation_to_geometry(payload, relation_id)
        records.append(record)
    frame = gpd.GeoDataFrame(records, geometry="geometry", crs=GEOGRAPHIC_CRS)
    return frame.dropna(subset=["geometry"]).reset_index(drop=True)


def snapshot_boundaries(boundary_dir: Path, province_relation_id: int = LAGUNA_PROVINCE_RELATION_ID) -> dict:
    retrieved_at = datetime.now(UTC).isoformat()
    province = build_province_frame(province_relation_id)
    municipalities = build_municipality_frame(province_relation_id)

    boundary_dir.mkdir(parents=True, exist_ok=True)
    province.to_file(boundary_dir / "laguna_province.geojson", driver="GeoJSON")
    municipalities.to_file(boundary_dir / "laguna_municipalities.geojson", driver="GeoJSON")

    projected = municipalities.to_crs("EPSG:32651")
    metadata = {
        "source": "OpenStreetMap API, api.openstreetmap.org/api/0.6 relation geometry",
        "province_relation_id": province_relation_id,
        "retrieved_at": retrieved_at,
        "province_features": int(len(province)),
        "municipality_features": int(len(municipalities)),
        "municipality_area_km2": {
            row["name"]: round(row.geometry.area / 1_000_000, 3)
            for _, row in projected.iterrows()
        },
        "municipality_psgc_refs": [
            {"name": row["name"], "psgc_ref": row["psgc_ref"], "population": row["population"]}
            for _, row in municipalities.iterrows()
        ],
        "province_area_km2": round(province.to_crs("EPSG:32651").geometry.area.sum() / 1_000_000, 3),
    }
    (boundary_dir / "laguna_boundaries.metadata.json").write_text(json.dumps(metadata, indent=2))
    return metadata


def load_boundaries(boundary_dir: Path) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    province = gpd.read_file(boundary_dir / "laguna_province.geojson")
    municipalities = gpd.read_file(boundary_dir / "laguna_municipalities.geojson")
    return province, municipalities
