# Frozen protocol: corruption-resilient feature queries

## Kernel

Given a known rational scenario-feature matrix of row rank `r`, certified
feature-span payoffs, and a scenario oracle that may return adversarially wrong
answers on at most `t` queried scenarios, characterize exactly when THEORICA can
recover the complete payoff table and robust plan.

## Proposed law

For a queried row set `Q`, let

`C_Q = {Phi_Q beta : beta in Q^p}`.

Exact recovery from every pattern of at most `t` corrupted query responses is
possible if and only if the minimum Hamming weight of a nonzero vector in
`C_Q` is at least `2t + 1`. Equivalently, after deleting any `2t` queried rows,
the remaining feature rows still have rank `r`.

The minimum query count is therefore the smallest size of a subset satisfying
that distance condition. For distinct-point Vandermonde feature rows of rank
`r`, the predicted optimum is exactly `r + 2t`.

## Strongest alternatives

1. The uncorrected rank-`r` selector is sufficient because exact interpolation
   detects bad answers. It cannot: `r` arbitrary values define a unique span
   element and provide no residual check.
2. Repeat every basis query `2t + 1` times and take a majority. This costs
   `r(2t + 1)` calls and assumes repeatable corruption semantics. The proposed
   code-distance selector uses distinct scenarios and should need `r + 2t` on
   MDS/Vandermonde families.
3. `r + 2t` always suffices. This should fail for degenerate scenario geometry;
   the exact distance test must abstain rather than infer an MDS promise.

## Frozen experiment

- Opened sweep: ranks 2--4, `t` in 1--2, distinct rational Vandermonde points,
  at least 120 generated additive games.
- Prospective holdout: 30 untouched seeds with 17--97 scenarios and corruption
  positions/values derived only after the query selector is frozen.
- Inject every corruption pattern up to `t` for small boundary families and a
  deterministic adversarial sample for larger families.
- Compare reconstructed payoff tables and downstream robust plans against the
  untouched full-table baseline.
- Compare query counts against repetition-majority and the uncorrected rank
  selector.
- Generate degenerate feature families where `r + 2t` rows do not achieve the
  required distance; production must find a larger certified subset or abstain
  within the frozen cap.
- Independent checker must use only the standard library and must not import
  production code.

## Lower bound and falsification

For any queried code with distance at most `2t`, persist two feature-span payoff
vectors and two corruption patterns of weight at most `t` that yield the same
observed transcript but different complete payoff tables (and, where possible,
different robust values). This is the decisive impossibility witness.

## Pass threshold

- zero reconstruction or policy mismatches;
- zero unqueried-oracle accesses;
- exact `r + 2t` calls on every Vandermonde case;
- strict saving over repetition-majority whenever `r > 1` and `t > 0`;
- all distance-failing geometries reject or use a larger certified subset;
- at least 60 indistinguishable-transcript lower-bound witnesses;
- full regression and touched-file lint pass.

## Kill condition

Kill or reformulate if the diagnostic cannot be computed before outcomes, any
accepted corruption pattern reconstructs incorrectly, the prospective holdout
fails, or the result reduces to syntax without changing the robust-planning
execution path.

## Smallest possible claim

The result, if it passes, will be an exact executable query-selection and
decoding law under an externally certified feature map and a hard bound on
adversarial query corruptions. It will not cover unknown features, stochastic
noise, approximate span membership, adaptive adversaries exceeding `t`, or
unsupported downstream planning complexity.
