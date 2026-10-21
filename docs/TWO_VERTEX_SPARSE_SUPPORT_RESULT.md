# Result: two-vertex sparse-support law

## Smallest supported claim

For any finite robust query game with exactly two ambiguity vertices, an
optimal plan uses at most two query actions. Strict randomization beats every
pure query exactly when a segment joining two action-payoff points on opposite
sides of the diagonal crosses `x=y` above the best pure worst-case payoff.
THEORICA now returns the exact rational mixture and a primal-dual saddle
certificate.

This is an executable specialization of classical finite minimax and linear
programming geometry, not a claim to a new general minimax theorem.

## Exact law

Represent action `i` by `p_i=(a_i,b_i)` and define

`p = max_i min(a_i,b_i)`, `d_i=a_i-b_i`.

For each pair with `d_i d_j < 0`, let

`lambda_ij = d_j/(d_j-d_i)`

and let `t_ij` be either coordinate of
`lambda_ij p_i + (1-lambda_ij) p_j`; the coordinates are equal by
construction. Then the robust value is

`V = max(p, max_{d_i d_j < 0} t_ij)`.

Hence strict randomization occurs if and only if the second term is strictly
larger than `p`. A maximizing pair and `lambda_ij` give a support-two primal
certificate. The implementation also returns an ambiguity mixture `q` such
that every action's expected payoff under `q` is at most `V`; together these
are a complete saddle certificate.

## Proof

A randomized action plan realizes a point in the convex hull of the action
payoff points, and its robust payoff is the smaller coordinate. If an optimum
strictly exceeds every pure worst-case payoff, neither coordinate can be the
sole active constraint: maximizing a single coordinate over a finite convex
hull is attained at a vertex and therefore cannot yield a strict mixed gain.
Thus a strict optimum lies on `x=y`.

The maximizing diagonal point lies on the boundary of the planar convex hull.
It is therefore on a vertex or an edge. A vertex is a pure action and cannot
produce strict gain, so a strict optimum lies on a segment between two action
points. Its endpoints must lie on opposite sides of the diagonal, and solving
the diagonal equation gives `lambda_ij` above. Conversely every such crossing
is a feasible mixed plan. Taking the largest crossing together with the best
pure value therefore gives exactly `V` and proves the support-two bound.

For optimality certification, minimize over `q in [0,1]` the convex upper
envelope `max_i(q a_i+(1-q)b_i)`. Its endpoints and pairwise breakpoints contain
an exact minimizer. Equality of this dual value with the primal value, plus the
reported inequalities, proves the saddle certificate by weak duality.

## Frozen exact evaluation

The protocol commit preceded result generation.

| Gate | Result |
|---|---:|
| `3 x 2` games over `{0,1,2}` | 729 |
| `4 x 2` games over `{0,1,2}` | 6,561 |
| Total exact games | 7,290 |
| Strict-randomization cases | 2,108 |
| Value/policy/dual mismatches | 0 |
| Support-bound mismatches | 0 |
| Certificate mismatches | 0 |
| Independent-checker mismatches | 0 |
| Repository tests | 123 passed |

Both implementations produced the SHA-256 digest
`8097edb597a5a0664f7c63eda1ac4b5e17335ef5cfb2d9df3d8ce0f81cab1c8d`.

The frozen witness `(0,2),(2,0),(0,0)` mixes the first two actions at
`(1/2,1/2)`, uses dual ambiguity weights `(1/2,1/2)`, and attains value `1`
versus pure value `0`. Adding dominated `(1/4,1/4)` leaves the policy and value
unchanged. Adding `(3/2,3/2)` changes the exact optimum to that pure action at
value `3/2`. At the equality boundary, adding `(1,1)` preserves value `1` but
canonicalizes to the new pure action, exactly as preregistered. All four
predictions passed.

## Preserved failed gate

The first independent audit agreed on every mathematical output but failed the
byte digest because it serialized a pure probability as integer `1`, whereas
the primary path serialized `Fraction(1,1)`. Canonicalizing the independent
record to `Fraction(1)` restored byte-identical digests. No solver logic,
protocol, or primary artifact changed. The original failure is preserved in
`results/two_vertex_sparse_support/failed_gate.txt`.

## Priority audit

Finite zero-sum minimax, primal-dual linear programming, convex-hull support
arguments, and small-support equilibria are classical. Bernhard von Stengel's
modern treatment makes the finite-game/LP duality precise; Caratheodory-type
convex-hull support bounds are also standard. The defensible contribution is
limited to the closed-form diagonal-crossing criterion, exact canonical
primal-dual certificate, exhaustive independent evaluation, and its integration
as a fail-closed THEORICA planner.

Primary reference:

- Bernhard von Stengel, *Zero-Sum Games and Linear Programming Duality*,
  Mathematics of Operations Research 49(2), 2024,
  https://doi.org/10.1287/moor.2022.0149

## Direct project consequence

`synthesize_orbit_ambiguity_plan` now invokes the sparse-support fast path for
any quotient with exactly two ambiguity vertices, regardless of the number of
query actions. Generic symbolic support enumeration is bypassed, the returned
executable mixture uses at most two actions, and a certificate failure aborts
the route.

## Limits

- Exactly two finite ambiguity vertices are required.
- The implementation is `O(n^2)` in the number of actions; no asymptotic
  novelty is claimed.
- The exhaustive grid validates three- and four-action games; the proof carries
  the arbitrary finite-action statement.
- This does not solve games with three or more ambiguity vertices, where larger
  supports may be necessary.
