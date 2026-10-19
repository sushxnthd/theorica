# Frozen protocol: orbit-quotient ambiguity planning

## Active kernel

- **Precise question.** For a finite permutation action and a certified
  action-invariant convex ambiguity set, can robust query planning be reduced
  without loss from label space to point-orbit mass space, and can THEORICA
  synthesize an exact rational mixed plan that detects when randomization
  strictly improves every pure query orbit?
- **Best-known frontier.** Finite zero-sum minimax/linear programming,
  randomized decision rules, group averaging, and robust optimization are
  classical. The prior orbit-mixture result only handles the special target of
  uniform point inclusion when the ambiguity set contains the uniform prior.
- **Exact objective.** Prove the quotient reduction, implement an exact
  rational fail-closed planner, exhaust finite two- and three-orbit panels, and
  independently reproduce the two-orbit strict-gain boundary.
- **Strongest alternative explanation.** Any observed gain is merely generic
  matrix-game mixing and algebraic structure contributes no lossless
  compression or executable certificate.
- **Cheapest decisive falsification.** Find one certified invariant ambiguity
  instance where the quotient value differs from a full-label enumeration, or
  where the returned rational mixture fails its worst-case payoff certificate.
- **Mechanism-derived unseen prediction.** With point-orbit sizes `(3,4)`,
  `k=2`, query compositions `(2/3,0)` and `(0,1/2)`, and ambiguity orbit-mass
  vertices `(3/4,1/4)` and `(1/4,3/4)`, the unique equalizing mixture places
  weight `3/7` on the first query orbit and `4/7` on the second, attaining
  value `2/7`. The best pure value is `1/6`, so the exact gain is `5/42`.
- **Publishable threshold.** Exact theorem and proof, exhaustive rational
  verification, independent checker, primary-literature boundary audit, and a
  frozen prediction with no mismatch.
- **Project-consequence threshold.** THEORICA must gain a callable planner that
  accepts algebraic query orbits plus ambiguity vertices and either emits a
  seed-executable exact certificate or refuses.
- **Kill condition.** Any quotient/full-game mismatch, any certificate
  mismatch, or a priority audit showing the full specialization and planner
  already available unchanged.

## Frozen gates

1. The frozen `(3,4)` prediction above is not changed after implementation.
2. Primary enumeration uses exact `Fraction` arithmetic throughout.
3. The independent checker does not import production planner code.
4. The result must compare against the strongest pure-query-orbit baseline.
5. Historical novelty is not claimed for minimax, LP duality, group averaging,
   or mixed strategies.

## Holdout integrity

No unopened external challenge is used. The frozen witness is a prospective
algebraic prediction, and the remaining enumerated families are verification
cases rather than a fitted cohort.
