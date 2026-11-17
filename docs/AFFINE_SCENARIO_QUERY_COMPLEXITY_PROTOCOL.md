# Frozen protocol: optimal affine-scenario query complexity

## Question

Suppose every ambiguity scenario has a known rational descriptor
`z_s in Q^d`, the descriptors affinely span dimension `d`, and an external
certificate guarantees that every component-local action payoff is affine in
`z_s`.  Can THEORICA reconstruct the complete robust game using exactly
`d + 1` scenario-oracle calls, then invoke its existing exact product-free
planner without querying the other scenarios?  Is `d + 1` worst-case
necessary?

## Frontier and proposed law

Affine interpolation from `d + 1` independent samples is classical.  The
project claim under test is narrower and executable: a deterministic exact
query selector, rational reconstruction of every local payoff, downstream
robust-plan replay on all scenarios, and a matching adaptive-query lower-bound
witness integrated with THEORICA's fail-closed planner.

For descriptor dimension `d`, select the lexicographically first affinely
independent `d + 1` scenarios.  Query all component-local action payoffs at
only those scenarios.  Solve the exact rational affine interpolation system
for every action and reconstruct every unqueried column.

Sufficiency predicts `d + 1` queries independent of scenario count.  For
necessity, run any deterministic algorithm for at most `d` queries against an
all-zero oracle.  Its queried descriptors lie in a proper affine subspace, so
a nonzero affine function vanishes on the entire transcript.  Choosing its
sign creates an indistinguishable second game whose robust value is negative,
while the zero game's value is zero.

## Frozen evidence

- Opened families: at least 120 exact additive games across dimensions 1, 2,
  and 3, with 9--40 scenarios and 2--5 components.
- Prospective holdouts: 30 deterministic unseen families at scenario counts
  41, 64, 97, 127, and 193.  Freeze seeds and digests before opening.
- Every reconstructed payoff must equal the generator's untouched payoff
  table entry-for-entry.
- Every reconstructed robust plan must match the corresponding full-table
  rank router in value, classification, policy replay, and certificate state.
- At least 60 lower-bound attacks must produce identical transcripts for
  `d` queries but unequal exact robust values.
- Query count must be exactly `d + 1`, with zero oracle access to holdout
  scenarios.
- An independent checker must use only the standard library and must not
  import production code.

## Strongest alternatives

1. The saving is only interpolation folklore and does not survive exact robust
   planning or policy replay.
2. A heuristic set of coordinate extrema is enough, making affine-basis
   selection unnecessary.
3. `d` adaptive queries suffice because the minimax value needs less
   information than the full payoff table.
4. Accidental low rank, duplicate scenarios, or pure optima explain agreement.

Families must therefore have exact descriptor span `d`, nontrivial slopes,
distinct scenarios, and both pure and strict-randomization cases.  The
lower-bound construction attacks the third alternative directly.

## Product consequence

On a valid external affine-payoff certificate, THEORICA may query a scenario
oracle only `d + 1` times, reconstruct the full local game exactly, and route
it through the existing rank-one, rank-two, or rank-three planner.  Missing
certification, malformed shapes, non-spanning descriptors, or dimensions above
three must fail before querying.

## Kill conditions

Kill or reformulate on any unqueried oracle call, reconstruction mismatch,
full-table planning mismatch, false certificate, lower-bound transcript
disagreement, or any accepted unsupported input.

## Claim boundary

A pass supports exact rational descriptors, an externally justified affine
payoff certificate, descriptor dimension at most three, additive payoffs, and
the existing downstream hull-size caps.  It does not certify affinity from
`d + 1` observations, tolerate noise, cover approximate low rank, or improve
worst-case query complexity without known descriptors.
