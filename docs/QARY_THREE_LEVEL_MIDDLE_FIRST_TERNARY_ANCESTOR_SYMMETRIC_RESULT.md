# Exact ternary equal-ancestor-cost theorem

## Theorem

For ternary depth-three prefixes with root and middle query cost `x`, leaf cost
`y`, four physical copies per prefix, one adversarial substitution, one
recognized erasure, and a middle-level first query, the exact worst-case cost is

```text
T_3(x,y) = max(7x+y, 6x+3y, 5x+4y).
```

The phase boundaries are `x=2y` and `x=y`.

## Mechanism

The depth-nine ternary policy synthesized at unit costs has projected terminal
exposures `(root+middle, leaf)` satisfying every extreme-ray budget of all
three cost cones:

| Active face | Cone rays | Policy/face equality |
|---|---|---|
| `(7,1)` | `(1,0)`, `(2,1)` | `7/7`, `15/15` |
| `(6,3)` | `(1,1)`, `(2,1)` | `9/9`, `15/15` |
| `(5,4)` | `(0,1)`, `(1,1)` | `4/4`, `9/9` |

Linearity extends these inequalities throughout each closed cone.  Thus one
ternary policy—not three separately selected scalar policies—supplies the
universal upper bound on the entire positive `(x,y)` quadrant.

For the lower bound, restrict the 27 ternary completions to the embedded eight
binary completions.  Queries on prefixes containing the third symbol are
constant on this subset; the remaining rows reproduce the binary problem.
The proved binary lower faces `(7,1)`, `(6,3)`, and `(5,4)` therefore remain
valid.

## Evidence

- cost cones certified: **3/3**;
- extreme-ray inequalities: **6/6**;
- replayed terminal transcripts: **2,721**;
- prospective exact cost pairs: **12/12**;
- independent ray replays: **6/6**;
- independent holdout formulas: **12/12**;
- independent exact boundary: depth eight infeasible, depth nine feasible;
- independent solver states: **78,460**;
- independent THEORICA imports: **0**;
- artifacts reproduce byte-for-byte.
- full regression: **296/296** tests;
- scoped Ruff and diff-integrity checks: clean.

The executable
`certify_ternary_middle_first_ancestor_symmetric(root_middle_cost, leaf_cost)`
returns all three face values, the exact optimum, active phases, and phase
boundaries.  It fails closed on nonpositive, Boolean, or nonintegral costs.

## Reproduce

```bash
PYTHONPATH=src:scripts python \
  scripts/verify_qary_three_level_middle_first_ternary_ancestor_symmetric.py
PYTHONPATH=scripts python \
  scripts/audit_qary_three_level_middle_first_ternary_ancestor_symmetric.py
```

## Limitations

The theorem covers only arity three, depth three, equal root/middle costs,
positive integer costs, four copies, one substitution, one recognized erasure,
and a middle-first initial action.  It does not prove arbitrary ternary cost
triples, all arities, unrestricted first actions, deeper trees, other fault
budgets, or arbitrary query families.
