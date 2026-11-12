# The P0 breakpoint is invariant across a new symbol orbit

## Prospective result

The all-coordinate `1 <-> 2` image of P0 had not appeared in an earlier exact
solve.  Both frozen endpoint predictions passed:

| leaf cost `c` | exact value | unique optimal group | group-0 children |
| ---: | ---: | ---: | --- |
| 18 | 37 | 0 | `[33,33,33]` |
| 19 | 38 | 0 | `[34,33,34]` |

The asymmetric second vector is the preregistered consequence of transporting
the source vector `[34,34,33]` through the symbol involution, which exchanges
ordinary response labels 1 and 2.  It is therefore a stronger check than the
scalar value alone.

By the exact `c=18` certificate, the established `c=1` value, and monotonicity,
the transformed family satisfies `V(4,11,c)=37` for every integer
`1 <= c <= 18`.  Its first positive integer leaf-cost breakpoint is exactly
`c=19`.

## Structural consequence

The level-coloured partition-hypergraph certificate fixes all ten completion
indices, maps the thirteen query groups by

`[0,1,3,2,4,6,8,10,12,9,11,5,7]`,

and validates every edge.  It fixes root group 0 while swapping its ordinary
response cells 1 and 2.  Since query costs depend only on level and the map
preserves levels, it conjugates the complete weighted Bellman game and
transports every optimal policy, not merely the tested root action.

Together with the preceding P2 orbit result, this confirms both observed
breakpoint classes on unseen algebraic families: P2 remains at 8 and P0
remains at 19.  The executable consequence is that exact values, policies, and
breakpoint certificates can be cached per certified level-preserving symbol
orbit rather than recomputed for every labelled family.

## Independent check and limits

The zero-production-import audit reconstructs both ordered group-0 child
vectors from the frozen table, recomputes their action values, minimizes over
all emitted root actions, checks lower/upper-bound equality, verifies the
query and completion maps, and validates reserved-case accounting.  Each
endpoint used 5,392 Bellman states, 4,571 evaluated actions, and 135
compatibility states.

All 18 reserved family/cost cases are now open.  This closes the frozen
holdout panel without substitution, but does not make the finite panel a proof
for arbitrary word-set modifications, coordinate permutations that change
query levels, non-level-based costs, or unrelated algebraic families.
