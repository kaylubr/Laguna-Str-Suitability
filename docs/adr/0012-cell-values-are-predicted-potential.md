---
Status: accepted
---

# Grid-cell values are predicted potential, and the reported fit is the outcome of the methodology

Every grid cell in the study area receives a predicted revenue and a predicted occupancy, but
**only 288 of the 1,764 cells contain an active listing at all**. For the other 1,476 cells — 84%
of the grid — those values are predictions from the location's and municipality's characteristics,
with no observed STR performance behind them. They must be described as **predicted STR performance
potential**: the performance the specified model expects of an STR at that location, not a record
of what any property there earned. Any map, endpoint or written interpretation that presents them
as observed performance is wrong, and the same distinction carries through to the composite
suitability score, which is built on them.

This is not a side effect to be minimised. Chapter 3 applies the trained models to grid cells
precisely so that a listing need not be present, which is why the models take location and
demographic predictors rather than property characteristics.

**Reported model fit is a result, not a defect.** The revenue model scores R² 0.258 and the
occupancy model R² 0.038 on the held-out test set. Those are the observed predictive performance of
the specified model and are reported as such. The occupancy figure in particular is not a reason to
modify the methodology: property characteristics would very likely raise it, but they are excluded
by ADR 0005, and including them would make the grid-level prediction stage impossible for cells
without listings — destroying the province-wide coverage the two-stage design exists to produce. The
low figure is a finding about how much of STR occupancy is explicable from location and municipal
demographics alone, which is itself informative for a location-based suitability study.

## Consequences

The composite suitability score inherits both properties: it is a location-level construct, and its
performance indicators are model output rather than measurement. Suitability classes must not be
interpreted as observations of what happened in a cell, and the distinction between the 288 cells
with training evidence and the 1,476 without is a stated limitation rather than a hidden one.
