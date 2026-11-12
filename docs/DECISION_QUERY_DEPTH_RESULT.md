# Exact decision-query depth

## Result

Let `S` be the finite set of algebraic completions surviving a corrupted
transcript. Each completion induces an exact rational robust game. Write
`C(S)` when all games in `S` have the same value and at least one common
optimal randomized policy. For unused exact queries `Q`, query `q` partitions
`S` into its nonempty outcome cells `S(q,y)`.

The minimum worst-case number of additional queries needed to identify a
robust policy is exactly

`D(S,Q) = 0` when `C(S)`, and otherwise

`D(S,Q) = 1 + min_q max_y D(S(q,y), Q - {q})`.

Uninformative queries and queries with any impossible continuation are
discarded. If no query remains with a finite continuation, decision
identification is impossible for the supplied query family. The production
selector returns the minimizing adaptive tree, exact rational policies at its
leaves, or a fail-closed impossibility result.

If arbitrary binary questions may be asked and `kappa` is the minimum number
of common-policy-compatible blocks partitioning `S`, the depth is
`ceil(log2(kappa))`. Thus model identification can be unnecessarily expensive:
the tree needs to identify only a block in the decision quotient.

## Proof

The recurrence follows by induction on `|Q|`. A compatible current set needs
no further query. Otherwise every valid plan must choose some first query `q`;
an adversary can return the outcome whose child needs the largest remaining
depth, giving the lower bound. Choosing a `q` minimizing that maximum and then
using each inductively optimal child gives the matching upper bound. If every
candidate has an impossible child, no finite tree can certify all outcomes.

For unrestricted binary questions, every depth-`d` tree has at most `2^d`
leaves, so it cannot separate `kappa` required compatible blocks when
`d < ceil(log2(kappa))`. Conversely, label the blocks with fixed-length binary
codes and query their code bits.

## Frozen evidence

| Family | Result |
|---|---:|
| Opened binary feature codes, 2–8 completions | 7/7 exact |
| Prospective 32- and 64-completion codes | depths 5 and 6 |
| Decision-quotient savings, dimensions 2–6 | 5/5 exact |
| Missing-coordinate attacks | 5/5 fail closed |
| Redundant and constant query controls | 4/4 no improvement |
| Higher-order 3–6 action conflicts | 4/4 exact |
| Independent stdlib-only replay | 27/27 |

Across the five saving cases, the decision quotient used depth one while
unique-model recovery needed depth two through six, saving 15 worst-case
queries in aggregate. The 32- and 64-completion prospective families returned
the frozen predictions exactly. In every missing-coordinate attack, two
distinct uniquely optimal policies remained inseparable and the selector
abstained.

The higher-order face family is an adversarial baseline: every pair of
completion games shares an optimal policy, so a pairwise-conflict graph has no
edges, but the full family has no common policy. One query separates a proper
face from its complement and makes both leaves compatible. This demonstrates
why the exact common-policy predicate, rather than pairwise conflict alone, is
required.

## Executable consequence

After finite-list transcript decoding, THEORICA can now plan follow-up
measurements against the decision quotient itself. It stops as soon as the
remaining completions share an exact robust policy, even if the scientific
model is still ambiguous. If the available measurements cannot guarantee such
a leaf, it returns no partial plan.

## Reproduction

```bash
python scripts/verify_decision_query_depth.py
python scripts/audit_decision_query_depth.py
pytest -q tests/test_corruption_resilient_features.py
```

Primary and independent evidence is stored under
`results/decision_query_depth/` and is deterministic.

## Novelty boundary and limitations

Bellman recurrences, optimal decision trees, and binary information bounds are
classical. The bounded contribution is their exact composition with
THEORICA's corrupted algebraic completion list and its non-pairwise
common-robust-policy predicate, yielding an auditable optimal follow-up policy
and a fail-closed product rule.

The implementation assumes a finite enumerated completion set, exact rational
games, and a supplied finite table of exact query outcomes. Its dynamic program
is exponential in the number of available queries and completions. Continuous
version spaces, noisy follow-up outcomes, approximate policies, query costs,
and online generation of algebraic queries require separate theory and are not
claimed here.
