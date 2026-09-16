---
Status: accepted
---

# OSM features come from a local Geofabrik extract, and demographics join on PSGC code

Two implementation decisions taken while building the pipeline.

**Feature extraction uses a local PBF extract rather than an Overpass query.** Boundaries were
already retrieved from the OSM API because Overpass was unreachable, but the OSM API serves
relations by ID and cannot answer tag-based questions, so it cannot supply POIs, tourism features
or the water layer. Those are extracted from the Geofabrik Philippines extract
(`philippines-latest.osm.pbf`) parsed locally with pyosmium. This remains OpenStreetMap data, so
Chapter 3's stated source is unchanged; what changes is the retrieval mechanism. The extract is
recorded with its retrieval date and MD5 so a run can be tied to one snapshot of the data, and the
extraction is a deterministic tag filter driven by the version-controlled taxonomy in
`taxonomy.py` rather than by a hand-picked list of places.

**The demographic join keys on PSGC code rather than municipality name.** The OSM boundary
relations carry a `ref` tag holding each municipality's ten-digit PSGC code, and those codes
reconcile exactly, all 30, with the PSA population table. AirROI listing records carry the same
codes in short form (`PH0403401` against `0403401000`), so the listing-to-municipality and
municipality-to-population joins can both be done on code. This is an **implementation detail of
the spatial join, not a restatement of the methodology**: Chapter 3 describes assigning
demographic attributes to cells "according to the municipality in which each cell is located" and
does not prescribe how the identifier is matched. Name matching was rejected because the retrieved
data already demonstrates it fails — AirROI's own `location_info.region` field labels a Laguna
listing as Pangasinan — and because a code join is exact where a name join needs diacritic and
alias handling.

## Consequences

The extraction depends on a ~600MB download that is not committed; the derived, much smaller
snapshots under `assets/osm/` are committed instead, so the pipeline reruns offline from them.
Rounding the code join means a listing whose code is absent from the boundary snapshot would be
dropped rather than silently mis-assigned, so the join reports unmatched rows instead of coercing
them.
