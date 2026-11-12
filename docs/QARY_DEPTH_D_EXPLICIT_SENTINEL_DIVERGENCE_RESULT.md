# Depth-d divergence quotient theorem

## Central theorem

Let `q>=3`, `d>=2`, and let the base completions be the binary cube
`B_d={0,1}^d`.  Add two distinct words from

`F_{q,d}={2} x {0,...,q-1}^{d-1}`.

Under the complete q-ary prefix-query library with a distinguished outside
response, the level-cost-preserving active query-system class is determined
exactly by `r`, the length of the common prefix of the two suffixes after their
fixed leading symbol 2.

Therefore:

- there are exactly `d-1` policy-transport classes;
- the class indexed by `0<=r<=d-2` contains

  `N_r = C(q,2) q^r q^{2(d-r-2)} = (q-1)q^{2d-r-3}/2`

  families; and
- one synthesized policy per class transports to every family in that class
  for every positive level-cost vector under the fixed fault, erasure, and
  copy model.

The counts satisfy

`sum_r N_r = C(q^{d-1},2)`.

## Mechanism

Before divergence, one prefix query contains both added completions.  At the
first differing suffix coordinate, that shared path splits into two singleton
paths.  Every later active query lies on one of those separate paths.  Symbol
names and later suffix values only relabel query groups and response cells.

All other prefixes return the outside token for every completion.  Such rows
cannot separate a nonterminal live set and are minimax-dominated.  The first
level at which the two added completions split is preserved by every
level-coloured query-system isomorphism, proving that different `r` values are
not isomorphic.

This gives an executable capability: compute `r` in linear time, select one of
`d-1` canonical policies, and transport its completion, query, and response
labels constructively.  No family-specific search is required.

## Complete unseen depth-four test

The frozen ternary depth-four universe passed exactly:

| Common suffix prefix `r` | Families | Predicted |
|---:|---:|---:|
| 0 | 243 | 243 |
| 1 | 81 | 81 |
| 2 | 27 | 27 |

All 351 unordered extensions were classified, and every one received an
edge-checked constructive transport from its predicted representative.  The
three frozen holdouts passed.  Representatives from different classes were
independently certified non-isomorphic.  Replacing 351 family-specific solves
with three representatives yields a **117-fold** reduction.

The first generic backtracking implementation did not finish at useful
latency on the 18-completion cube.  That negative computational result was
preserved by changing the experiment to a constructive partition bijection:
fix the completion map, match same-level query partitions, and validate every
response-cell edge.  The complete constructive enumeration finished in under
30 seconds in the local environment.

## Independent verification

The zero-production-import audit independently reconstructed:

- all 351 unordered families and the 243/81/27 split;
- 354 completion/query/response-cell transports, including the holdouts;
- three cross-class non-isomorphism certificates;
- 42 additional closed-form identity checks over `3<=q<=9` and `2<=d<=7`;
  and
- the 117-fold representative-solve reduction.

The result SHA-256 is
`00d69ec8af68c2624cfa43c63e339033152892685a7785dee36c6eda90fdd133`;
the audit SHA-256 is
`2ebafdf9bf3c364f453f5837ca19638db550db26d45614ad12bf38c7838fe7f8`.

## Limits

The theorem covers a binary cube plus exactly two added words with a shared
leading symbol, complete prefix libraries, explicit outside responses, and
level-only positive costs.  It does not classify three or more added words,
aliased outside responses, incomplete libraries, non-level costs, or different
adversarial semantics.  The depth-four experiment is structural; it does not
open a new numerical minimax sweep.  PR #13 remains draft and unmerged.
