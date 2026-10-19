# Frozen protocol: sparse orbit-mixture repair law

Date frozen: 2026-10-19
Branch: `breakthrough-engine/orbit-mixture-repair-20261019`

## Active kernel

**Precise question.** Let a finite permutation group G act on a finite label set X with point-orbits O_1,...,O_r. Let A be a nonempty G-closed family of admissible k-subset queries. When can a G-invariant randomized plan supported on A attain the universal minimax coverage value k/|X| even though no single query orbit is orbit-balanced?

**Frontier.** Group averaging, invariant designs, orbit polytopes, and Caratheodory sparsification are classical. The preceding THEORICA result established the exact criterion for one query orbit. This run tests the multi-orbit repair boundary and implements an exact fail-closed planner. No broad historical novelty is presumed.

**Exact objective.** Prove or refute:
1. every G-invariant plan is a mixture of uniform plans on query orbits;
2. its per-point inclusion vector is the corresponding convex combination of normalized orbit-composition vectors;
3. the universal k/n guarantee is attainable iff u=(k/n,...,k/n) lies in their convex hull;
4. whenever attainable, a plan using at most d+1 <= r query orbits exists, where d is the affine dimension of the accessible composition vectors.

**Strongest alternative explanation.** The result may be only a direct repackaging of classical invariant-design and convex-hull facts, without a material reasoning capability beyond uniform sampling from all k-subsets.

**Cheapest decisive falsification.** Exhaustively enumerate small finite actions, admissible unions of query orbits, and exact rational mixtures. Any mismatch between the convex-hull certificate and the true linear feasibility result, any support-bound violation, or any synthesized plan whose point inclusions are not exactly k/n kills the theorem/implementation.

**Mechanism-derived unseen prediction.** In intransitive actions whose point-orbit sizes make a single balanced seed arithmetically impossible, two or more individually suboptimal query orbits can still repair one another exactly when their composition vectors bracket u. A concrete frozen witness family uses two point-orbits of sizes 3 and 4 with k=2: mixing query types (1,1) and (0,2) with weights 6/7 and 1/7 should attain exact inclusion 2/7 on every point although neither component does.

**Publishable threshold.** Exact theorem and proof; exhaustive finite verification; independent checker; explicit minimal repair witnesses and impossibility cases; primary-literature boundary; deterministic reproduction.

**Project-consequence threshold.** THEORICA must gain an executable exact-rational synthesizer that either returns a sparse invariant minimax plan with a verifiable certificate or refuses infeasible admissible families. It must strictly extend the single-orbit planner.

**Kill condition.** Kill or reformulate if exact enumeration finds a counterexample, if sparse synthesis is not independently reproducible, or if the result cannot change THEORICA's query-planning capability.

## Holdout and provenance

No previously frozen empirical holdout is opened. Enumeration families, witness, solver logic, and acceptance gates are fixed before implementation and execution. Failures will remain on this branch.
