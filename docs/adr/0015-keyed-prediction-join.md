---
Status: accepted
---

# Predictions are joined to cells by an explicit key written by the producer

The pipeline persisted predictions as a bare single column with no cell identifier, so the scoring
stage could only attach them to grid cells by row order. That alignment was real but unenforced: it
held solely because both files were written from the same frame in the same row order, and nothing
in the code stated, checked or tested it. Any reordering of the grid before writing would have
silently attached every prediction to the wrong cell, and every downstream weight, score and class
would have been wrong without any error being raised.

A key attached inside the scoring stage would have fixed nothing, because it could only have been
attached by the same row order it was meant to replace. **The producer therefore writes the key.**
Each prediction file now carries `cell_id` alongside its prediction column, and the scoring stage
joins on that key, asserting that the identifier is present, unique and non-null, that the
prediction file covers exactly the same set of cells as the grid, and that the merge is
one-to-one.

## Consequences

Row order can no longer affect which prediction a cell receives. Regression tests reverse the
prediction rows, shuffle them, shuffle each prediction file independently of the other, and shuffle
the grid itself, and assert that every cell still receives its own prediction. A prediction file
without a `cell_id` column now fails loudly instead of being silently aligned by position.

The change is confined to the output step: no prediction value, model, predictor, hyperparameter or
spatial assignment was altered. Re-running the pipeline to regenerate the keyed files reproduced
the previously stored predictions **bit-identically** (maximum absolute difference 0.0), which
confirms both that the join was correct and that the pipeline is reproducible.
