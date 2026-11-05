# Exact arbitrary-depth root-respecting insurance law

## Theorem

For q-ary prefix queries at depth `d`, four physical copies per prefix, positive
integer level costs `c=(c_1,...,c_d)`, one adversarial substitution, and one
recognized erasure, the exact minimax cost over the complete root-respecting
policy class is independent of `q >= 2`.

A root-respecting policy resolves the current prefix symbol before querying a
strict descendant. Define `H`, `G`, and `F` as the continuation costs with no
faults, one substitution, and one substitution plus one erasure remaining:

```text
H_1(c_1) = c_1
G_1(c_1) = 3c_1
F_1(c_1) = 4c_1

H_d(c) = c_1 + H_{d-1}(c_2,...,c_d)
G_d(c) = max(2c_1 + G_{d-1}, 3c_1 + H_{d-1})
F_d(c) = max(2c_1 + F_{d-1}, 3c_1 + G_{d-1}, 4c_1 + H_{d-1}).
```

Equivalently, `F_d` is the maximum of exactly `d(d+1)/2` affine faces whose
coefficient vectors are

```text
(2^r, 4, 1^(d-r-1))
(2^r, 3, 2^s, 3, 1^(d-r-s-2)).
```

## Proof

With no remaining fault, one query identifies the current symbol and the policy
recurses, giving `H_d`.

With one substitution remaining, two equal answers identify the symbol while
leaving the substitution hidden. A disagreement forces a third answer, exposes
the substitution, and leaves a fault-free suffix. These two adversarial
branches give `G_d`.

With one substitution and one erasure, two equal non-erased answers leave both
budgets hidden; an observed erasure can force a third answer while leaving the
substitution; and a conflict plus erasure can force a fourth answer while
exhausting both budgets. The corresponding continuations give `F_d`. A branch
that exposes the substitution before the erasure is no worse than the displayed
erasure-first branch for positive costs, so it adds no face.

Induction expands the recurrence into two exhaustive transcript families. If
both faults are exposed at one level, the path has coefficients
`(2^r,4,1^*)`. If they are exposed at separate levels, it has
`(2^r,3,2^s,3,1^*)`. The adversary realizes every such path, establishing all
lower bounds; the repetition policy attains their maximum, establishing the
upper bound. Counting gives `d + d(d-1)/2 = d(d+1)/2` faces.

This also explains the previous results. At depth two the three faces are the
complete unrestricted law. At depth three these are six of the seven
unrestricted faces; `(0,4,2)` is precisely an ancestor-bypass policy excluded
by root-respecting order.

## Prospective and exhaustive evidence

| Arity | Depth | Costs | Faces | Exact cost |
|---:|---:|---|---:|---:|
| 2 | 4 | `(3,1,4,2)` | 10 | 26 |
| 3 | 4 | `(2,5,1,3)` | 10 | 30 |
| 5 | 5 | `(1,3,2,7,1)` | 15 | 41 |
| 2 | 6 | `(6,1,2,1,3,2)` | 21 | 38 |
| 3 | 8 | `(1,2,3,4,5,6,7,8)` | 36 | 88 |

- All 5/5 frozen holdouts matched the recurrence and explicit face maximum.
- All 1,092 positive cost vectors through depth six with costs in `{1,2,3}`
  matched exactly.
- An independent standard-library implementation reproduced every holdout,
  all 1,092 exhaustive cases, the face counts, and the evidence digest with
  zero THEORICA imports.
- Removing one physical copy at any level caused the certificate to abstain.
- Two opened unrestricted depth-four calibrations matched: uniform costs had
  cost 10; `(1,1,1,20)` had cost 86 with active path `(2,2,2,4)`.

The unrestricted depth-four calibrations `(20,1,1,1)`, `(1,20,1,1)`, and
`(1,1,20,1)` exceeded a 240-second cap and remain explicit negative
computational results.

## Reproduction

```bash
python scripts/verify_qary_root_respecting_insurance.py
python scripts/audit_qary_root_respecting_insurance.py
pytest -q tests/test_corruption_resilient_features.py
```

Raw deterministic evidence is under `results/qary_root_respecting_insurance/`.

## Scope and limitation

This theorem is exact for the root-respecting class, not all adaptive prefix
policies. Ancestor bypass can improve the unrestricted optimum and remains the
central open mechanism at depth four and beyond. The theorem does not address
larger fault budgets, arbitrary query libraries, or general liar-game capacity.
