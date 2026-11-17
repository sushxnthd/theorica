# P2 first integer leaf-cost breakpoint is exactly eight

## Prospective result

The two frozen endpoint predictions passed at fixed `(a,b)=(4,11)`:

| Leaf cost | Exact value | Clean group-3 children |
|---:|---:|---:|
| 7 | 33 | `[22,22,22]` |
| 8 | 34 | `[23,22,22]` |

Clean middle query group 3 is uniquely optimal at both endpoints.  Its tested
root branch is `max(33,26+c)`: at `c=7` the leaf-sensitive child first ties the
two structural children; at `c=8` it becomes the unique worst child and raises
the exact residual by one.

## Exact boundary argument

The exact value is nondecreasing in every query cost.  The previously certified
`c=1` value and the new `c=7` value are both 33.  Monotonicity therefore proves

`V_P2(4,11,c) = 33` for every integer `1 <= c <= 7`.

The exact `c=8` value is 34, so 8 is the first integer leaf-cost breakpoint.
This sharpens the prior unbounded-chamber falsification into an executable
policy boundary: use the clean separator with residual 33 through leaf cost 7;
at cost 8 the same action remains optimal but its critical child changes.

## Certificates

Each endpoint solves 4,537 Bellman states, 3,291 actions, and 115 compatibility
states.  At `c=7`, the nearest competing root action costs 37 and leaf actions
cost 40.  At `c=8`, the nearest root action still costs 37 and leaf actions
cost 42.  Thus the breakpoint is caused by a downstream leaf-sensitive child,
not a change in the root query.

The zero-production-import audit independently reconstructs the branch values,
child crossing, root minima, clean-separator classification, monotonicity
inference, and reserved-case accounting.

## Scope and limitations

This is the first integer breakpoint for P2 at one witness state and fixed
`(a,b)=(4,11)`.  It does not prove that `max(33,26+c)` remains exact beyond
`c=8`, locate the corresponding P0 breakpoint, or characterize arbitrary
states and families.  Eight cumulative family/cost cases are open; 10 remain
sealed.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_ternary_p2_first_leaf_breakpoint.py
PYTHONPATH=src python scripts/audit_qary_ternary_p2_first_leaf_breakpoint.py
```
