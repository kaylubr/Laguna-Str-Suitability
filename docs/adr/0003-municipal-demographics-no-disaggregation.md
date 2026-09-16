---
Status: accepted
---

# Demographics are linked by municipality and are constant across a municipality's cells

Chapter 3 links PSA demographic attributes to grid cells "according to the municipality in which
each cell is located", and cites the municipal availability of those demographics as one of the
three reasons the grid is 1km rather than finer. Municipal-level linkage is therefore the method,
not a shortfall in the data: every cell inside a municipality carries the same population density
value. Spreading municipal population across cells in proportion to built-up area was considered
and rejected, because it would manufacture within-municipality variation that no source supports.

## Consequences

The predictor contributes no within-municipality discrimination, so it acts as a municipality-level
context term rather than a spatial gradient. Because it is constant within a municipality it can
only influence predicted revenue and occupancy through the Random Forest models; it does not enter
the composite score directly, since Chapter 3's five suitability indicators do not include a
demographic indicator. Chapter 3 also refers to "population density and other demographic
information" being converted to numeric predictors, whereas the PSA table held contains population
counts only, so population density is the sole demographic predictor available. Population differs
across all 30 municipalities, which means this predictor also identifies the municipality: name and
code are excluded as model inputs, but the demographic predictor cannot be used without carrying
some municipality-level information, and that is recorded here rather than worked around.
