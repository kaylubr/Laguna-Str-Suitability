---
Status: accepted
---

# Grid construction: projected CRS, land boundary, and cell inclusion rule

Chapter 3 fixes the cell size at 1km, defines the study extent as the administrative boundary of
Laguna, restricts all spatial input data to that extent by clipping before the grid is created,
expects roughly 1,928 cells at about 64 per municipality, and repeats the analysis on 500m and
2km grids. It does not name a projected coordinate system, does not say how a cell that only
partly overlaps the study area is treated, and does not distinguish the administrative boundary
from the land within it. Those three silences are decisions recorded here.

All metric work is done in **EPSG:32651 (UTM zone 51N)**, which covers Laguna's longitude range
and gives true kilometres per cell, so "1km" means the same distance everywhere in the province.
Distances that Chapter 3 specifies are still computed with the Haversine formula on geographic
coordinates; the projection exists to make the grid regular and areas correct.

The **land boundary is derived** by subtracting OSM water polygons from the OSM administrative
polygon for the province. The administrative extent is not usable as-is because Laguna's boundary
runs through Laguna de Bay, so the raw polygon includes a large area of open water that no
accessibility or POI feature can meaningfully describe. The committed snapshot measures the
administrative extent at **2,108.4 km²**, against roughly 1,918 km² of land area and Chapter 3's
1,928 cells — so about 190 km², close to 190 of the 1km cells, is lake rather than land. The water
layer is therefore not a cosmetic refinement: without it the grid would be roughly 10% too large
and the extra cells would be open water.

The grid is anchored on integer-kilometre UTM coordinates, so the 500m and 2km grids nest inside
the 1km grid rather than drifting relative to it. A cell is retained when its **land coverage is
at least 50% of its area** — equivalently, a majority-water cell is dropped — and its geometry is
clipped to the land boundary so that area-weighted features are computed on the retained part
only.

## Consequences

Measured on the committed snapshots, the administrative extent is 2,108.4 km² and the water inside
it is 355.1 km² — of which **Laguna de Bay alone accounts for 330.0 km² (92.9%)**, with the other
246 water bodies contributing 25 km² between them. The derived land boundary is therefore
1,753.3 km² and the retained grid is **1,764 cells**, against Chapter 3's stated 1,928. The
alternative rule of keeping any cell that touches land gives 2,006, so 1,928 sits between the two
candidate rules and matches neither: it is close to PSA's 1,918 km² land area, which is a figure
about land rather than a count of cells. **The grid is therefore not forced to reproduce 1,928**,
and the deviation is recorded here as the measured difference between an approximate figure in the
methodology and a defensible boundary derivation.

Excluding majority-water cells additionally removes cells whose centroid falls on the lake, which
would otherwise record near-zero distance to lake-adjacent facilities and rank as artificially
suitable. It also costs a small number of training observations: 46 of the 1,277 active listings
fall outside any retained cell, 17 because coordinate jitter places them on water and 26 because
their cell was dropped by the majority-land rule.
