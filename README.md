# STR Investment Suitability — Laguna

A desk study that scores every majority-land 1km × 1km grid cell in Laguna, Philippines on
short-term-rental investment suitability. It implements the methodology of Chapter 3 of the
thesis, held at `docs/thesis-chr3.md`, which is the source of truth for this build.

The output is a *relative* suitability class per cell. It is not a profitability forecast for any
individual property, and it is not field-verified.

## Method, in the order it runs

1. Preprocess each source separately — AirROI listings and monthly history, PSA population, OSM.
2. Build the validated target population: dormant listings removed, uncorroborated
   trailing-twelve-month revenue removed → 1,277 listings.
3. Construct the 1km grid over Laguna's derived land boundary → 1,764 cells, with 500m and 2km
   grids for the sensitivity runs.
4. Assign rasters to spatial units: every active listing to its containing cell (1,277 → 1,231
   listings inside the retained grid), every cell to the municipality it overlaps most.
5. Engineer four feature groups: accessibility, POI, tourism and demographic.
6. Train two independent Random Forest regressors — annual revenue and occupancy — on listing-level
   observations with location and demographic predictors.
7. Evaluate with RMSE, MAE and R² on a held-out test set, then permutation importance.
8. Apply both models to every eligible grid cell, producing predicted STR performance potential.
9. Normalize the five suitability indicators, weight them with the Entropy Weight Method, and sum.
10. Classify with Jenks Natural Breaks implemented using the Fisher-Jenks algorithm into five
    classes, and export for visualization.

Random Forest prediction is deliberately separate from composite suitability scoring: the models
predict revenue and occupancy, and do not produce the suitability score themselves.

## Layout

```
assets/boundaries/   committed OSM boundary snapshots
data/                raw and derived data, not committed (see data/README.md)
docs/thesis-chr3.md  the methodology this build follows
docs/adr/            decisions taken where the methodology is silent
src/str_suitability/ pipeline code
tests/               unit tests
```

## Decisions where Chapter 3 is silent

Recorded as ADRs in `docs/adr/`. The load-bearing ones: the grid's projected CRS and cell
inclusion rule (0004), the exclusion of property characteristics from the models (0005), the
target-population exclusions (0006), the hyperparameter search protocol (0010), the municipality
assignment and PSGC reference (0011), what a cell's predicted value means (0012), and the
variables kept outside the models and indicator set (0013).

## Status

All ten methodology stages are implemented and run over the 1,764 retained grid cells. The models
are fitted on 1,231 listings across 288 of those cells; predictions, entropy weights, composite
scores and suitability classes are produced for every retained cell.

Chapter 3 carries its normalization and entropy-weighting formulas as images, so the implementation
follows the mathematical specification supplied for the study, including the convention that a zero
proportion contributes nothing to the entropy sum. Input-side assertions run before the entropy
weighting, the weights are asserted to sum to 1, and classification is Jenks Natural Breaks
implemented using the Fisher-Jenks algorithm.

Suitability scores are relative within Laguna and are built on predicted STR performance potential
rather than observed performance, since only 288 of the 1,764 cells contain an active listing.

## Environment

Python 3.14.4, managed with `uv`.

```
uv sync
uv run pytest
```
