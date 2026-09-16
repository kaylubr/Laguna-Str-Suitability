---
Status: accepted
---

# Target population: dormant listings and uncorroborated revenue are excluded

Chapter 3 removes dormant listings from consideration because their zero revenue and occupancy
"signify the property status quo rather than the result of its operations", and states that the
monthly historical data "is used to identify and, if possible, correct inconsistencies in the
listing's trailing-twelve-month revenue and occupancy data before the final targets are built".
Applying both rules to the retrieved data:

- Of 2,080 listings, **732 are dormant** — TTM revenue and TTM occupancy both exactly zero. They
  are removed under Chapter 3's own rule.
- A further **71 report positive TTM revenue that no month inside the trailing-twelve-month window
  corroborates.** Fifty-nine have no window months at all, and the rest have only zero-revenue
  months. Chapter 3 asks for these inconsistencies to be corrected where possible; for these 71 it
  is not possible, because there is no monthly evidence to correct them with. Their reported
  revenue is also an order of magnitude below the rest of the population (median 11,544 against
  127,458), which is the signature of a stale trailing-twelve-month figure.

Those 71 are excluded as well, so the **validated target population is 1,277 listings**. This is a
data-quality decision about target validity, not a change to the modelling method: Chapter 3's
definition of an active listing (non-zero revenue and occupancy) would have retained them, and
that definition is otherwise applied unchanged.

A second and entirely separate reduction happens later, at spatial assignment, and it is not a
target-validity rule. Each active listing is placed in the grid cell containing its coordinates,
and **46 of the 1,277 fall outside the retained grid**, leaving **1,231 listings as the final
training population**. Those 46 are lost because of where they sit, not because of what they
reported: 17 have coordinates that jitter onto a water polygon, 26 fall in cells dropped by the
majority-land rule, and 3 sit outside the province polygon altogether. Twenty-four of the 46 are in
Cavinti, which is lakeside. Both counts are therefore meaningful and both are reported: 1,277 is
the validated target population before spatial assignment, and 1,231 is the population the models
are actually fitted on.

## Consequences

Thirty-nine percent of retrieved listings are excluded in total, and the exclusion is **not spatially
uniform** — some municipalities lose a far larger share of their listings than others, and
municipalities whose listings are mostly dormant contribute almost no training observations at all.
Predictions are still produced for every grid cell, since the models take location and demographic
predictors rather than listing attributes, but the cells whose training evidence was removed are
the cells whose predictions rest most heavily on extrapolation. The diagnostic listing-density layer
is the natural place to make this visible.

The final training population of 1,231 listings occupies **288 of the 1,764 grid cells**, so the
population the models learn from is concentrated in a sixth of the study area.
