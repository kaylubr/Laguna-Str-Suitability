# STR Investment Suitability — Laguna

A desk study that scores every majority-land 1km × 1km grid cell in Laguna, Philippines on
short-term-rental investment suitability. It implements the methodology of Chapter 3 of the
thesis, held at `docs/thesis-chr3.md`, which is the source of truth for this build.

The output is a *relative* suitability class per cell. It is not a profitability forecast for any
individual property, and it is not field-verified.

## Method, in the order it runs

1. Preprocess each source separately — AirROI listings and monthly history, PSA population, OSM.
2. Build the training population: dormant listings removed, uncorroborated trailing-twelve-month
   revenue removed → 1,277 listings.
3. Construct the 1km grid over Laguna's land boundary, with 500m and 2km grids for the
   sensitivity runs.
4. Engineer five feature groups: accessibility, POI, tourism, demographic.
5. Train two independent Random Forest regressors — annual revenue and occupancy — on listing-level
   observations with location and demographic predictors.
6. Evaluate with RMSE, MAE and R² on a held-out test set, then permutation importance.
7. Normalize the five suitability indicators, weight them with the Entropy Weight Method, and sum.
8. Classify with Jenks natural breaks into five classes and export for visualization.

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
inclusion rule (0004), the exclusion of property characteristics from the models (0005), and the
target-population exclusions (0006).

## Environment

Python 3.14.4, managed with `uv`.

```
uv sync
uv run pytest
```
