# Affine-rank-two scenario hull quotient: exact result

## Smallest supported claim

For a finite robust game with certified component-additive payoff, if its
scenario payoff columns have exact rational affine dimension two, every
non-extreme scenario column can be deleted without changing the minimax game.
When the remaining planar convex hull has at most eight vertices, THEORICA now
computes an exact executable policy through the existing product-free
fixed-scenario planner, lifts nature's distribution to the original scenarios,
and replays the certificate on every original column.

Rank below or above two and hulls with more than eight vertices fail closed
before the downstream planner is called.

## Theorem and proof

Flatten all component-local action payoffs into a matrix whose scenario columns
are `u_j`. Suppose `affdim{u_j}=2`. An exact injective two-coordinate projection
of the difference space preserves convex combinations and extremality. Let `H`
be the original scenario indices whose projected columns are vertices of the
planar convex hull.

For every deleted index `j`, there are nonnegative coefficients `lambda_h`
summing to one such that

`u_j = sum_(h in H) lambda_h u_h`.

For any randomized agent policy `p`, linearity gives

`p·u_j = sum_(h in H) lambda_h (p·u_h) >= min_(h in H) p·u_h`.

Thus deleting `j` cannot lower the policy's worst payoff. Since retained
columns are a subset of the original columns, the reverse inequality is
immediate, proving equality of the robust values and optimal-policy sets. The
additive decomposition is unchanged on `H`, so the fixed-scenario planner
recovers the value and policy without enumerating Cartesian joint actions.

## Frozen evidence

| Gate | Result |
|---|---:|
| Opened exact rational families | 121/121 |
| Opened strict-randomization cases | 15 |
| Prospective holdouts | 25/25 |
| Holdout ambient scenarios | 11, 17, 29, 47, 80 |
| Holdout hull vertices | 3, 4, 5, 6, 8 |
| Rank-three attacks rejected | 50/50 |
| Nine-vertex over-cap attacks rejected | 20/20 |
| Independent audit | 9/9 checks |

The strongest cheap heuristic—retain only coordinate minima and maxima—is
false. On the parabolic five-scenario witness with action profiles `x^2+2x`
and `x`, coordinate extrema retain scenarios `x=-2,0,2` and claim value `0`.
The omitted hull vertex `x=-1` lowers the exact value to `-1`. Full convex-hull
retention returns `-1`.

The scaling witness contains 20 components, two actions per component, and 80
ambient scenarios. Its eight-vertex hull preserves the exact game while the
implicit Cartesian action space contains `2^20 = 1,048,576` joint actions.

Reproduce with:

```bash
python scripts/verify_rank_two_scenario_hull.py
python scripts/audit_rank_two_scenario_hull.py
pytest -q tests/test_robust_provenance.py
```

## Novelty and priority audit

Extreme-point reasoning for convex uncertainty sets is classical, and scenario
reduction is a substantial established literature. For example,
[Buchheim and Kurtz](https://optimization-online.org/wp-content/uploads/2017/09/6199.pdf)
survey convex and discrete uncertainty in robust combinatorial optimization,
while [Goerigk and Kurtz](https://arxiv.org/abs/2209.00499) study optimal
scenario reduction with robust-performance guarantees.

This is therefore not claimed as a new convex-hull theorem. The bounded
contribution is an executable THEORICA law connecting exact affine-rank
detection, rational planar hull recovery, certified additive planning,
original-scenario replay, prospective many-scenario validation, and explicit
rank/cap abstention. Publication priority for that combined software theorem
still requires external expert review.

## Limitations

- Inputs and rank decisions are exact rational, not approximate or statistical.
- Affine rank must equal two; rank one uses the separate endpoint theorem.
- More than eight hull vertices currently exceed the downstream certified cap.
- Payoff additivity must be independently certified.
- The holdouts are generated algebraic families, not external domain data.

## Product consequence

An arbitrary number of raw ambiguity scenarios no longer determines planner
feasibility. THEORICA can first measure exact payoff geometry, retain only the
extreme rank-two columns, and route any hull of size at most eight into the
product-free planner. It abstains before planning on every unsupported case.
