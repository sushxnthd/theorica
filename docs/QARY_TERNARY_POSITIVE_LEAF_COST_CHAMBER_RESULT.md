# Positive leaf-cost chamber conjecture falsified by query necessity

## Frozen claim and outcome

The preregistered claim asserted that at fixed `(a,b)=(4,11)`, the exact P2
and P0 residual values would remain 33 and 37 for every real leaf cost
`c>=1`.  The lower-endpoint predictions passed:

- P2 at `c=1`: exact lower and constructive upper bounds are both 33;
- P0 at `c=1`: exact lower and constructive upper bounds are both 37;
- the P0/P2 endpoint gap remains `a=4`.

The universal chamber claim nevertheless fails.  Exact synthesis with every
leaf query forbidden is infeasible for both families.  Thus no winning policy
can remain entirely within root and middle queries.

## Impossibility mechanism

Every winning policy must contain a reachable branch using at least one leaf
query.  The adversarial worst-case cost of any policy is therefore at least
`c`, so

`V_P2(c) >= c` and `V_P0(c) >= c`.

Consequently the constant formulas must fail for `c>33` in P2 and `c>37` in
P0.  This is a structural counterexample to the unbounded chamber, not a
failure of the two finite rays already established.  The earlier values at
`c=1` and `c=2` remain exact; they simply lie inside a bounded, still-unknown
leaf-cost chamber.

## Exact certificates

At `c=1`, P2 solves 4,537 states and 3,291 actions.  Clean middle group 3 is
optimal at 33, while the closest leaf actions cost 34.  P0 solves 5,392 states
and 4,571 actions; root group 0 and middle group 3 tie at 37, while leaf
actions cost 38.

When only levels 0 and 1 are allowed, exhaustive dynamic programming visits
197 states and 119 actions for P2 and 208 states and 151 actions for P0, with
no finite winning policy in either case.  The zero-production-import audit
replays the endpoint formulas, structural separator split, leaf-free
infeasibility, derived counterexample thresholds, four-unit gap, and reserved
case accounting.

## Scope and next experiment

This proves leaf-query necessity only at the frozen witness state for P0 and
P2.  It does not locate the first finite `c` where either formula changes, nor
give the replacement piecewise-linear branch.  The next decisive experiment
should derive and freeze that first breakpoint rather than sampling another
arbitrary ray.  Six cumulative family/cost cases are open; 12 remain sealed.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_ternary_positive_leaf_cost_chamber.py
PYTHONPATH=src python scripts/audit_qary_ternary_positive_leaf_cost_chamber.py
```
