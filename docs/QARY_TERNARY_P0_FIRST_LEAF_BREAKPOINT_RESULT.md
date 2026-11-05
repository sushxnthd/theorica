# P0 first integer leaf-cost breakpoint is exactly nineteen

## Prospective result

Both frozen endpoint predictions passed at fixed `(a,b)=(4,11)`:

| Leaf cost | Exact value | Optimal query groups | Root group-0 children |
|---:|---:|---:|---:|
| 18 | 37 | `[0]` | `[33,33,33]` |
| 19 | 38 | `[0]` | `[34,34,33]` |

The root group-0 action follows the tested branch `max(37,19+c)`.  At `c=18`
all three children tie at 33; at `c=19` two leaf-sensitive children become
critical and raise the exact residual by one.

## Exact boundary argument

Exact value is nondecreasing in every query cost.  The previously certified
`c=1` value and the new `c=18` value are both 37.  Monotonicity therefore proves

`V_P0(4,11,c) = 37` for every integer `1 <= c <= 18`.

The exact `c=19` value is 38, so 19 is the first integer leaf-cost breakpoint.
This gives an executable policy boundary: root group 0 is uniquely optimal at
both tested endpoints and its critical-child set changes at the breakpoint.

## Separation from P2

At the same fixed root and middle costs, P2's first integer breakpoint is 8
and its clean-separator policy hands off at 12.  P0's first breakpoint is 19.
Thus algebraic completion structure changes not only the low-cost optimum but
also the location and mechanism of the leaf-cost phase transition.

## Exact certificates

Each endpoint solves 5,392 Bellman states, 4,571 actions, and 135 compatibility
states.  At `c=18`, root group 0 costs 37 while every other root action costs
at least 48.  At `c=19`, group 0 costs 38 while every other action costs at
least 49.

The zero-production-import audit independently reconstructs the root branch,
child vectors, root minima, monotonicity inference, and reserved-case accounting
solely from the emitted artifact.

## Scope and limitations

This is the first integer breakpoint for P0 at one witness state and fixed
`(a,b)=(4,11)`.  It does not characterize real-valued costs, prove the affine
branch beyond `c=19`, or generalize to arbitrary states and families.  Twelve
cumulative family/cost cases are open; six remain sealed.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_ternary_p0_first_leaf_breakpoint.py
PYTHONPATH=src python scripts/audit_qary_ternary_p0_first_leaf_breakpoint.py
```
