# Counterexample-guided policy columns: prospective falsification

## Result

Counterexample-guided policy column generation repaired the complete opened
calibration record, then failed on its first prospective transfer case.

The initial discovery fans contained 34, 34, and 33 policy exposure
antichains.  Ordered separation over the 181 already-opened cases added exactly
one new column to the first obstruction family.  Its seven terminal-exposure
extremes are:

```text
(1,5,1) (3,3,5) (3,4,3) (3,5,0) (4,2,2) (4,3,1) (4,4,0)
```

That column closes the known `(2,9,3)` gap for the first pair and yields
181/181 calibration agreement.  The resulting frozen 102-column system was
then used to preregister 20 untouched pair/cost predictions.

The very first prospective case, the second obstruction pair
`{(2,0,0),(2,2,0)}` at `(2,9,3)`, falsified transfer:

| Quantity | Cost |
|---|---:|
| Frozen column-fan prediction | 52 |
| Exact production optimum | **51** |
| Independent optimum | **51** |

The experiment stopped immediately.  The remaining 19 cases stay unopened,
and the new prospective policy was not added to the fan.

## Verification

- calibration closure: **181/181**;
- calibration columns added: **1**;
- column synthesis states: **43,623**;
- prospective cases run: **1/20**;
- production states for the counterexample: **34,323**;
- independent standard-library solver: feasible at 51 and infeasible at 50;
- independent verifier imports zero THEORICA modules;
- frozen prediction snapshot contains all 20 pre-execution predictions.

## Scientific consequence and kernel decision

The frozen pair-local fan does not transfer the repair to the next obstruction
pair at the same cost vector and exact value.  The subsequent
partition-hypergraph experiment shows that this is a missing orbit-closure
step, not a genuinely family-specific policy: the first two query systems are
isomorphic and the exact policy transports between them.  Thus this result
rules out the frozen pair-local update rule, while the stronger original
interpretation is explicitly superseded.

This is the third consecutive falsification of the minimal-obstruction global
cost-fan program.  That kernel is terminated rather than patched.  The next
active THEORICA kernel is the **algebraic obstruction-pair transfer boundary**:
characterize exactly which completion-family relabelings induce policy-tree
equivalence, which preserve only scalar optima, and which require distinct
exposure antichains.  This moves from fitting a global cost law to proving an
identifiability/equivalence theorem about algebraic family structure.

## Scope and limitations

The result is bounded to the specified depth-three ternary, four-copy,
one-substitution, one-recognized-erasure, middle-first problem.  It does not
prove that the second pair lacks a 51-cost column; exact feasibility proves
that such a policy exists.  It proves that the frozen first-family repair and
all discovery columns fail to provide it.  Nineteen prospective cases remain
reserved for the new transfer-boundary kernel.
