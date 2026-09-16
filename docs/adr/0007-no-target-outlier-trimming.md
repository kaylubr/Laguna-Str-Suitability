---
Status: accepted
---

# Target outliers are retained: no IQR or percentile trimming

Chapter 3 states that "extreme values are screened using the criteria for outliers" but never
specifies the criterion, and that silence is resolved here by retaining the target distribution
as observed. Revenue reaches 8,336,456 against a median of 127,458, and the observations in that
tail are exactly the high-performing listings that a short-term-rental investment-suitability
study exists to identify: trimming them would remove the evidence that defines the highest
suitability class while making RMSE and R² flatter simply because the hardest observations were
deleted. An IQR fence at 1.5× would have removed a substantial share of the upper tail. Random
Forest regression is insensitive to the monotone rescaling that extreme targets induce, so no
robustness is gained by screening them.

The screened quantities are therefore limited to the established data-quality checks: dormant
listings removed, uncorroborated trailing-twelve-month revenue removed, invalid coordinates and
duplicate listing IDs rejected. No IQR, percentile, or z-score screening is applied to revenue or
occupancy targets, and the distribution is reported rather than trimmed.

## Consequences

Reported MAE and RMSE are large in absolute terms because the target is genuinely heavy-tailed,
and they are reported untrimmed. Permutation importance and the predicted values inherit the same
distribution. An IQR-based sensitivity check may be run as a separate, clearly labelled robustness
analysis, but it does not replace the primary model and its reported RMSE, MAE and R².
