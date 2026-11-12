# P1 inherits the exact first leaf-cost breakpoint at nineteen

## Result

The frozen transfer prediction passed both exact endpoints.  For the P1 family
(the Boolean cube plus `200, 220`) at fixed root and middle costs `(4,11)`,

| leaf cost `c` | exact minimax value | optimal groups | group-0 child values |
| ---: | ---: | --- | --- |
| 18 | 37 | `[0]` | `[33, 33, 33]` |
| 19 | 38 | `[0]` | `[34, 34, 33]` |

Thus P1 has the same first positive integer leaf-cost breakpoint as its P0
isomorph: `c=19`, and `V(4,11,c)=37` throughout `1 <= c <= 18`.

## Mechanism and consequence

The prior level-coloured partition-hypergraph certificate maps all thirteen
query groups and all ten completions from P0 to P1 by identity.  The exact P1
solve independently recovered the transferred branch

`max(37, 19+c)`.

This turns the structural certificate into an executable capability: once a
weighted breakpoint is proved for one member of this isomorphism orbit, its
optimal query and exact child costs can be transported without reopening the
whole orbit.  Direct solving remains a falsification check for held-out costs.

## Independent check and limitations

The audit imports no solver code.  It reconstructs both group-0 values from
the emitted child values, recomputes the minimum over every emitted root
action, checks lower-bound/upper-bound equality, validates the identity mapping
record, and verifies holdout accounting.  Two cases were opened: 14 of 18 are
now open, with four still sealed.

The result is exact only for this finite ten-word family and the stated cost
ray.  It does not establish a new isomorphism class, a symbolic formula for all
cost triples, or robustness under changing the word set.
