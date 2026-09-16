---
Status: accepted
---

# Random Forest predictors exclude property characteristics

Chapter 3 states that the revenue and occupancy models "use attributes related to location and
demographics as predictors rather than specific property characteristics", and that this is
precisely what makes it possible to predict performance for a grid cell irrespective of whether an
active listing is present. The engineered predictor set is therefore accessibility and distance
measures, POI density by category, tourism features, and municipal demographic attributes, for
both models. Bedrooms, bathrooms, guest capacity, ratings, superhost status, property type and
room type are excluded from both models. Accessibility distances are computed between points
only — the nearest transportation facility and the nearest tourist attraction — so no
road-distance or expressway measure is introduced.

Chapter 3 contains one sentence that lists "spatial, demographic, POI, and listing attributes"
together. It is treated as a drafting slip, because it contradicts the explicit statement above
and because the chapter's own feature-importance passage enumerates "demographic, spatial,
accessibility, tourism, and POI attributes" with no listing attributes among them.

## Consequences

Predicted revenue is a location-conditioned expectation for a typical STR at that location, not a
forecast for any particular property, which is what allows every grid cell to receive a value.
The cost is explanatory power: a property-aware model would fit the listing data better, and the
reported R² reflects that deliberate trade-off rather than a modelling failure. Feature
importance results likewise describe the contribution of locational characteristics only.
