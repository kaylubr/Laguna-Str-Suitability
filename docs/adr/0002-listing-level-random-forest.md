---
Status: accepted
---

# Train the Random Forest models on listing-level observations and predict every grid cell

Chapter 3 sets the study up in two stages: models are developed on listing-level STR observations
with location and demographic predictors, and the trained models are then applied to the
corresponding spatial and demographic characteristics of the grid cells. Both models therefore
train on listing rows with TTM revenue and TTM occupancy as targets, and each listing takes the
spatial and demographic predictors of the grid cell containing its coordinates. Because those
predictors describe location rather than property, a trained model can be applied to any grid
cell whether or not it holds an active listing, so the grid-level prediction stage emits annual
revenue and occupancy for every cell in the grid.

## Considered Options

Averaging listings into cell-level training rows was considered and set aside: for most cells it
would substitute a single listing's value for the whole cell's potential, and it would change
what the target means, since Chapter 3 defines the targets on listings. Assigning a reference
property profile to each cell was also considered and set aside as unnecessary once the
predictor set is confined to location and demographic attributes.

## Consequences

The comparison between observed and predicted performance is a comparison at different levels of
observation: the models are fitted on individual listings but produce location-level potential.
Chapter 3 states this explicitly and frames the grid values as general STR performance potential
rather than a forecast for any particular property.
