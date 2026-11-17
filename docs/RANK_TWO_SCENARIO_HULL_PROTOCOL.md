# Frozen protocol: affine-rank-two scenario hull quotient

## Precise question

When a certified additive robust game has many ambiguity scenarios but its scenario payoff columns have affine dimension exactly two, can THEORICA replace all non-extreme scenario columns by the exact rational convex hull, then recover the minimax policy without Cartesian joint-action enumeration?

## Proposed structural boundary

Flatten every component-local action payoff profile into a rational matrix with scenarios as columns. After subtracting one scenario column, require exact column rank two. Choose an injective two-row projection of that difference space and compute the exact planar convex hull of the projected scenario columns.

Every deleted scenario column is then a convex combination of retained extreme columns. Consequently, under every agent mixture its expected payoff is a convex combination of extreme-scenario payoffs and cannot be below their minimum. The full game and hull game should therefore have identical minimax value and strict-randomization classification.

The production route is authorized only when the exact hull contains at most eight distinct extreme columns, matching the certified fixed-scenario planner boundary. Larger hulls must fail closed before planning.

## Frozen predictions

1. Exact value, strict-randomization classification, and executable policy match an independently expanded exact solver on every opened family.
2. Deleting interior and duplicate scenarios never changes the value.
3. The lifted nature distribution is supported only on original extreme scenarios; the returned agent policy replays to the certified value across every original scenario.
4. Prospective holdouts with 11, 17, 29, 47, and 80 ambient scenarios, but 3--8 hull vertices, pass exactly.
5. Rank-three inputs and rank-two inputs with nine or more hull vertices are rejected before calling the fixed-scenario planner.
6. An uncertified coordinate-extrema heuristic is falsified by a rank-two witness whose worst scenario is not a coordinate extreme.

## Frozen evaluation

- Opened rational families with 9--40 ambient scenarios and 3--8 exact hull vertices, including duplicate columns, strict interior columns, positive/negative/zero local slopes, strict-randomization cases, and pure-optimal cases.
- Strong baseline: independently expanded Cartesian joint actions plus exact rational arrangement enumeration on the retained hull.
- Prospective seed: 20261025. Holdout ambient sizes: 11, 17, 29, 47, and 80. Holdout hull sizes: 3, 4, 5, 6, and 8.
- Falsification: rank-three mutations, nine-vertex parabolic hulls, and a coordinate-extrema deletion counterexample.
- Scaling witness: at least 20 components, at least 64 ambient scenarios, and at most eight hull vertices.
- Independent checker imports no THEORICA production code and regenerates the frozen families and exact values.

## Exact objective

Zero value, classification, hull, certificate, lifted-nature, or realized-payoff mismatches; zero false accepts on rank-three and over-cap inputs; exact replay on all original scenarios; no Cartesian expansion in production.

## Strongest alternative explanation

Success could come from duplicate columns, dominated actions, or accidentally one-dimensional geometry. The sweep therefore requires exact affine rank two, distinct strict-interior columns, opposing action slopes, and mixed optima. The coordinate-extrema attack tests whether arbitrary low-dimensional projection alone is insufficient without full hull retention.

## Product consequence

On a valid certificate with at most eight hull vertices, THEORICA may route an arbitrary-scenario additive game to the fixed-scenario product-free planner. On rank mismatch or excess hull size it must abstain without invoking that planner.

## Kill condition

Kill or reformulate on any false acceptance, any mismatch with the expanded exact game, any deleted scenario below the certified value, any non-extreme retained/deleted error, or any planner call after a rank/cap failure.

## Smallest publishable claim

A positive result supports only an exact product-free convex-hull quotient for certified additive games with rational affine scenario rank two and at most eight extreme scenario columns. It does not solve general low-rank games, approximate rank, nonadditive payoffs, or rank-two games with unbounded hull size.
