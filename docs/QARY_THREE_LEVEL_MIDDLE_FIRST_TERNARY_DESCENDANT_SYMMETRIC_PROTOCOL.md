# Frozen protocol: ternary equal-descendant-cost law

## Question

For ternary depth-three prefixes with root-query cost `x` and equal middle/leaf
cost `y`, determine the exact worst-case cost under four physical copies, one
adversarial substitution, one recognized erasure, and a middle-level first
query.

## Prospective claim

Before inspecting any scalar outcomes beyond the existing unit-cost policy,
test the binary-embedding lower envelope

```text
T_3(x,y,y) = max(2x+7y, 3x+6y, 4x+3y).
```

The predicted phase boundaries are `x=y` and `x=3y`.

## Decisive upper-bound test

Project each terminal exposure `(r,m,l)` of the already frozen ternary
unit-cost policy to `(r,m+l)`.  The claim survives only if that single policy
satisfies all six extreme-ray inequalities:

| Face | Required cone rays |
|---|---|
| `(2,7)` | `(0,1)`, `(1,1)` |
| `(3,6)` | `(1,1)`, `(3,1)` |
| `(4,3)` | `(1,0)`, `(3,1)` |

No policy may be resynthesized after seeing a failed ray.  Any strict budget
violation falsifies the proposed one-policy proof route and must be retained.

## Lower bound

Restrict the 27 ternary completions to the eight binary completions.  Queries
using the third symbol are constant on that subset, while the remaining query
rows reproduce the proved binary problem.  Replay the three surviving binary
faces after substituting costs `(x,y,y)`.

## Prospective holdouts

Evaluate points on both sides of, and exactly on, `x=y` and `x=3y`, including
large coprime pairs.  Holdouts are declared here and must not be changed after
implementation:

```text
(1,79), (39,40), (1,1), (41,40), (2,1), (3,1),
(121,40), (79,1), (5,7), (11,3), (13,17), (29,11)
```

## Independent audit

An audit with zero imports from `theorica` must independently:

1. reconstruct the projection and all six ray inequalities;
2. recompute every holdout value directly from the three affine faces;
3. replay the exact unit-cost boundary (depth eight infeasible, depth nine
   feasible) using the existing independent solver;
4. verify deterministic byte-for-byte regeneration of primary and audit JSON.

## Claim boundary

Success proves only arity three, depth three, costs `(x,y,y)` for positive
integer `x,y`, four copies, one substitution, one recognized erasure, and a
middle-first initial action.  It does not prove arbitrary ternary costs,
unrestricted first actions, higher arity, deeper trees, or other fault models.
