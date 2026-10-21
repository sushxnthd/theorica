# Frozen protocol: two-vertex sparse-support law

## Active kernel

- **Precise question.** For an arbitrary finite set of query actions and
  exactly two ambiguity vertices, can THEORICA replace generic support
  enumeration by an exact certificate showing that an optimal robust plan uses
  at most two actions, and characterize exactly when a mixture strictly beats
  every pure query?
- **Best-known frontier.** The current fast path handles exactly two actions
  against any number of ambiguity vertices by optimizing a one-dimensional
  lower envelope. Finite zero-sum games and linear-programming support bounds
  are classical, but the runtime lacks the dual exact geometry and executable
  certificate for arbitrarily many actions against two vertices.
- **Exact objective.** Derive a necessary-and-sufficient strict-randomization
  criterion, an exact rational planner, and a locally checkable certificate.
  Exhaustively compare it with an independent exact oracle on every `3 x 2`
  and `4 x 2` payoff matrix over `{0,1,2}`.
- **Strongest alternative explanation.** Any observed two-action support is
  merely a small-grid artifact or generic LP behavior with no sharper
  criterion, canonical certificate, or runtime consequence.
- **Cheapest decisive falsification.** Find a matrix for which the proposed
  pairwise crossing rule disagrees with the exact convex-hull optimum, or an
  optimal value that requires support on three actions.
- **Mechanism-derived unseen prediction.** Appending any action whose payoff
  point lies strictly southwest of the certified diagonal crossing leaves the
  policy and value unchanged; appending `(1,1)` to the frozen witness replaces
  the mixture by that pure action.
- **Publishable threshold.** Exact theorem and proof; zero mismatches over the
  frozen enumeration; independent implementation and digest agreement;
  adversarial equality/duplicate/dominated-action checks; repository tests and
  dedicated CI green; primary-literature priority audit with the claim narrowed
  to the specialized planner and certificate.
- **Project-consequence threshold.** Replace the generic exact-support search
  whenever the ambiguity quotient has two vertices, returning a proof object
  and using at most two executable queries regardless of the number of
  available actions.
- **Kill condition.** Any exact value mismatch, any required support of size
  three, any invalid certificate, or failure to improve THEORICA's executable
  reasoning path kills this kernel.

## Frozen theorem candidate

Represent action `i` by its two payoffs `p_i=(a_i,b_i)`. Let

`p = max_i min(a_i,b_i)`.

The candidate law is:

1. an optimal robust plan has support at most two;
2. strict randomization is possible exactly when some pair lies on opposite
   sides of the diagonal and its segment crosses `x=y` at value `t>p`;
3. the largest such crossing value is the robust optimum;
4. the two endpoint actions plus the exact mixing weight form a complete
   primal certificate, while the diagonal crossing supplies equal ambiguity
   payoffs.

The primary implementation may scan all pairs in `O(n^2)` exact arithmetic.
No asymptotic novelty is required for this run.

## Frozen enumeration and predictions

- Enumerate all `3 x 2` and `4 x 2` matrices over `{0,1,2}`: `729 + 6,561 =
  7,290` games.
- The independent oracle enumerates all pure actions and all pairwise diagonal
  intersections without importing the production solver.
- Required mismatches: zero for value, strictness, policy realization, support
  size, and certificate validity.
- Frozen strict witness: actions `(0,2),(2,0),(0,0)` must mix the first two at
  `(1/2,1/2)` for value `1`, strictly above pure value `0`.
- Frozen dominated append: adding `(1/4,1/4)` must leave that certificate and
  value unchanged.
- Frozen overriding append: adding `(3/2,3/2)` must select the new pure action
  at value `3/2` and report no strict-randomization advantage.

All generated artifacts must be canonical JSON with fixed ordering and a
SHA-256 digest reproduced by the independent checker.
