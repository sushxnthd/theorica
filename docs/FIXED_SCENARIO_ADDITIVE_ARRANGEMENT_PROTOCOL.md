# Frozen protocol: fixed-scenario additive arrangement law

## Precise question

Does the four-scenario product-free planner extend as an exact executable law
to arbitrary fixed scenario count `m`, or do higher-dimensional degeneracy and
policy recovery invalidate the arrangement certificate?

## Theorem target frozen before outcomes

For a finite robust game with certified additive payoff

\[
u(a,b)=\sum_t u_t(a_t,b),\qquad b\in\{1,\ldots,m\},
\]

nature's dual is

\[
D(q)=\sum_t\max_{a_t}\langle q,u_{t,a_t}\rangle,
\qquad q\in\Delta_m.
\]

Let `L` be the number of distinct component-local action-tie hyperplanes. The
target law is that an exact minimizer occurs among at most

\[
\binom{L+m}{m-1}
\]

intersections of `m-1` tie or simplex-facet boundaries. An exact primal policy
supported on at most `m` tied joint responses must attain the same value. Value
computation must not enumerate the Cartesian joint-action space.

## Frozen evaluation

1. Implement one generic rational planner for `2 <= m <= 8`; retain the
   specialized two/three/four-scenario interfaces as predecessor controls.
2. Exhaustively test the normalized five-scenario binary family with three
   two-action components, each having a zero baseline and an arbitrary binary
   contrast: `32^3 = 32,768` games.
3. Compare every case against an independently expanded joint-action solver.
4. Before opening outcomes, freeze 50 seeded mixed-shape five-scenario games,
   balanced between strict-randomization and pure-optimal outcomes when the
   generator supplies both.
5. Include a scaling witness with at least 15 components and at least
   `4^15 = 1,073,741,824` implicit joint actions.
6. Run an independent Fraction-only checker that imports no THEORICA code and
   reopens the exhaustive digest, all holdouts, the candidate bound, and the
   scaling certificate.

## Strongest alternatives and falsification

- **Cartesian enumeration explains correctness:** refuted only if the
  production value path never constructs joint actions and the scaling witness
  is executable.
- **Four dimensions were accidental:** refuted only by zero exact mismatches at
  five scenarios, including strict-randomization cases.
- **Degeneracy breaks sparse recovery:** refuted only if every returned policy
  has positive masses, support at most `m`, and realizes the exact dual value.
- **The bound is cosmetic:** refuted only if every observed candidate count is
  below the closed-form bound and an independently generated high-product
  witness is solved.

## Kill conditions

Kill or narrow the generic claim on any exact value mismatch, missing sparse
primal witness below the configured active-response cap, candidate-bound
violation, independent-check disagreement, or predecessor regression. Fail
closed on uncertified additivity, malformed dimensions, scenario counts above
the configured cap, excessive boundary combinations, or excessive tied joint
responses.

## Publishable and project consequence thresholds

The smallest supported result must include a proof, exact rational
implementation, exhaustive five-scenario evidence, prospective mixed-shape
holdouts, independent verification, adversarial nonadditivity boundary, and a
production API that replaces four separate scenario-specific value planners
with one bounded fixed-dimensional mechanism. Classical arrangement, minimax,
and sparse-support ingredients are not claimed as novel.
