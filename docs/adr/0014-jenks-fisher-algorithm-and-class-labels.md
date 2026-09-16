---
Status: accepted
---

# Jenks Natural Breaks is implemented with the Fisher-Jenks algorithm

Chapter 3 specifies "the Jenks Natural Breaks classification method" to divide the composite
suitability values into five classes. The obvious library class for that, `mapclassify.NaturalBreaks`,
**is not reproducible**: on identical input, five successive runs produced the same breaks four
times and a different second break once (`0.3571428571` against `0.4214285714`), which moved a cell
across a class boundary. A study that reports which class each of 1,764 cells falls into cannot
have that boundary move between runs.

Classification therefore uses **`mapclassify.FisherJenks`**, which returned identical breaks across
every run. Fisher's method is the exact optimal-partition solution to the same problem — the
classical Jenks natural-breaks algorithm — so this is the specified method implemented
deterministically, not a substitute methodology.

The method is described throughout as **"Jenks Natural Breaks classification implemented using the
Fisher-Jenks algorithm"**, that string is carried in the `classify` module and reported in the
suitability summary, and the five class labels are exactly:

1. Very High Suitability
2. High Suitability
3. Moderate Suitability
4. Low Suitability
5. Very Low Suitability

## Consequences

A test asserts that repeated classification of the same scores returns identical labels, so a
regression to a non-deterministic classifier fails the suite rather than silently altering classes.

The lowest class is labelled **"Very Low Suitability"**, following Chapter 3's own list of the five
categories. An earlier draft of the mathematical specification called it "Very Low / Unsuitable";
that phrasing is not used anywhere in the output, because Chapter 3 does not contain it.
