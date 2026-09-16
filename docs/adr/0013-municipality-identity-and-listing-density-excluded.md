---
Status: accepted
---

# Municipality identity and listing density stay out of the models and the indicator set

Two variables sit close to the boundary of the specified design and are deliberately kept outside
it.

**Population density is retained as a predictor** because Chapter 3 names it explicitly among the
demographic attributes converted to numeric predictors. It is municipal-level, so it is constant
across every cell assigned to the same municipality, and that constancy has a measured consequence:
in the occupancy model it is the only predictor whose permutation importance rises above noise.
That is what a municipality-level variable looks like when it is the only source of
between-municipality variation — it is doing municipality-level work. It nonetheless remains a
demographic predictor and is not reclassified.

**Municipality name and municipality code are not added as predictors.** They carry much the same
information as the density, only more explicitly, and adding them would turn the model into a
municipality classifier while double-counting a single input. They are used for spatial assignment,
demographic joining, validation and visualisation, and for nothing else.

**Listing density is excluded from both the Random Forest predictors and the five suitability
indicators.** Chapter 3 enumerates four predictor groups and exactly five indicators, and listing
density appears in neither. It may be calculated as a diagnostic or supporting visualisation, but
it must not enter either the trained models or the composite score. Had it been allowed in, it would
also have been circular: it measures the local STR market that the suitability score is trying to
assess.

## Consequences

The predictor set stays exactly as specified, and no variable was added at any point to improve
model performance. The occupancy model's dependence on a municipality-level predictor is recorded
here as an observed property of the specified design rather than corrected, because correcting it
would mean departing from Chapter 3's demographic predictor set.
