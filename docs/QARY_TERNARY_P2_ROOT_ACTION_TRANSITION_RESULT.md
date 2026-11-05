# P2 root-action collision and strict handoff confirmed

## Prospective result

Both frozen endpoint predictions passed at fixed `(a,b)=(4,11)`:

| Leaf cost | Exact value | Optimal query groups | Group 0 children | Clean group 3 children |
|---:|---:|---:|---:|---:|
| 11 | 37 | `[0,3]` | `[26,26,33]` | `[26,22,22]` |
| 12 | 37 | `[0]` | `[27,27,33]` | `[27,22,22]` |

At `c=11`, the clean separator reaches value `26+c=37` and ties the
constant-value root competitor.  At `c=12`, its value rises to 38 while root
group 0 remains at 37, so the optimizer hands off strictly from the clean
middle query to the non-clean root query.

## Executable policy consequence

The first-breakpoint result showed that leaf cost raises a downstream child
without initially changing the root query.  The present result identifies the
next policy event: at the tested collision endpoint both policies are optimal;
one integer later, only root group 0 is optimal.  An exact planner can therefore
select either certified policy at `c=11`, but must select group 0 at `c=12`.

## Exact certificates

Each endpoint solves 4,537 Bellman states, 3,291 actions, and 115 compatibility
states.  At `c=11`, groups 0 and 3 both cost 37; every other root action costs
48.  At `c=12`, group 0 costs 37, group 3 costs 38, and every other action
costs at least 48.

The zero-production-import audit independently reconstructs the nominated
child vectors, action values, root minima, clean-separator classification,
tie-to-handoff transition, and reserved-case accounting solely from the
emitted artifact.

## Scope and limitations

This is a prospective two-endpoint transition certificate for P2 at one
witness state and fixed `(a,b)=(4,11)`.  It does not prove that the displayed
action formulas hold at unopened costs, characterize real-valued costs,
locate the P0 transition, or generalize to arbitrary families and states.
Ten cumulative family/cost cases are open; eight remain sealed.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_ternary_p2_root_action_transition.py
PYTHONPATH=src python scripts/audit_qary_ternary_p2_root_action_transition.py
```
