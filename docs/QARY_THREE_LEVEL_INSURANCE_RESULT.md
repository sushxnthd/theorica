# Exact three-level fault-budget insurance law

> **Retracted on 2026-10-27.** The seven-face unrestricted theorem below is
> false. Its alleged `4b+2c` lower face can exceed the cost of a feasible
> root-respecting policy, violating minimax monotonicity. The exact violation
> cone is `c > 2a` and `b > 2a+c`. See
> [QARY_THREE_LEVEL_MONOTONICITY_CORRECTION_RESULT.md](QARY_THREE_LEVEL_MONOTONICITY_CORRECTION_RESULT.md)
> for the proof, prospective counterexamples, independent audit, and bounded
> replacement claim. The original text is retained below as a falsified
> historical result; it must not be cited as a theorem.

## Theorem

For the depth-three q-ary prefix-query family with four physical copies of
every prefix query, positive integer level costs `(a,b,c)`, one adversarial
answer substitution, and one recognized erasure, the exact adaptive minimax
cost is independent of `q >= 2` and equals

```text
C_q(a,b,c) = max(
    4b + 2c,
    2a + 2b + 4c,
    2a + 3b + 3c,
    2a + 4b + c,
    3a + 2b + 3c,
    3a + 3b + c,
    4a + b + c,
).
```

The seven affine faces are the possible worst transcript classes after
quotienting by the remaining global substitution and erasure budgets. They
include a root-bypass certificate `4b+2c`, plus paths on which the faults remain
hidden or become exposed at different levels.

## Proof structure

At each prefix, the policy state is determined by the feasible completions,
the per-completion disagreement counts, the erasure flag, and unused physical
queries. Symmetry collapses q sibling subtrees to the same continuation value.
Conditioning on whether the first observable conflict/erasure occurs at the
root, middle, or leaf level leaves seven non-dominated path-count vectors:

```text
(0,4,2), (2,2,4), (2,3,3), (2,4,1),
(3,2,3), (3,3,1), (4,1,1).
```

An adversary can retain incompatible completions along each vector, giving the
seven lower bounds. Conversely, the recursive policy queries until a conflict
or erasure certifies expenditure of a global fault; it then descends using the
corresponding reduced-budget continuation. The same seven vectors exhaust the
continuations, so the maximum lower bound is attained. Arity changes the number
of sibling subtrees and the nonadaptive burden, but symmetry leaves every
realized adaptive path unchanged.

The executable certificate exposes all seven bounds and their active faces.
The exact planner independently synthesizes the matching policy from the raw
query library rather than using the formula.

## Evidence

- 125/125 opened binary calibration cases matched for `1 <= a,b,c <= 5`.
- 8/8 frozen prospective holdouts matched exactly.
- Both binary and ternary families matched.
- Six of seven faces were activated by the prospective set; all seven were
  necessary on the opened grid.
- An independent standard-library solver reproduced 8/8 optima with zero
  THEORICA imports.
- Deleting one necessary leaf-parent copy made identification impossible, and
  both solvers abstained.
- The strongest prospective separation was ternary `(1,2,3)`: adaptive cost
  18 versus 136 for the complete nonadaptive four-copy prefix schedule.

Two pre-freeze ternary extremes, `(3,1,5,1)` and `(3,5,1,1)`, exceeded the
120-second calibration cap and remain explicitly unresolved. They are not
silently counted as matches.

## Reproduction

```bash
python scripts/verify_qary_three_level_insurance.py
python scripts/audit_qary_three_level_insurance.py
pytest -q tests/test_corruption_resilient_features.py
```

Raw deterministic evidence is under `results/qary_three_level_insurance/`.

## Scope

This is a theorem for the stated finite depth-three prefix-query construction,
one substitution, one recognized erasure, four physical copies, and positive
integer costs. It is not a general weighted liar-game capacity theorem. The
result supplies an exact executable policy cost and impossibility boundary for
this family; it does not claim that the seven-face form persists at depth four
or for larger fault budgets.
