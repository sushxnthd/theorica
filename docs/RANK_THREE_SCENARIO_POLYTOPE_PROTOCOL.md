# Rank-three scenario polytope quotient protocol

Status: frozen before implementation and before holdout generation  
Kernel branch: `breakthrough-engine/additive-product-minimax-law-20261021`

## Precise question

For a certified additive robust game whose scenario payoff columns have exact rational affine dimension three, can THEORICA delete every non-vertex scenario, solve only the resulting 3D polytope vertices, and lift an exact executable minimax certificate without expanding Cartesian joint actions?

## Frontier and smallest plausible law

For any mixed policy, payoff is affine in the scenario column. Therefore its minimum over a finite scenario set equals its minimum over the vertices of that set's convex hull. Convex-hull reduction is classical; the project contribution under test is an exact rational rank/polytope router, fail-closed boundary, lifted nature certificate, and prospective product-free validation integrated with THEORICA.

## Objective

Implement an exact `synthesize_rank_three_scenario_polytope_plan` that:

1. proves affine dimension exactly three from rational payoff columns;
2. projects every scenario to exact rational 3D coordinates;
3. classifies vertices using exact Carathéodory membership certificates, never floating geometry;
4. rejects rank below/above three before planning;
5. rejects more than eight surviving vertices before the downstream planner;
6. invokes the fixed-scenario additive planner only on surviving vertices;
7. lifts nature probabilities and replays the returned policy against every original scenario.

## Frozen evaluation

Opened families: at least 80 exact games spanning four through eight polytope vertices, both pure-optimal and strict-randomization regimes.

Prospective holdouts, seed 20261026: ambient scenario counts 9, 12, 16, 20 and 24, with surviving vertex counts 4, 5, 6, 7 and 8. Generate holdouts only after implementation is frozen.

Adversarial gates:

- 50 exact rank-four inputs must abstain before planning;
- 20 nine-vertex rank-three inputs must exceed the certified cap;
- duplicate columns and lower-rank inputs must not be misclassified;
- a coordinate-extrema baseline must be falsified by a fixed witness where it deletes a non-axis-extreme vertex and changes the minimax value.

Scaling witness: 20 binary components, at least 20 ambient scenarios and eight surviving vertices; exact certificate without enumerating the implicit (2^{20}) joint actions.

## Independent check

A Fraction-only checker must independently reconstruct affine rank, test convex membership by subsets of at most four points, expand only the reduced holdout games, verify values/classification/lifted payoffs, and avoid importing the production planner.

## Publishable threshold

- zero mismatches on opened and untouched holdout cases;
- zero rank-four or over-cap false accepts;
- coordinate-extrema baseline decisively wrong on the frozen witness;
- exact policy support at most the number of surviving vertices;
- full regression and hosted reproduction green;
- explicit novelty limit: not a new convex-hull or minimax theorem.

## Project consequence threshold

THEORICA routes certified rank-three scenario families with many redundant scenarios into the existing product-free fixed-scenario planner, while refusing unsupported rank or excessive hull complexity.

## Kill condition

Kill or reformulate if exact membership becomes impractical at the frozen sizes, any non-vertex deletion changes value, lifted replay fails, any rank-four case is accepted, or the prospective holdouts reveal a mismatch.
