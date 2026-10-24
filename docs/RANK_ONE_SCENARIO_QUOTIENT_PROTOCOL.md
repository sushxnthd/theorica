# Frozen protocol: rank-one scenario quotient law

## Precise question

When a certified additive robust game has many ambiguity scenarios, can exact
payoff geometry prove that the game is equivalent to only two extremal
scenarios, removing the fixed `m <= 8` arrangement ceiling without enumerating
Cartesian joint actions?

## Proposed algebraic boundary

Flatten every component-local action payoff into a row of a rational matrix
`U`, with one column per ambiguity scenario. The kernel accepts exactly when
the scenario columns have affine dimension at most one, equivalently when every
row of `U` is an affine function of one nonconstant scenario coordinate
`z_j`.

For affine dimension one, every additive joint-action payoff is affine in
`z_j`. Every nature mixture therefore matters only through
`E[z]`, whose feasible set is the interval `[min z, max z]`. The many-scenario
game should equal the two-scenario game at those endpoints. If all columns are
identical, it should collapse to one effective scenario.

## Frozen predictions

1. Exact value, strict-randomization classification, and executable policy from
   the quotient match a Cartesian expanded exact solver on every opened case.
2. The returned policy has support at most two, independent of scenario count.
3. Scenarios strictly between the two feature extremes never change the value.
4. Generated rank-one holdouts with previously unseen scenario counts above
   eight are solved exactly instead of hitting the existing ambient-dimensional
   cap.
5. Any one-entry perturbation that raises affine scenario dimension above one
   is rejected before quotient planning. An endpoint-only heuristic without the
   rank certificate will be shown to fail on an adversarial rank-two witness.

## Frozen evaluation

- Opened exact sweep over rational rank-one families with 3--6 scenarios,
  multiple coordinate orderings, positive/negative/zero slopes, tied actions,
  strict-randomization cases, and pure-optimal cases.
- Strong baselines: Cartesian expanded exact solution; the existing
  fixed-scenario arrangement planner where its cap permits; uncertified
  endpoint deletion on rank-two counterexamples.
- Prospective holdouts generated from a frozen seed with 9, 13, 21, 34, and 64
  scenarios. Holdout generation is not inspected after freezing.
- Scaling witness with at least 20 components and at least 50 scenarios, for
  which Cartesian action expansion is infeasible but the quotient contains two
  scenarios.
- Independent checker recomputes the affine representation and expanded
  small-case values without importing the production quotient helper.

## Exact objective

Zero value, classification, endpoint, certificate, or realized-payoff
mismatches; zero false accepts on the rank-two falsification set; policy support
at most two; exact replay of every returned rational certificate.

## Strongest alternative explanation

Any success might come merely from duplicate scenarios or a monotone dominant
action. The sweep therefore requires distinct interior scenario columns,
opposing action slopes, and strict mixed optima. Rank-two attacks determine
whether endpoint deletion succeeds only accidentally.

## Product consequence

On a valid certificate, THEORICA may route an arbitrary-scenario additive game
to its exact two-vertex planner. On failure it must abstain from the quotient and
retain the existing general planner boundary.

## Kill condition

Kill or reformulate the kernel on any false acceptance of affine dimension
greater than one, any mismatch with expanded exact minimax, any returned support
above two, or any inability to certify all original-scenario payoffs exactly.

## Smallest publishable claim

A positive result supports only an exact product-free scenario quotient for
certified additive games whose local payoff scenario columns have affine
dimension at most one. It does not solve general low-rank games, nonadditive
payoffs, or arbitrary many-scenario arrangements.
