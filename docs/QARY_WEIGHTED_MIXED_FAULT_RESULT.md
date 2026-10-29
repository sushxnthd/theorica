# Weighted q-ary mixed faults: falsification and replacement mechanism

## Decisive result

The frozen conjecture

`C_q(m;t,s;c) = (t+1) sum(c) + (t+s) max(c)`

is false. The exact weighted minimax planner found three counterexamples among
nine completed cases, including two frozen prospective holdouts. An independent
standard-library solver reproduced every optimum and the fail-closed attack.

| `q,m,t,s` | level costs | conjecture | exact optimum | gap |
| --- | --- | ---: | ---: | ---: |
| `2,3,1,2` | `(7,1,3)` | 43 | 39 | -4 |
| `4,2,2,1` | `(2,9)` | 60 | 58 | -2 |
| `2,3,1,1` | `(5,1,2)` | 26 | 23 | -3 |

The first two rows were frozen before implementation. The last row is the
cost-order falsification: the same multiset `(1,2,5)` costs 26 in increasing
order but 23 in order `(5,1,2)`. Therefore the optimum does not depend only on
`sum(c)` and `max(c)`.

## Why the proof failed

The unweighted prefix-dominance exchange is not cost preserving. More
importantly, forcing faults at one level can reveal that the global budgets are
exhausted. Later levels then need fewer confirmations. With costs `(5,1,2)` and
one substitution plus one erasure, one worst path spends four root queries and
observes a conflict and an erasure. That certifies both faults have been spent,
so the two remaining symbols need one query each:

`4*5 + 1 + 2 = 23`,

not the conjectured `2*(5+1+2) + 2*5 = 26`.

The `(2,9)` counterexample shows the complementary insurance mechanism: extra
cheap ancestor probes can reduce the number of expensive descendant probes.
The weighted optimum is therefore a dynamic allocation problem over both
remaining ambiguity and remaining fault budgets, rather than a static
concentration at the maximum-cost level.

## Executable replacement capability

`plan_adaptive_decision_queries_with_weighted_faults` accepts arbitrary
positive integer query costs and returns an exact minimum-cost robust decision
tree. It uses monotone cost-bounded search with integer binary search, records
the exact worst-case cost and depth, and abstains when the physical query
library is insufficient. Removing one required leaf-parent copy in the
`(3,2,1,1,(1,5))` family produced abstention.

The replacement research kernel is now **fault-budget insurance**: compress
the exact planner state into a recurrence that prices how a query both reduces
model ambiguity and reveals or consumes adversarial budget. A valid closed form
must retain cost order and branching structure. The falsified sum/max law is
not used as a bound except as the cost of its specific threshold policy.

## Evidence

- Nine exact cases completed; six matched and three falsified the conjecture.
- All nine optima were reproduced by a solver importing zero THEORICA modules.
- The independent audit reproduced the evidence digest.
- One frozen permutation holdout `(3,3,1,1,(5,1,2))` exceeded a 90-second exact
  search cap and remains explicitly unresolved; it is not counted as evidence.

## Reproduction

```bash
python scripts/verify_qary_weighted_mixed_fault_law.py
python scripts/audit_qary_weighted_mixed_fault_law.py
pytest -q tests/test_corruption_resilient_features.py
```

Raw deterministic evidence is under `results/qary_weighted_mixed_fault_law/`.

## Limits

The completed experiments use finite prefix-query families, global bounded
substitutions, recognized erasures, and positive integer costs. The exact
planner is exponential and one larger permutation hit the declared runtime
cap. No closed-form weighted theorem is claimed. The durable contribution of
this run is a prospective falsification, its independently reproduced
counterexamples, the identified budget-insurance mechanism, and an executable
exact policy synthesizer for bounded instances.
