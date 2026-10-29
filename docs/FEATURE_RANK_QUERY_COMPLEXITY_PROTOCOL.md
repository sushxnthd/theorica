# Frozen protocol: feature-rank scenario query complexity

## Question

Let every scenario carry a known rational feature row `phi_s in Q^p`, with
exact row rank `r`.  Suppose an external certificate states that every
component-local action payoff is a linear functional of `phi_s`.  Can
THEORICA recover the complete robust game with exactly `r` scenario-oracle
queries, even when `p > r`, and is `r` worst-case necessary?

This strictly generalizes the affine-coordinate kernel: affine payoffs use
feature rows `(1,z_s)` and therefore have rank `d + 1`.  It also covers
certified polynomial, mechanistic-basis, and redundant-feature families.

## Proposed law

Choose the lexicographically first `r` linearly independent feature rows and
an exact set of `r` pivot columns.  Query every local payoff on only those
scenarios.  Express every remaining feature row as an exact rational linear
combination of the queried rows, then apply the same combination to each
queried payoff.  The query count is the feature-row rank, not the scenario
count or the raw feature width.

For necessity, run an arbitrary deterministic algorithm for fewer than `r`
queries against the zero oracle.  The queried feature rows do not span the
full row space, so a nonzero linear payoff functional vanishes on the entire
transcript but not on at least one unqueried scenario.  Choose its sign so its
robust value is negative.  The zero and nonzero games are transcript-
indistinguishable but have different robust values.

## Frozen evidence

- At least 160 opened exact families over feature ranks 2--4 and 9--48
  scenarios, including affine, quadratic, cubic, and redundant-column maps.
- 40 prospective holdouts at 53, 79, 113, 167, and 257 scenarios.
- At least 80 adaptive lower-bound witnesses with fewer than `r` queries.
- Every reconstructed payoff must match the untouched generated table exactly.
- For ranks 2--4, full-table and reconstructed-table robust plans must match in
  value, policy, randomization classification, and certificate state.
- A one-dimensional cubic family must demonstrate four-query recovery where
  the earlier affine-coordinate certificate is invalid.
- Adding linearly redundant feature columns must not increase query count.
- An independent standard-library checker must reproduce reconstruction,
  feature ranks, query traces, lower-bound witnesses, and the evidence digest
  without importing production code.

## Strongest alternatives

1. Raw feature width, rather than row rank, determines query complexity.
2. Nonlinear features break exact downstream robust planning.
3. Robust value requires fewer queries than complete payoff reconstruction.
4. Agreement is explained by pure optima or duplicate scenarios.

The sweep therefore includes redundant columns, polynomial features, distinct
scenario rows, nontrivial coefficients, and strict-randomization cases.  The
indistinguishability construction attacks the third alternative directly.

## Product consequence

THEORICA may acquire a certified structured robust game using one oracle call
per independent feature direction, then invoke the existing exact rank router.
Missing certification, zero rank, inconsistent oracle shapes, or failure of an
exact row-span certificate must abort before downstream planning.

## Kill conditions

Kill or reformulate on any unqueried oracle call, reconstruction mismatch,
rank or pivot error, robust-plan mismatch, lower-bound transcript mismatch,
or false acceptance of uncertified/malformed input.

## Claim boundary

A pass supports exact rational feature rows and externally certified linearity
of local payoffs in those features.  It does not infer the feature map, certify
linearity from queried observations, tolerate noise, or guarantee that a
reconstructed game lies within the current downstream rank/hull caps.
