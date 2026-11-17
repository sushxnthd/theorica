# Frozen protocol: explicit outside-prefix sentinel covariance

UTC date: 2026-11-11

## Experiment change

The prior experiment falsified universal alphabet covariance because response value `0`
represented both an observed symbol zero and a completion outside the active
prefix. This experiment changes the query encoding, not the family panel: it
uses a distinguished outside-prefix response `-1`, while observed symbols
remain `0,1,2`.

## Source, unseen image, and costs

Source P0:
`000,001,010,011,100,101,110,111,200,210`.

Unseen target under the all-coordinate alphabet involution `0 <-> 1`:
`111,110,101,100,011,010,001,000,211,201`.

The frozen witness state, substitution/erasure budgets, query multiplicities,
and level costs remain unchanged. Exact endpoints are `(a,b,c)=(4,11,18)`
and `(4,11,19)`.

## Predictions frozen before endpoint enumeration

1. With outside response `-1` fixed separately from the alphabet, the
   coordinatewise `0 <-> 1` action induces a level-preserving query-cell
   incidence isomorphism.
2. The transported completion/query/cell map passes exhaustive edge checks.
3. Source and target exact values coincide at 37 for `c=18` and 38 for
   `c=19`.
4. Root group 0 is uniquely optimal at both endpoints. Ordered root child
   values are `[33,33,33]` at `c=18` and `[34,34,33]` at `c=19`.
5. Exact search counts and compatibility-state counts match source versus
   target at each endpoint, because the labelled games are conjugate.
6. An independent audit with zero production imports will validate the
   structural map and replay all four root minima.

## Falsifiers

Any absent/invalid incidence isomorphism, endpoint mismatch, non-unique root,
ordered-child mismatch after the declared response permutation, or unequal
exact-search counts falsifies the restored-covariance claim.

## Claim boundary

A pass establishes covariance for this finite prefix-query game after the
outside-prefix response is made explicit. It does not establish the necessity
or minimality of the encoding, arbitrary query families, arbitrary states, or
all cost vectors.
