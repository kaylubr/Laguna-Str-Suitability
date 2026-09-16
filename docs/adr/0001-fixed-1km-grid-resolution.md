# Fix the grid at 1km rather than a finer resolution

AirROI jitters the published coordinates of every listing by up to roughly 150m to protect host privacy, so a cell finer than 1km would locate each listing inside a square smaller than its own positional error: the analysis would resolve jitter rather than geography. 1km is therefore a data-imposed floor on resolution, not a compromise on precision, and the 500m sensitivity run exists to demonstrate the point rather than to improve the map.

## Consequences

The grid cannot be refined to sharpen the map, and any request to do so is a methodological error rather than an optimisation. Any change to the cell size invalidates every spatial feature and both trained models, so the resolution is effectively frozen for the life of the study.
