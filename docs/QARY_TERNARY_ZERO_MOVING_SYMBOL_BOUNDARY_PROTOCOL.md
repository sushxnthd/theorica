# Frozen protocol: zero-moving symbol boundary

## Conjecture under attack

The completed holdout panel established exact policy transport under the
all-coordinate involution `1 <-> 2`, which fixes symbol 0.  A tempting stronger
claim is that every coordinatewise alphabet permutation preserves the weighted
prefix-query game.

This experiment applies `0 <-> 1` in all three coordinates to P0, producing

`111, 110, 101, 100, 011, 010, 001, 000, 211, 201`.

The target has not appeared in an earlier exact solve.

## Structural prediction frozen before solving

The prefix-query library uses outcome 0 both for an observed zero and for
completions outside a query prefix.  Moving symbol 0 therefore need not map
query cells bijectively.  A level-coloured partition-hypergraph refinement,
run before either exact endpoint, separates source and target after five
rounds: the source color-class sizes contain two classes of size 5, whereas
the target contains two classes of size 3 and a different singleton profile.

Frozen prediction: no level-preserving query-cell isomorphism exists.  Thus
the previously proved policy-transport mechanism does not apply.

## Exact falsification test

At fixed costs `(a,b)=(4,11)`, solve the unseen target at `c=18` and `c=19`.
Compare its exact value, optimal root groups, and ordered child vectors against
P0's source signatures:

| `c` | source value | source optimal groups | source group-0 children |
| ---: | ---: | --- | --- |
| 18 | 37 | `[0]` | `[33,33,33]` |
| 19 | 38 | `[0]` | `[34,34,33]` |

The universal alphabet-permutation conjecture is falsified structurally even
if these two scalar values coincide.  A changed value or root-policy signature
is an additional executable counterexample showing that labelled zero has a
concrete planning consequence.

## Required evidence

- preserve all endpoint outputs, including accidental scalar agreement;
- independently replay root minima without importing THEORICA;
- verify the frozen color-refinement separation;
- deterministic replay, targeted lint, full regression, and exact-head hosted
  execution;
- do not reopen or replace the completed 18-case panel: this is a new
  out-of-orbit falsification experiment on the same kernel and branch.
