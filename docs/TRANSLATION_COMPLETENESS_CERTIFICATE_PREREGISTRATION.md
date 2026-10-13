# Translation-group completeness certification: frozen exact protocol

**Classification:** DISCRIMINATION / EXACT THEOREM / SYSTEM BOUNDARY

## Active kernel

- **Question:** after fully querying rows that generate a candidate subgroup `H`, can THEORICA certify from substantially fewer queries that every other unknown permutation row belongs to `H`?
- **Best-known frontier:** a supplied completeness certificate enables `rn+(n-r)b` reconstruction, but the discovery learner cannot infer that promise safely for nonfaithful operations.
- **Exact objective:** determine the worst-case zero-error query complexity of certifying containment of every remaining row in the discovered group over arbitrary permutation-row operations.
- **Strongest alternative:** group structure permits a generally subquadratic automatic certificate comparable to base-signature reconstruction.
- **Cheapest decisive falsification:** use the trivial discovered group and compare the all-identity table with a table whose untrusted row transposes two unqueried coordinates.
- **Publishable success condition:** a matching upper/lower bound, exhaustive finite verification, an independent checker, and an executable fail-closed certificate routine.
- **Project-relevance threshold:** the result must determine when THEORICA may replace an external generator-completeness certificate and change the learner's acceptance/query policy.
- **Kill condition:** any permutation outside the trivial group is uniquely excluded with fewer than `n-1` queries in the adversarial row, or `n-1` queried images fail to determine a promised permutation.

## Frozen theorem candidate

For arbitrary permutation-row operations on `n>=2` points, suppose `r` trusted rows have been fully queried and generate a candidate group `H`. Any zero-error algorithm that certifies every remaining row belongs to `H` requires, in the worst case,

```
rn + (n-r)(n-1)
```

distinct cell queries, and this number is sufficient.

The lower bound uses `H={id}`. On the all-identity operation, if any untrusted row has at least two unqueried coordinates, swapping those two coordinates gives an outside permutation with the same transcript. The upper bound queries `n-1` images of every untrusted permutation; bijectivity forces the final image, after which exact group membership is decidable.

## Frozen checks

1. Exhaust all permutations and all coordinate subsets through `n=8`.
2. For every subset of size at most `n-2`, confirm at least one outside permutation agrees with identity on the subset.
3. For every subset of size `n-1`, confirm identity is the unique agreeing permutation.
4. Independently verify the transposition construction and forced-last-image argument through `n=64` without importing the primary enumerator.
5. Exercise the production certificate on an in-group repeated-row table and an outside-transposition table.

No external holdout is opened. Historical novelty is not asserted by this exact run.
