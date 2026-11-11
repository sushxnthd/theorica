# The P2 breakpoint is invariant across a new symbol orbit

## Prospective result

The all-coordinate `1 <-> 2` image of P2 had not appeared in an earlier exact
solve.  Its frozen endpoint predictions both passed:

| leaf cost `c` | exact value | unique optimal group | group-2 children |
| ---: | ---: | ---: | --- |
| 7 | 33 | 2 | `[22,22,22]` |
| 8 | 34 | 2 | `[23,22,22]` |

Therefore the transformed family has the same first positive integer leaf-cost
breakpoint as P2: `c=8`, with `V(4,11,c)=33` for integer `1 <= c <= 7`.

## Structural mechanism

The coordinatewise involution fixes the prefix symbol 0 and swaps symbols 1
and 2.  It consequently permutes query cells and query groups without changing
query level.  The exact certificate maps the source clean separator from group
3 to target group 2 and validates every graph edge.  Because level costs are
preserved, the map conjugates the complete weighted decision game, not merely
the two tested root actions.

The direct solve recovered the transported branch `max(33,26+c)`.  This gives
an executable consequence: exact policies and cost boundaries may be cached
once per level-preserving symbol orbit and transported by the certified query
permutation.

## Independent check and limits

The zero-production-import audit recomputes both group-2 action values from the
emitted children, minimizes over every emitted root action, verifies exact
lower/upper-bound equality, checks the frozen query permutation and completion
map, and validates reserved-case accounting.  Sixteen of eighteen cases are
now open; two remain sealed.

This result covers one new finite family, one witness state, integer leaf
costs, and one level-preserving involution.  It does not prove invariance under
symbol maps that move 0, coordinate permutations that change query levels, or
arbitrary modifications of the word set.
