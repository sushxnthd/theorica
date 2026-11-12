# Frozen protocol: tight rank-three nature-support law

## Question

For every certified additive robust game whose rational scenario payoff columns
have affine dimension exactly three, can THEORICA replace the planner's nature
distribution by an exact distribution on at most four original scenarios while
preserving every component-local action's expected payoff and the minimax
certificate?

## Frontier and proposed law

Caratheodory's theorem implies that a barycenter in three dimensions has a
representation on at most four points. The proposed executable law is sharper
than the current eight-vertex certificate: preserve the nature barycenter in
the exact rank-three quotient, lift the resulting weights to original scenario
indices, and independently replay every local action expectation. The bound
four should be tight on the four-by-four identity game.

## Frozen evaluation

- Seed: `20261027`.
- Opened cohort: 80 exact rational games with 4--8 hull vertices.
- Prospective holdout: 30 separately generated games, six each at 4, 5, 6, 7,
  and 8 vertices; holdout generation is frozen before production outcomes.
- Dense-certificate interventions: 40 synthetic optimal nature certificates on
  rank-three polytopes, intentionally supported on 5--8 vertices before exact
  compression.
- Tightness control: the four-action/four-scenario identity game must require
  nature support four.
- Boundary attacks: 40 affine-rank-four identity/perturbation games must not be
  assigned the rank-three bound.

## Strongest alternative explanation

The downstream linear-program solver already tends to return sparse basic
solutions. Therefore a small observed support is not evidence for the law. The
decisive intervention supplies dense optimal certificates and requires exact
barycenter and per-action expectation preservation after compression.

## Acceptance and kill conditions

Accept only if all opened and untouched holdout cases preserve total mass,
nonnegativity, rank-three barycenter, every local action expectation, dual
optimality, and support at most four; all dense interventions compress; the
identity witness proves support four is necessary; every rank-four attack
abstains; an independent Fraction-only checker agrees; and the full regression
suite passes.

Kill or reformulate on any false certificate, expectation mismatch, support
above four, false acceptance of rank four, failure of the tightness witness, or
dependence on floating arithmetic for acceptance.

## Project consequence

A surviving result changes THEORICA's rank-three plan from an eight-scenario
dual explanation to a provably tight four-scenario counterexample certificate,
without changing its executable policy or minimax value.
