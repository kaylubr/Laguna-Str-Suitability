---
Status: accepted
---

# OSM data is retrieved from the OSM API and committed as snapshots

Administrative boundaries are retrieved from the OpenStreetMap API
(`api.openstreetmap.org/api/0.6`), not from Overpass and not through osmnx. Overpass returned
HTTP 504 on every attempt from this environment, across two independent endpoints and repeated
retries, while the OSM API answered in about a second and served the whole province. The province
relation (1503483) exposes its 30 member municipalities directly, and each of those relations
carries a `ref` tag holding its PSGC code and a `population` tag dated 2024-07-01 whose values
match the PSA table exactly — so the boundary snapshot also supplies the PSGC codes the PSA file
lacked and provides the independent name reconciliation Chapter 3 calls for. Retrieving full
relation geometry rather than Nominatim's `polygon_geojson` was preferred because Nominatim
simplifies geometry, and cell coverage, POI counts and distances all read that geometry.

Two candidate routes were rejected. osmnx was rejected because it fetches through Overpass, which
is unreachable here. Nominatim polygon geometry was rejected as the primary source because it is
simplified for display.

## Consequences

Boundary snapshots are committed under `assets/boundaries/` with retrieval timestamps, so the grid
can be rebuilt offline and cannot fail during a defense. POIs, tourism features and the water layer
still require a tag-based extraction that the OSM API cannot serve, since it returns relations by
ID rather than by tag. If Overpass stays unreachable, those layers are extracted from a Geofabrik
Philippines extract parsed locally — still OpenStreetMap data, so Chapter 3's data source is
unchanged, but it adds a large one-time download and a parser dependency. Which route is taken is
recorded here when the extraction is built.
