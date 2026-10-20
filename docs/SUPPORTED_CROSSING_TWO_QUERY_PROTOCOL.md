# Frozen protocol: supported-crossing law for two-query robust games

Frozen before generating the exhaustive result.

## Active kernel

- **Question.** For two admissible queries and an arbitrary finite ambiguity
  polytope, exactly when does randomization strictly dominate both pure queries?
- **Frontier.** The current `2 x 2` protected-pairing fast path is exact, but
  additional ambiguity vertices fall back to generic support enumeration.
- **Objective.** Derive a necessary-and-sufficient structural certificate,
  implement an exact-rational planner, and validate it against independent
  all-intersection enumeration on unseen `2 x 3` and `2 x 4` families.
- **Strongest alternative.** The two-vertex protected pair may cease to certify
  optimality once a third vertex undercuts its crossing; no local pair law may
  survive arbitrary extra vertices.
- **Cheapest decisive falsification.** Exhaust all matrices over `{0, 1, 2}` for
  `2 x 3` and `2 x 4`. Any value, policy, strict-advantage, or certificate
  mismatch kills the kernel.
- **Mechanism-derived prediction.** A crossing pair remains optimal exactly when
  every other ambiguity line lies at or above its crossing and the active
  slopes bracket zero. Adding any vertex whose payoff at the certified mixture
  is at least the certified value preserves the value and policy.
- **Publishable threshold.** Exact proof, rational implementation, exhaustive
  enumeration, independent checker, frozen unseen examples, reproducibility,
  and a priority audit. Classical finite-game geometry is not novelty.
- **Project-consequence threshold.** Replace generic exact support enumeration
  whenever the quotient game has two query actions, returning either a sparse
  supported-crossing witness or a pure-policy certificate.
- **Kill condition.** Any exhaustive mismatch, unsupported claimed optimum, or
  failure of the slack-vertex preservation prediction kills the kernel.

## Proposed theorem

For payoff rows `(a_j)` and `(b_j)`, let

`g_j(lambda) = b_j + lambda * (a_j - b_j)`

and `f(lambda) = min_j g_j(lambda)` on `[0,1]`. The best pure value is
`p = max(f(0), f(1))`.

Strict randomization is optimal if and only if there is a pair of ambiguity
vertices `j,k` with an interior intersection `lambda*`, common value `v`, and:

1. `g_l(lambda*) >= v` for every vertex `l` (supported crossing);
2. the slopes active at `lambda*` bracket zero;
3. `v > p`.

The policy is `(lambda*, 1-lambda*)`. Necessity follows because the lower
envelope `f` is concave and every interior maximizer has zero in the convex
hull of its active slopes. Sufficiency follows from the same subgradient
condition. The lower envelope can be built exactly after sorting slopes, so the
planner is `O(m log m)` for `m` ambiguity vertices and returns a two-vertex
certificate even when the ambiguity set has many vertices.

## Frozen tests

- Exhaustive `2 x 3`: `3^6 = 729` matrices.
- Exhaustive `2 x 4`: `3^8 = 6,561` matrices.
- Total: 7,290 exact games.
- Required mismatches: zero for value, policy value, strict advantage, and
  supported-crossing validity.
- Frozen strict witness extends the prior matrix with a slack vertex:
  `((1/2, 1/6, 1), (1/8, 3/8, 1))`; prediction is probability `3/7`, value
  `2/7`, pure value `1/6`, and active vertices `(0,1)`.
- Frozen boundary witness adds an undercutting vertex:
  `((1/2, 1/6, 0), (1/8, 3/8, 0))`; prediction is no strict randomized
  advantage and value `0`.
- Duplicate executions must be byte-identical, and an independent implementation
  must reproduce the aggregate counts and digest.

## Priority boundary

This is a specialization of classical finite zero-sum games, lower-envelope
geometry, linear programming, and minimax theory. The intended defensible claim
is the exact THEORICA fast path and supported-crossing certificate, not invention
of those foundations.
