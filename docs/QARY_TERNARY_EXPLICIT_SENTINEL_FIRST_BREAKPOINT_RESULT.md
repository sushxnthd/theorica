# The explicit outside token moves P0's first breakpoint from 19 to 23

## Exact result

At the frozen witness state and fixed root/middle costs `(a,b)=(4,11)`, both
prospective endpoint predictions passed:

| leaf cost | exact value | unique root group | ordered root children |
| ---: | ---: | ---: | --- |
| 22 | 37 | 0 | `[33,33,33]` |
| 23 | 38 | 0 | `[34,34,33]` |

Each exact solve enumerated 20,085 Bellman states, evaluated 15,794 actions,
and certified 95 compatibility states.

Together with the certified value 37 at `c=1` and monotonicity in positive
query costs, the `c=22` endpoint proves

`V_explicit(4,11,c)=37` for every positive integer `1<=c<=22`.

The value 38 at `c=23` proves that 23 is the first positive integer
breakpoint.

## Mechanism and product consequence

The two previously opened sentinel endpoints gave root-group-0 children
`[29,29,33]` at `c=18` and `[30,30,33]` at `c=19`. The new endpoints confirm
the local branch

`children_0(c)=[c+11,c+11,33]`,

with root action

`4+max(c+11,33)=max(37,c+15)`

through the tested transition. The constant child 33 controls through `c=22`;
the two leaf-sensitive children become 34 at `c=23`.

Under the old encoding, outside-prefix and observed zero shared response `0`,
and the first P0 breakpoint occurred at 19. Making outside-prefix explicit
moves the certified breakpoint from 19 to 23. This is a concrete planning
consequence: repairing alphabet covariance also buys four additional integer
leaf-cost units before worst-case value increases.

## Independent check

The zero-production-import audit reconstructed both root minima from emitted
actions, checked exact lower/upper-bound equality, ordered child vectors,
unique optimality, and the monotonicity argument. Evidence was regenerated
byte-for-byte, targeted lint passed, and the complete regression suite passed.

## Limits

The result is bounded to this P0 witness state, positive integer leaf costs,
the explicit outside token, and fixed `(a,b)=(4,11)`. The displayed affine
branch is certified at the opened endpoints and explains the transition, but
is not claimed for arbitrary larger costs, families, or states.
