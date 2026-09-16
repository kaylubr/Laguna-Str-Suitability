---
Status: accepted
---

# Cells take their municipality by largest overlap, and PSGC codes come from the PSA reference

Chapter 3 assigns demographic attributes to grid cells "according to the municipality in which each
cell is located" but does not say what happens when a cell lies in more than one. Because cells are
clipped to the land boundary, **508 of 1,764 cells (28.8%) intersect more than one municipality,
and some intersect up to four**. Each cell is therefore assigned to the municipality with the
largest intersection area, computed by polygon overlay, with the overlap share retained as a
diagnostic column. A rule that required a cell to fall wholly inside a municipality was tried first
and rejected: it left 522 cells (30%) with no municipality at all and therefore no demographic
value, which silently removed 417 of 1,277 listings from the training population.

The municipality join keys on **PSGC code rather than name**. Twenty-eight of the 30 municipalities
carry a `ref` tag holding their code on their OSM relation; Pila and Victoria do not. Their codes
are filled from an explicit, documented name-to-code mapping in `reference.py`, sourced from the
PSA Philippine Standard Geographic Code publication rather than inferred from the neighbouring
codes in the sequence. `fill_missing_psgc_refs` reports how many codes came from each source, and
the pipeline asserts that every municipality ends with a code and a population. The target
population is unaffected: the active-listing definition and its exclusions are unchanged, so the
1,277 listings remain the modelling population.

## Consequences

Boundary cells take the majority municipality's population density, which is constant within a
municipality by design, so two adjacent cells on a boundary can differ in density by the difference
between two municipalities' densities. This is a direct effect of the municipal-level demographic
data rather than of the assignment rule.

A defect found while implementing this is recorded here because it was silent rather than loud:
before the reference fill, the two missing codes entered the join as null keys, and pandas matches
null keys to null keys, so the two municipalities cross-joined against the two unmatched PSA rows
and produced four rows from two. Later merges on the duplicated cell IDs compounded it to 87
duplicate rows in the grid table. Merges onto municipalities and cells are now declared
`validate="one_to_one"`, and every spatial-unit table asserts one row per cell ID before any
suitability calculation, so the failure mode fails loudly instead of inflating the unit count.
