# Exact two-level fault-budget insurance law

## Theorem

Fix `q >= 2`. Index `q^2` pairwise-incompatible exact decisions by two-symbol
q-ary words. Give the root query cost `a`, every child-prefix query cost `b`,
and expose four physical copies of each query. Against one adversarial answer
substitution and one recognized erasure, the exact adaptive minimax cost is

`C_q(a,b) = max(2a + 4b, 3a + 3b, 4a + b)`.

Thus the phase diagram is

- `2a + 4b` for `a <= b`;
- `3a + 3b` for `b <= a <= 2b`;
- `4a + b` for `a >= 2b`.

The value is independent of `q`. Arity increases the completion set and the
fixed-schedule burden, but not the adaptive worst-path cost.

## Proof

Query the root until one non-erased symbol appears twice. Two equal answers
identify the root because at most one can be substituted. If neither fault was
observed this costs `2a`, after which the child still needs four copies. If an
erasure was observed it costs `3a`, after which the child is a one-substitution
repetition problem needing three copies. A visible conflicting answer without
an erasure leaves only an erasure and costs no more than the displayed bound.
If both a conflict and erasure were observed, four root copies identify the
root and both budgets are exhausted, so one child query suffices. This policy
costs at most the maximum of the three affine terms.

For the reverse inequality, before the root is forced an adversary answers any
child-prefix query with zero while retaining suffix-zero completions in at
least two root classes. Such a query cannot reduce root ambiguity; charging it
only strengthens the lower bound. The adversary may therefore realize each of
three root transcripts:

1. two matching truthful answers, preserving both faults for the child;
2. one erasure followed by two matching truthful answers, preserving the
   substitution for the child;
3. one erasure, one conflicting substituted answer, and two matching truthful
   answers, exhausting both faults at the root.

The remaining child problems require respectively four, three, and one query
copies by exact error-erasure repetition distance. These transcripts force
`2a+4b`, `3a+3b`, and `4a+b`; hence their maximum is a lower bound and matches
the policy above.

## Prospective exact evidence

All three opened calibrations and all five frozen holdouts matched exactly.

| `q` | `(a,b)` | regime | predicted = exact |
| ---: | ---: | --- | ---: |
| 3 | `(2,7)` | child expensive | 32 |
| 4 | `(5,3)` | intermediate | 24 |
| 5 | `(9,4)` | root expensive | 40 |
| 3 | `(6,6)` | `a=b` boundary | 36 |
| 4 | `(8,4)` | `a=2b` boundary | 36 |

The independent solver reconstructed every physical query and reproduced 8/8
optima without importing THEORICA. Deleting one required child-query copy made
the `(q,a,b)=(3,2,7)` family unidentifiable, and both implementations abstained.

The strongest prospective adaptive-versus-fixed separation is 32 versus the
fixed child-query lower bound 84 for `(3,2,7)`, saving at least 52 worst-case
cost units. The executable certificate reports the three adversarial lower
bounds, their maximum, and the active cost regime.

## Reproduction

```bash
python scripts/verify_qary_two_level_insurance.py
python scripts/audit_qary_two_level_insurance.py
pytest -q tests/test_corruption_resilient_features.py
```

Raw deterministic evidence is under `results/qary_two_level_insurance/`.

## Limits and novelty boundary

The theorem is restricted to two-level prefix-query families, one global
substitution, one recognized erasure, four copies per query, positive integer
costs, and finite exact decisions. It is not a general weighted liar-game
capacity result. Its contribution is the sharp three-phase law, the identified
fault-budget-insurance mechanism, executable exact policy selection, and
independently replayed prospective nonbinary evidence.
