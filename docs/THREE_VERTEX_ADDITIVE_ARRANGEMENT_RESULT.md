# Three-vertex additive arrangement law

## Smallest supported claim

For a finite zero-sum robust game with additive component payoffs and exactly
three ambiguity vertices, THEORICA computes the exact minimax value from a
two-dimensional arrangement of component-local action-tie lines.  It does not
enumerate the Cartesian joint-action space to compute the value.  It also
returns an executable optimal policy with support at most three, subject to an
explicit fail-closed cap on the tied active joint-action set.

## Theorem

For component `t`, action `a`, and payoff triple `u[t,a]`, let nature choose
`lambda = (x,y,1-x-y)` in the probability triangle.  Define

`g(lambda) = sum_t max_a <lambda,u[t,a]>`.

The minimax value is `min_lambda g(lambda)`.  Let `H` contain every equality
line between a pair of actions in the same component and let

`L = sum_t binom(|A_t|,2)`.

The minimum is attained at a triangle vertex, an intersection of a line in
`H` with a triangle edge, or an intersection of two lines in `H`.  Thus at
most

`3 + 3L + binom(L,2)`

exact rational candidates suffice before duplicate and out-of-triangle points
are removed.  This is polynomial in the additive description for the fixed
three-vertex ambiguity dimension, independent of `product_t |A_t|`.

At a minimizing `lambda`, complementary slackness restricts the row player to
joint responses formed from component actions tied at `lambda`.  Finite
minimax duality gives a feasible mixture over those responses.  A basic
feasible solution to the three payoff constraints uses at most three joint
responses.  A deterministic optimum exists exactly when one tied response
guarantees the value at all three vertices; otherwise randomization is
necessary.

## Proof sketch

Each component maximum is convex piecewise affine.  Their sum is affine on
every cell of the common line arrangement.  A linear function on a polygonal
cell reaches its minimum at a cell vertex, which is one of the enumerated
candidates.  Minimax duality identifies this dual minimum with the robust-game
value.  The support bound follows by taking a basic feasible optimal row
strategy in a game with three columns.  THEORICA verifies the returned policy
directly in exact arithmetic against all three scenario payoffs.

## Frozen evidence

| Gate | Result |
|---|---:|
| Exhaustive opened family | 531,441 / 531,441 exact |
| Value mismatches | 0 |
| Pure/randomized-boundary mismatches | 0 |
| Strict-randomization cases | 150,084 |
| Pure-optimal cases | 381,357 |
| Frozen mixed-dimension holdouts | 36 / 36 exact |
| Holdout split | 18 strict, 18 pure |
| Maximum returned support | 3 |
| Independent checks | 8 / 8 |

The 18-component scaling witness has four actions per component.  Cartesian
expansion would create `4^18 = 68,719,476,736` joint actions.  The exact
arrangement realized 12 distinct tie lines and only 22 feasible candidates;
the returned policy used support two.

## Strong controls and falsification

The strongest matched control is an independently expanded three-column game
solved by its own exact rational arrangement.  The checker separately compares
the component-local arrangement value with the expanded global arrangement on
all 531,441 opened cases.  It imports no THEORICA production code.  Every
returned production policy is also evaluated directly at all three vertices.

The preregistered kill conditions were any exact value mismatch, any incorrect
pure-versus-randomized decision, any policy below the claimed value, or support
above three.  None occurred.

## Novelty and priority boundary

The underlying ingredients are classical: finite minimax and the equivalence
between matrix games and linear programming; hyperplane arrangements in fixed
dimension; and finite-support results for separable games.  In particular,
Edelsbrunner, O'Rourke, and Seidel give optimal fixed-dimensional hyperplane
arrangement construction (`SIAM J. Comput.`, DOI 10.1137/0215024), and Stein,
Ozdaglar, and Parrilo study finite-support equilibria in separable games
(`arXiv:0707.3462`).

Accordingly, this result does **not** claim a new minimax theorem, a new
arrangement bound, or a new support theorem.  The defensible contribution is
their exact compositional specialization into a product-free robust planner,
the sharp deterministic/randomized decision, exhaustive rational validation,
and a fail-closed implementation in THEORICA.

## Direct project consequence

THEORICA may now route certified three-scenario additive planning problems to
`synthesize_three_vertex_additive_plan` instead of the generic Cartesian
planner.  The route returns exact value, nature certificate, executable sparse
policy, candidate accounting, and certificate validity.  Missing additivity,
malformed triples, or an excessive tied active set causes abstention.

## Limitations

- Exactly three finite ambiguity vertices; not an arbitrary or continuous set.
- Additive component payoffs; cross-component interactions invalidate the law.
- Value computation is product-free, but policy recovery currently enumerates
  only the tied active Cartesian set and therefore has a fail-closed cap.
- This is a static zero-sum result, not a sequential or adaptive-game theorem.
- Exact rational inputs are certified; floating-point conditioning is outside
  the present claim.

