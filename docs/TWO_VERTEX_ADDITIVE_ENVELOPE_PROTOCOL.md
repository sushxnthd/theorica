# Two-vertex additive envelope protocol

## Active kernel

- **Question:** For an additive robust game with exponentially many joint
  actions but exactly two coupled ambiguity vertices, can THEORICA compute an
  exact optimal policy and decide whether randomization is necessary without
  enumerating the Cartesian action space?
- **Frontier:** A general two-column matrix game has an optimal maximizing
  strategy with support at most two. The preceding coupled-additive theorem
  removes Cartesian policy variables but its generic active-set solver and
  common-mass coupling do not exploit the two-vertex algebra.
- **Objective:** Derive and implement a product-free exact law whose candidate
  set has size at most `2 + sum_t binom(|A_t|, 2)`, whose returned policy has
  support at most two, and whose strict-randomization decision matches a fully
  expanded exact solver on every feasible frozen case.
- **Strongest alternative explanation:** Any gain is merely the classical
  two-column support bound; additivity supplies no usable product-free
  construction or strictness criterion.
- **Cheapest decisive falsification:** Exhaust all pairs of two-action
  components with payoffs in `{0,1,2}`, then compare exact values and
  strict-randomization decisions against independent Cartesian expansion.
- **Unseen prediction:** On seed `20261027`, 32 disjoint mixed-dimension games
  (3-6 components, 2-4 actions each, integer payoffs 0-7) will have zero value,
  policy, and strictness mismatches; every strict case will use exactly two
  joint atoms and every non-strict case will expose a pure witness.
- **Publishable threshold:** Exact theorem and proof; zero mismatches in the
  exhaustive sweep and frozen holdout; independent implementation; explicit
  failure boundary; reproducible raw evidence.
- **Project consequence threshold:** A 20-component, five-action witness must
  replace `5^20` joint actions with at most 202 exact envelope candidates and
  return an executable policy with at most two atoms.
- **Kill condition:** Any exact-value mismatch, false strictness decision,
  support above two, invalid pure witness, or inability to fail closed when the
  additivity certificate is absent.

## Frozen theorem target

For component action payoff pairs `(u_ta, v_ta)`, define

`g(lambda) = sum_t max_a [lambda u_ta + (1-lambda) v_ta]`.

The robust value is `min_[0,1] g(lambda)`. A minimizer occurs at an endpoint or
at a pairwise line intersection within one component. At an interior minimizer,
a deterministic optimum exists iff zero is in the Minkowski sum of the payoff
difference sets of the tied component actions. Otherwise two extreme tied
joint responses bracket zero and their exact mixture is optimal; randomization
is necessary.

## Frozen evidence design

1. Exhaustive opened family: all 6,561 ordered pairs of two-action components
   with payoffs in `{0,1,2}`.
2. Prospective holdout: 32 PRNG-generated cases under seed `20261027`, generated
   only after this protocol is committed.
3. Expanded exact baseline: enumerate joint actions and invoke a separate exact
   two-column solver.
4. Independent checker: rederive the dual envelope, expand all tractable cases,
   validate both scenario payoffs, pure witnesses, support, and evidence digest
   without importing the new production function.
5. Negative gate: missing additivity certificate and malformed payoff pairs
   must be rejected before planning; capped exact tied-difference search must
   abstain rather than approximate.

## Claim boundary

Finite minimax, two-column support bounds, upper envelopes, and Minkowski sums
are classical. The candidate claim is the exact compositional envelope and
zero-sum strictness certificate integrated into THEORICA, with prospective
cross-dimensional validation. It does not cover three or more coupled vertices,
uncertified cross-component payoffs, approximate additivity, or unbounded
tied-difference state growth.
