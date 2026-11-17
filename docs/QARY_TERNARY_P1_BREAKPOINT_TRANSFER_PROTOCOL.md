# P1 breakpoint-transfer protocol

## Question

Does the exact first leaf-cost breakpoint proved for the P0 obstruction transfer
prospectively to the isomorphic P1 obstruction at two unopened cost endpoints,
including the optimal root action and its three exact child values?

The two ten-word families are

- P0: the Boolean cube plus `200, 210`;
- P1: the Boolean cube plus `200, 220`.

The previously published, level-coloured partition-hypergraph certificate maps
every query group, completion, and nonempty query cell by the identity map.  No
P1 endpoint at the costs below is opened before this prediction is frozen.  P1
itself was previously tested at `(2,9,3)`; only these two cost instances are
prospective holdouts.

## Frozen prospective prediction

Fix root and middle costs at `(a,b)=(4,11)` and open exactly two reserved P1
leaf-cost cases:

| leaf cost `c` | predicted exact value | predicted group-0 child values |
| ---: | ---: | --- |
| 18 | 37 | `[33, 33, 33]` |
| 19 | 38 | `[34, 34, 33]` |

Group 0 is predicted to be optimal at both endpoints.  Consequently the first
positive integer P1 leaf-cost breakpoint is predicted to be exactly `c=19`,
with the constant chamber `V(4,11,c)=37` for `1 <= c <= 18`.  This is a
prospective transfer claim: an exact P1 solve must independently recover the
values rather than copy the P0 artifact.

## Falsification rule

The prediction is falsified if either endpoint's exact lower and constructive
upper bounds disagree with the frozen value, if group 0 is not optimal, if its
ordered child-value vector differs, or if a zero-production-import audit cannot
reconstruct the breakpoint statement from the emitted JSON.

Any failure is retained as a negative result.  The run opens two reserved
cases, moving the cumulative accounting from 12/18 to 14/18 and leaving four
sealed cases.
