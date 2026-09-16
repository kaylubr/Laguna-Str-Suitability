---
Status: accepted
---

# Hyperparameter grid, search protocol, and the 80:20 sampling method

Chapter 3 specifies an 80:20 training/test split, five-fold cross-validation with grid search, and
names five hyperparameters — number of trees, max depth, min samples split, min samples leaf, and
max features — but gives no values for any of them, and does not say how observations are drawn
into the two splits. Those silences are resolved here.

**Sampling.** The split is a random 80:20 draw using a fixed seed, so the partition is
reproducible. Chapter 3 specifies the ratio only. The test set is drawn once and is not touched
during tuning: the grid search runs entirely inside the training split, and the held-out metrics
are computed once on the final model, so the reported RMSE, MAE and R² are not contaminated by
model selection.

**Scoring.** Candidate parameter sets are compared on cross-validated RMSE, the metric Chapter 3
lists first and the one most sensitive to the heavy right tail in the revenue target.

**Grid.** `n_estimators` [200, 500], `max_depth` [None, 10, 20], `min_samples_split` [2, 5],
`min_samples_leaf` [1, 2], `max_features` ["sqrt", 0.5] — 48 candidate sets, 240 fits per model.

## Consequences

The grid is deliberately modest rather than wide. With roughly 1,020 training rows, a
several-hundred-point grid would be selecting on cross-validation noise rather than signal, and
the selected optimum would be less likely to hold on the test set. Coverage of all five named
hyperparameters is preserved, so the search is a genuine implementation of Chapter 3's procedure
rather than a shortcut. A wider grid can be substituted in `config.py` and re-run if a reviewer
asks for it; the search protocol above holds either way.
