# Frozen protocol: optimal adaptive decision queries with adversarial lies

Status: frozen before implementation.

## Question

Given a finite algebraic completion list, a finite set of follow-up query
instances, and at most `t` adversarial answer substitutions, what is the exact
minimum worst-case number of adaptive queries needed to identify one common
robust policy and value?

## Predicted theorem

Let `ell_theta` be the minimum number of lies needed to make completion
`theta` consistent with the current transcript. Completion `theta` remains
feasible exactly when `ell_theta <= t`. For remaining query instances `Q`, let
`D(ell, Q)` be zero when the feasible completions share one exact robust
decision. Otherwise

`D(ell, Q) = 1 + min_{q in Q} max_{y in A_q} D(ell + 1[c_theta(q) != y], Q - {q})`,

where infeasible completions are clipped at `t + 1`, branches with no feasible
completion are omitted, and the value is infinity if no query has finite
children. `A_q` is the declared finite answer alphabet of query `q`.

The recurrence is exact: the lie-count vector is a sufficient transcript
state, every feasible answer branch is an adversary move, and backward
induction supplies both the lower bound and an executable optimal policy. A
leaf is valid only when THEORICA's full common-policy predicate succeeds; a
pairwise compatibility graph is not a valid substitute.

## Predicted algebraic separation

Index `2^m` incompatible robust decisions by leaves of a complete binary
prefix tree. Each internal-node query returns the next branch bit inside its
subtree and zero outside it. Provide three physical copies of each query and
allow one lie.

- Majority querying only the nodes on the realized root-to-leaf path gives an
  adaptive upper bound `3m`.
- Each of the `2^(m-1)` sibling leaf pairs differs only on its parent query.
  Any fixed one-lie schedule therefore requires all three copies of every
  leaf-parent query, for a lower bound `3 * 2^(m-1)`.

Thus the same frozen query library has a linear adaptive upper bound and an
exponential nonadaptive lower bound. The primary solver must return the exact
adaptive optimum, not merely the constructive upper bound.

## Frozen experiments

- Opened two-class repetition controls for `t = 0, 1, 2`, predicted exact
  depths `1, 3, 5`; deleting one required copy must fail closed.
- Opened prefix-tree families at depths two and three.
- Prospective untouched depth-four prefix tree (16 completions), with exact
  optimal depth at most 12 versus a certified fixed-schedule lower bound 24.
- Higher-order three- through six-action face families where every pair of
  completions is compatible but the full family is not. The exact tree must
  use the common-policy predicate and remain robust to one lie.
- Independent checker using only the Python standard library, with no
  THEORICA imports.

## Strong baselines

- No-error adaptive decision depth.
- Fixed-schedule decision corruption radius.
- Repetition of a clean decision tree.
- Unique-model identification.
- Pairwise decision-conflict graphs.

## Publishable threshold

- Exact recurrence agrees with exhaustive transcript replay on every opened
  case.
- The prospective 16-completion family has finite exact depth no greater than
  12 and beats the fixed lower bound of 24.
- All missing-copy attacks abstain.
- All higher-order cases have zero pairwise conflict edges while the exact
  solver still detects and resolves the full conflict.
- Returned trees carry lie-count states and rational leaf decisions and pass
  an independent structural replay.

## Novelty and kill boundary

Liar games, dynamic programming, and repetition codes are classical. The
bounded contribution sought is their exact composition with THEORICA's
non-transitive algebraic decision quotient, plus an executable separation
between fixed and adaptive scientific queries. Kill or reformulate if the
prospective adaptive/fixed separation fails, if pairwise compatibility is
sufficient on the higher-order families, or if the returned policy cannot be
independently replayed.
