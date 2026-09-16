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

Those 71 are excluded as well, so the **final training population is 1,277 listings**. This is a
data-quality decision about target validity, not a change to the modelling method: Chapter 3's
definition of an active listing (non-zero revenue and occupancy) would have retained them, and
that definition is otherwise applied unchanged.

## Consequences

Thirty-nine percent of retrieved listings are excluded in total, and the exclusion is **not spatially
uniform** — some municipalities lose a far larger share of their listings than others, and
municipalities whose listings are mostly dormant contribute almost no training observations at all.
Predictions are still produced for every grid cell, since the models take location and demographic
predictors rather than listing attributes, but the cells whose training evidence was removed are
the cells whose predictions rest most heavily on extrapolation. The diagnostic listing-density layer
is the natural place to make this visible.
