# Adaptive rack-seed acquisition has a linear competitive gap

**Result date:** 15 October 2026  
**Status:** **PASS — all frozen exact gates**

## Smallest supported claim

In THEORICA's complete-row acquisition model, under only a certified finite
left-rack promise, every deterministic always-correct seed-acquisition policy
has labeled instances with minimum operation-generating rank 2 on which it
must query all `n` translation rows. Thus automatic acquisition can cost
`n^2` oracle cells even though an optimal two-row certificate would permit
exact reconstruction in `2n` cells.

This is a row-acquisition lower bound, not a lower bound for arbitrary adaptive
cell queries.

## Construction and proof

For `n >= 3` and a distinguished element `z`, define `R(n,z)` by:

- `L_x = id` for every `x != z`;
- `L_z` fixes `z` and cycles all other `n-1` elements.

This is a left rack. If `x != z`, left self-distributivity is immediate because
`L_x` is the identity. If `x = z`, the translation assignment is constant on
the two orbits of `L_z`: the singleton `{z}` carries `L_z`, while every other
element carries the identity. Hence
`L_(x*y) = L_x L_y L_x^-1` in every case.

No singleton generates the carrier. Conversely, `{z,a}` generates it for any
`a != z`, because repeated action by `L_z` visits the full non-`z` cycle.
Therefore the minimum generating rank is exactly 2.

Run an arbitrary deterministic policy on the trivial rack `x*y=y`. A correct
policy must eventually acquire all `n` rows because the closure of any proper
seed subset is that subset itself. Let `z` be the last row in this policy's
all-identity transcript order. On `R(n,z)`, the first `n-1` acquired rows and
all observed values are identical to the trivial-rack transcript. The policy
therefore makes the same choices and cannot stop: its queried rows exclude
`z` and do not generate the carrier. It must query row `z` last. The cost is
`n` rows, while the instance optimum is 2.

Under a uniformly random labeling of this family, the exact expected number of
rows for a fixed deterministic identity-transcript order is

```
(n+1)/2 + 1/n,
```

where the extra term handles the case in which the distinguished row appears
first and a second seed is still required.

## Exact evidence

| Check | Result |
|---|---:|
| Labeled permutation-row operations exhausted through order 4 | 331,997 |
| Racks found through order 4 | 130 |
| Invalid greedy certificates | 0 |
| Greedy-suboptimal racks, order 3 | 1/13 |
| Greedy-suboptimal racks, order 4 | 12/114 |
| First counterexample order | 3 |
| Adversarial family orders checked | 3–64 |
| Family rack/rank/worst-case failures | 0 |
| Independent direct checks | 62/62 PASS |

The minimized order-3 counterexample has rows `id, id, (0 1)`. Label-order
acquisition chooses `(0,1,2)`, while `(0,2)` is a generating set.

- Primary canonical digest:
  `7544296857290ce9a67a93a6002387041510120c4ef8103b0f2e01e00d497bf2`
- Primary result-file SHA-256:
  `3cc6ced57911b8f6ea7a871d3c125ad0785597df24d2199a1f5cf81c7156806c`
- Independent audit canonical digest:
  `519f84971a6f7eee8d95e79dad2cda81aebf401e5a7ac812becbad1e464cc54e`
- Audit result-file SHA-256:
  `e8baffa06af9374ce606423320aae47379e41044500a97fafc6cebe8467d6f13`
- Frozen protocol commit:
  `c356d72856c8dec9e6f73c49b46f7f18fe8502b9`

## SCIENCE ledger

- **KNOWN:** complete seed rows plus a certified rack promise reconstruct from
  any operation-generating seed set in `|S|n` cells.
- **KNOWN:** automatically finding such a set in the same full-row interface
  can have competitive ratio `n/2` in row count, even at generating rank 2.
- **FALSIFIED:** least-outside-closure acquisition generally tracks minimum
  generating rank; the first counterexample occurs at order 3.
- **ANOMALOUS:** the additive gap already reaches 2 at order 4, consistent with
  the unbounded constructed family rather than a one-off small-case defect.
- **UNTESTED:** optimal partial-cell probing, randomized policies under a
  specified prior, noisy racks, and stronger subclasses such as connected
  quandles.

## CONSEQUENCE ledger

THEORICA now exposes automatic rack-seed acquisition only behind an explicit
`max_seed_rows` budget. The runtime returns an exact reconstruction receipt if
closure reaches the carrier and otherwise abstains with
`seed_budget_exhausted`. It does not silently imply that the acquired seed set
is minimum or near-minimum.

The earlier `|S|n` capability remains valuable when semantic seed rows are
supplied externally. To beat this new boundary automatically, THEORICA needs a
different interface: partial-row anomaly probes, additional family structure,
or an explicit distributional/randomized contract.

## Claim boundary and novelty

The rack translation identity is classical, and generating-set acquisition is
a standard algebraic concern. This result establishes a sharp systems-facing
adversarial boundary for THEORICA's current complete-row oracle interface; it
does not assert historical first priority. External expert prior-art review is
still required before any field-level novelty claim.

