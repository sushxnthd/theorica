# Frozen P0 symbol-orbit breakpoint transfer

## New family

Apply the involution `1 <-> 2` independently in all three coordinates to the
P0 words.  The resulting ten-word family is

`000, 002, 020, 022, 200, 202, 220, 222, 100, 120`.

This family has not appeared in an earlier exact solve.  A level-coloured
partition-hypergraph check, performed before opening either cost endpoint,
maps all ten completions identically and maps the thirteen query groups as

`[0,1,3,2,4,6,8,10,12,9,11,5,7]`.

In particular, P0's unique root group 0 is fixed.  Its ordinary response
labels 1 and 2 are exchanged, while response label 0 is fixed.  Because the
certificate preserves query levels, it preserves every weighted minimax
policy for any level-cost triple.

## Frozen prediction

At fixed root and middle costs `(a,b)=(4,11)`, open exactly the final two
reserved cases:

| leaf cost `c` | predicted exact value | predicted target group-0 children |
| ---: | ---: | --- |
| 18 | 37 | `[33,33,33]` |
| 19 | 38 | `[34,33,34]` |

Target group 0 is predicted to be uniquely optimal at both endpoints.  Hence
the transformed family is predicted to satisfy `V(4,11,c)=37` for every
integer `1 <= c <= 18`, with its first positive integer leaf-cost breakpoint
at `c=19`.

## Falsification and accounting

The prediction fails if the direct exact solve disagrees on either minimax
value, the unique optimal group, or the ordered target group-0 child vector;
if the structural map does not validate edge-by-edge; or if a zero-production-
import audit cannot reconstruct the claims from emitted JSON.  Failures remain
recorded as negative evidence.

These endpoints move the cumulative reserved-case count from 16/18 to 18/18.
No additional family or cost case may be substituted after either endpoint is
opened.
