# Frozen protocol: ternary equal-ancestor-cost theorem

Status: frozen before cone replay, independent verification, and API promotion.

## Hypothesis

For ternary depth-three prefixes with root and middle query cost `x`, leaf cost
`y`, four physical copies per prefix, one substitution, one recognized erasure,
and a middle-level first query, the exact value is predicted to be

```text
T_3(x,y) = max(7x+y, 6x+3y, 5x+4y).
```

The phase boundaries are `x=2y` and `x=y`, as in the binary slice.

## Decisive certificate

Scalar agreement is not sufficient.  A ternary adaptive policy must satisfy
the transcript-exposure budgets on the complete extreme-ray set

```text
(1,0), (2,1), (1,1), (0,1).
```

Those rays define the three closed cost cones.  A policy meeting the active
face on both rays of each cone proves the upper envelope everywhere by
linearity.  The matching lower envelope must be justified by an exact binary
embedding into the ternary completion family.

## Frozen tests

- Replay every terminal transcript of the ternary unit-cost policy.
- Verify all six face/ray inequalities for the three cones.
- Open prospective asymmetric `(x,y)` holdouts only after the cone certificate
  is fixed.
- Independently reconstruct the prefix-query rows, exact depth boundary, face
  comparisons, phase coverage, and exposure inequalities with zero THEORICA
  imports.
- Require deterministic artifacts, full regression, and hosted workflow
  integration.

## Kill conditions

Retain a negative result and do not promote the theorem if any ray inequality
fails, any prospective exact optimum differs from the envelope, depth eight is
independently feasible, depth nine is independently infeasible, or the audit
disagrees.

## Claim boundary

Success covers only arity three, depth three, equal root/middle costs, positive
integer costs, four copies, one substitution, one recognized erasure, and a
middle-first initial action.  It does not prove arbitrary ternary cost triples,
all arities, unrestricted first actions, deeper trees, other fault budgets, or
arbitrary query families.
