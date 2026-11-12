# Set-valued optimal-policy bisimulation result

The complete cost-optimal policy quotients of `P0` and `P2` differ under all
four preregistered root conditions. The preceding selected-tree separation is
therefore not a deterministic tie-breaking artifact.

| Root | Exact cost | P0 optimal root actions | P2 optimal root actions | Equal? |
|---|---:|---:|---:|---:|
| Unrestricted middle | 51 | 2 | 2 | No |
| Forced middle 1 | 51 | 1 | 1 | No |
| Forced middle 2 | 51 | 1 | 1 | No |
| Forced middle 3 | 52 | 1 | 1 | No |

The content-addressed quotients contain 70 canonical nodes for `P0` and 67 for
`P2`. In the three cost-51 comparisons, the first localized difference is an
erasure-conditioned ordinary child whose exact residual value is 29 for `P0`
and 27 for `P2`. At the cost-52 root, the truthful cell-size vectors differ
immediately: `[1,9]` versus `[1,1,8]`.

Exact enumeration solved 942,101 value states for `P0` and 943,624 for `P2`.
The zero-production-import audit replayed 2,124 reachable Bellman records,
4,652 evaluated actions, 137 content hashes, and every retained optimal edge.
Every omitted finite action was strictly worse, with minimum Bellman gap 1.

No reserved case was opened; all 18 remain sealed. The claim covers every exact
cost-optimal policy in the frozen four-copy grouped-query model for the already
opened `P0/P2` instance at `(2,9,3)`. It does not yet characterize other costs
or families. The next experiment should extract the smallest algebraic state
predicate predicting the residual-value split and test it prospectively.

