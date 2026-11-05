# Frozen protocol: exact decision-query depth

Status: frozen before implementation.

## Question

Given finitely many algebraic completions that survive a corrupted transcript,
and a finite family of exact follow-up queries, what is the minimum worst-case
number of additional queries needed to identify one robust policy even when the
underlying completion remains unidentified?

## Theorem prediction

For a completion subset `S`, let `C(S)` mean that all games in `S` have one
common exact robust policy and value. For unused queries `Q`, where query `q`
partitions `S` into nonempty outcome cells `S(q,y)`, the optimal adaptive depth
obeys

`D(S,Q) = 0` if `C(S)`, and otherwise

`D(S,Q) = 1 + min_q max_y D(S(q,y), Q - {q})`,

where uninformative queries and branches with no finite continuation are
discarded. If no query has a finite continuation, exact decision identification
is impossible for the supplied query family.

The recurrence is both necessary and sufficient by induction on the remaining
query set, so it yields an executable optimal query tree rather than a heuristic.

If arbitrary binary questions are permitted and `kappa` is the minimum number
of common-policy-compatible blocks partitioning the completions, the exact
depth is `ceil(log2(kappa))`: every depth-`d` tree has at most `2^d` compatible
leaves, while a `kappa`-block partition can be encoded in that many bits.

## Frozen boundary sweep

- Opened affine-code families with 2–8 completions.
- Pairwise-incompatible equal-value games indexed by binary feature codes.
- Prospective untouched dimensions 5 and 6: coordinate queries should require
  exactly 5 and 6 worst-case queries across 32 and 64 completions.
- Redundant and constant queries, which must never improve the optimum.
- Missing-coordinate attacks, which must return impossibility rather than a
  truncated plan.
- Higher-order policy conflicts where every proper face is compatible, to show
  that pairwise conflict graphs are not a complete baseline.
- Independent dynamic-program replay without importing THEORICA production code.

## Strong baselines

- Unique-completion depth.
- Greedy largest-split selection.
- Pairwise-conflict-only compatibility.
- Nonadaptive use of every query.

## Publishable threshold

- Exact recurrence agreement on every enumerated case.
- Predicted depth 5 and 6 on untouched coordinate families.
- Exact impossibility on every missing-coordinate attack.
- At least one family where decision depth is strictly smaller than unique-model
  depth.
- Deterministic evidence, independent audit, full regression, and a production
  selector returning an auditable tree.

## Claim boundary

The Bellman recurrence and decision-tree information bound are classical. The
bounded contribution is their exact composition with THEORICA's corrupted
algebraic completion games and common-robust-policy terminal predicate.

## Kill condition

Kill the extension if the recurrence disagrees with exhaustive trees, if the
selector returns a non-identifying leaf, or if it never improves on unique-model
recovery in a frozen positive family.
