# Frozen P2 symbol-orbit breakpoint transfer

## New family

Apply the involution `1 <-> 2` independently in all three coordinates to the
P2 words.  The resulting ten-word family is

`000, 002, 020, 022, 200, 202, 220, 222, 120, 110`.

This family has not appeared in an earlier exact solve.  A level-coloured
partition-hypergraph check, performed before opening either cost endpoint,
maps all ten completions identically and maps the thirteen query groups as

`[0,1,3,2,4,6,8,10,12,9,11,5,7]`.

In particular, P2's clean separator at source group 3 transports to target
group 2.  The certificate preserves query levels, so it preserves every
weighted minimax policy for any level-cost triple.

## Frozen prediction

At fixed root and middle costs `(a,b)=(4,11)`, open exactly two reserved cases:

| leaf cost `c` | predicted exact value | predicted target group-2 children |
| ---: | ---: | --- |
| 7 | 33 | `[22,22,22]` |
| 8 | 34 | `[23,22,22]` |

Target group 2 is predicted to be uniquely optimal at both endpoints.  Hence
the transformed family is predicted to satisfy `V(4,11,c)=33` for integer
`1 <= c <= 7`, with its first positive integer leaf-cost breakpoint at `c=8`.

## Falsification and accounting

The prediction fails if the direct exact solve disagrees on either minimax
value, the optimal group set, or the ordered target group-2 child vector; if
the structural map does not validate edge-by-edge; or if a zero-production-
import audit cannot reconstruct the claims from emitted JSON.  Failures remain
recorded as negative evidence.

These two endpoints move the cumulative reserved-case count from 14/18 to
16/18, leaving two cases sealed.
