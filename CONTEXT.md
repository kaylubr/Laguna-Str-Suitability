# STR Investment Suitability — Laguna

A desk study that ranks 1km grid cells across the province of Laguna, Philippines by how attractive they are for short-term-rental investment. The output is a relative ranking within the province, not a profitability forecast for any individual property.

## Language

**Grid cell**:
A fixed 1km x 1km square of the surface of Laguna. The spatial unit that everything in the final assessment is reported per.
_Avoid_: Tile, patch, zone, hex

**Suitability indicator**:
A single measured attribute of a grid cell that contributes to the composite assessment. The study uses five: predicted annual revenue, predicted occupancy, POI density, distance to the nearest tourist attraction, and distance to the nearest transportation facility.
_Avoid_: Factor, variable, metric, criterion

**Composite suitability score**:
The single number per grid cell produced by weighting all suitability indicators and summing them.
_Avoid_: Suitability index, score, rating

**Suitability class**:
One of the five ordered bands (Very High through Very Low) that a grid cell's composite suitability score falls into.
_Avoid_: Rating, grade, tier

**Listing**:
One short-term-rental property as recorded by AirROI, identified by its listing ID.
_Avoid_: Property, unit, rental, Airbnb

**Active listing**:
A listing whose trailing-twelve-month revenue and occupancy are both non-zero and whose revenue the monthly history corroborates. The modelling population is drawn from these.
_Avoid_: Valid listing, live listing

**Dormant listing**:
A listing whose trailing-twelve-month revenue and occupancy are both zero because the property was not operating, as distinct from one whose figures are simply missing. Dormant listings are excluded from model training.
_Avoid_: Inactive listing, zero listing, dead listing

**Trailing twelve months (TTM)**:
The August 2025 to July 2026 window over which listing revenue and occupancy are measured.
_Avoid_: Annual, last year, prior period

**Predicted STR performance potential**:
The revenue or occupancy a trained model predicts for a grid cell's location and demographic characteristics. It is a modelled expectation for that location, not an observation of any property.
_Avoid_: Predicted performance, forecast, observed performance

**Municipality**:
One of the 30 city or municipal administrative units of Laguna. The coarsest geographic grouping used in reporting.
_Avoid_: Town, LGU, city

**Barangay**:
A sub-municipality administrative unit. No barangay-level attribute data is currently held for the province.
_Avoid_: Village, district, neighborhood

**Sensitivity resolution**:
A re-run of the whole assessment at a different grid cell size (500m and 2km alongside the primary 1km) to test whether the resulting suitability pattern depends on the resolution chosen.
_Avoid_: Scale test, robustness check
