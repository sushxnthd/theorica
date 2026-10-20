# Result: supported-crossing law for two-query robust games

## Smallest supported claim

For a finite robust game with exactly two query actions and any finite number
of ambiguity vertices, strict randomization occurs exactly at an interior
crossing on the lower envelope of the vertices' affine payoff lines where the
active slopes bracket zero and the crossing value exceeds both pure-action
values. An exact lower-envelope planner finds the optimum and a two-vertex
certificate in `O(m log m)` time for `m` ambiguity vertices.

This is an exact THEORICA reasoning capability, not a claim to have invented
finite-game minimax theory, linear-programming duality, or lower-envelope
geometry.

## Theorem

Let the two actions have payoffs `a_j,b_j` against ambiguity vertex `j`, and
write

`g_j(lambda) = b_j + lambda(a_j-b_j)`,

`f(lambda) = min_j g_j(lambda)` for `lambda in [0,1]`.

Let `p=max(f(0),f(1))`. Then `max f > p` if and only if there is an interior
`lambda*`, with `v=f(lambda*)`, such that:

1. at least two active lines attain `v` at `lambda*`;
2. all other lines are at least `v` there; and
3. the slopes of the active lines bracket zero.

When these conditions hold, `(lambda*,1-lambda*)` is maximin, and two active
vertices with slopes on opposite sides of zero form a complete optimality
certificate.

### Proof

Each `g_j` is affine, so their pointwise minimum `f` is concave and
piecewise-affine. If `lambda*` is an interior maximizer, the concave
first-order condition is that zero lies in the convex hull of the active
slopes. In one dimension this is exactly the slope-bracketing condition. If
the value is strictly larger than both endpoint values, the maximizer is
interior and at least two envelope pieces meet (a lone zero-slope piece can be
certified at either boundary crossing of its maximal plateau). Conversely, a
supported interior crossing whose active slopes bracket zero has nonnegative
left derivative and nonpositive right derivative, hence globally maximizes
the concave envelope. Requiring its value to exceed `p` is exactly strict
dominance over both pure actions.

Equal-slope lines reduce to the one with least intercept. Sorting the remaining
lines by slope and maintaining their monotone crossing stack constructs the
lower envelope in `O(m log m)` time; scanning its breakpoints and the two
endpoints is linear. All arithmetic in the implementation is rational.

## Frozen predictions and exact results

The protocol was committed before result generation.

| Gate | Frozen requirement | Result |
|---|---:|---:|
| `2 x 3` matrices over `{0,1,2}` | 729 | 729 checked |
| `2 x 4` matrices over `{0,1,2}` | 6,561 | 6,561 checked |
| Total exact games | 7,290 | 7,290 |
| Value/policy mismatches vs all intersections | 0 | 0 |
| Certificate mismatches | 0 | 0 |
| Independent-checker mismatches | 0 | 0 |
| Strict-randomization cases | not fit | 2,222 |
| Preserved strict `2 x 2` games after slack vertex | all | 14/14 |
| Full repository tests | pass | 120 passed |

The frozen slack witness
`((1/2,1/6,1),(1/8,3/8,1))` returns
`lambda=3/7`, value `2/7`, best pure value `1/6`, and supporting vertices
`(0,1)`. The frozen undercut witness, replacing the third column by zeros,
returns value zero and no strict randomized advantage. Thus an added ambiguity
vertex preserves the certificate exactly when it does not undercut the
certified crossing; this is the mechanism-derived unseen prediction.

The primary and independent implementations produced the same aggregate
counts and SHA-256 value digest
`801be2e311d0f66eb0149210eeebffdd6a31a88b71a316f04aacda98eb7e8f87`.

## Adversarial falsification

The checker compared the lower-envelope solver against exhaustive enumeration
of both endpoints and every pairwise line intersection. It independently
verified the realized worst-case value, pure boundary, strictness decision, and
support certificate. The audit script reimplements the enumeration without
importing the production solver. Equality plateaus are deliberately
canonicalized to a pure policy because they provide no strict advantage.

## Priority audit

The mathematical substrate is classical. Finite zero-sum games are linear
programs, and max-min strategies solve a linear program; von Stengel's 2023
primary treatment gives the modern precise relation and documents the gap in
the historical converse reduction. Adler's primary paper likewise repairs the
LP-to-game reduction. Computational-geometry work treats lower envelopes as a
standard algorithmic object. Accordingly, the defensible contribution here is
only the specialized exact planner, sparse certificate, integration into
THEORICA's orbit-ambiguity path, and frozen exhaustive validation.

Primary sources consulted:

- Bernhard von Stengel, *Zero-Sum Games and Linear Programming Duality*, 2023,
  https://arxiv.org/abs/2205.11196
- Ilan Adler, *The Equivalence of Linear Programs and Zero-Sum Games*, 2013,
  https://optimization-online.org/wp-content/uploads/2010/06/2659.pdf
- Pankaj K. Agarwal, Otfried Schwarzkopf, and Micha Sharir, *The Overlay of
  Lower Envelopes and its Applications*, 1996,
  https://users.cs.duke.edu/~pankaj/publications/papers/overlay.pdf

No located source in this audit supports novelty for the broad geometry.

## Direct project consequence

`synthesize_orbit_ambiguity_plan` now bypasses generic symbolic support
enumeration whenever the quotient has two query actions and more than two
ambiguity vertices. It returns an exact executable mixture plus either a
supported-crossing witness or a deterministic boundary certificate. The
previous `2 x 2` protected-pairing fast path remains unchanged.

## Limits

- The theorem applies to exactly two actions; three or more actions still use
  generic exact support enumeration.
- The ambiguity set must be represented by finitely many vertices.
- The exhaustive validation covers payoff entries `{0,1,2}` for three and four
  vertices, plus frozen rational witnesses; the proof, not the grid, carries
  the general claim.
- This result does not establish a new minimax theorem or a new general lower-
  envelope algorithm.
