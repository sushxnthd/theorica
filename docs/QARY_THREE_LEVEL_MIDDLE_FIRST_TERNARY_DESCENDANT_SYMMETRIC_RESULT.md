# Exact ternary equal-descendant-cost theorem

## Theorem

For ternary depth-three prefixes with root-query cost `x`, equal middle/leaf
cost `y`, four physical copies per prefix, one adversarial substitution, one
recognized erasure, and a middle-level first query, the exact worst-case cost
is

```text
T_3(x,y,y) = max(2x+7y, 3x+6y, 4x+3y).
```

The sharp phase boundaries are `x=y` and `x=3y`.

## Mechanism

Projecting every terminal exposure `(r,m,l)` of the frozen depth-nine ternary
unit-cost policy to `(r,m+l)` gives a single policy that meets all extreme-ray
budgets of all three cost cones:

| Active face | Cone rays | Policy/face equality |
|---|---|---|
| `(2,7)` | `(0,1)`, `(1,1)` | `7/7`, `9/9` |
| `(3,6)` | `(1,1)`, `(3,1)` | `9/9`, `15/15` |
| `(4,3)` | `(1,0)`, `(3,1)` | `4/4`, `15/15` |

Linearity proves the upper bound throughout each closed cone.  The matching
lower bound restricts the 27 ternary completions to the embedded eight binary
completions.  Third-symbol queries are constant on that subset and the other
rows reproduce the binary problem, so the three specialized binary faces
remain unavoidable.

## Evidence

- cone certificates: **3/3**;
- extreme-ray inequalities: **6/6**;
- replayed terminal transcripts: **2,721**;
- preregistered prospective cost pairs: **12/12**;
- independent ray replays: **6/6**;
- independent holdout formulas: **12/12**;
- independent exact boundary: depth eight infeasible, depth nine feasible;
- independent solver states: **78,460**;
- independent imports from `theorica`: **0**;
- deterministic primary and audit artifacts reproduce byte-for-byte.

The executable
`certify_ternary_middle_first_descendant_symmetric(root_cost,
middle_leaf_cost)` returns the three lower faces, exact optimum, active phases,
and boundaries.  It fails closed for nonpositive, Boolean, or nonintegral
costs.

## Reproduce

```bash
PYTHONPATH=src:scripts python \
  scripts/verify_qary_three_level_middle_first_ternary_descendant_symmetric.py
PYTHONPATH=scripts python \
  scripts/audit_qary_three_level_middle_first_ternary_descendant_symmetric.py
```

## Limitations

The theorem covers only arity three, depth three, costs `(x,y,y)` with positive
integer `x,y`, four copies, one substitution, one recognized erasure, and a
middle-first initial action.  It does not prove arbitrary ternary cost triples,
all arities, unrestricted first actions, deeper trees, other fault budgets, or
arbitrary query families.
