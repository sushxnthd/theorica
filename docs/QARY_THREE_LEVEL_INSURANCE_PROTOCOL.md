# Frozen protocol: three-level fault-budget insurance law

Status: frozen before implementation and before prospective enumeration.
Parent commit: `ff0c0db7ae51937f1be7c79f39404aee4c97318e`.

## Candidate theorem

Fix `q >= 2`. Index `q^3` pairwise-incompatible exact robust decisions by
three-symbol q-ary words. Expose four physical copies of every prefix query,
with positive integer level costs `a`, `b`, and `c`. Allow one adversarial
answer substitution and one recognized erasure globally.

The candidate exact adaptive minimax cost is

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

The prediction is independent of `q`. Unlike the two-level result, the
three-level law is not a function of only the sum and largest cost; it has
seven insurance faces and includes the bypass certificate `4b + 2c`.

## Opened calibration

The candidate was inferred from exact enumeration of the complete binary grid
`1 <= a,b,c <= 5` (125 cases). Every value was reproduced by the maximum of
the seven displayed integer affine forms. Two ternary probes completed before
freezing: `(q,a,b,c)=(3,1,1,1)` had exact cost 8 and `(3,1,1,5)` had exact cost
24, both matching the candidate.

The ternary probes `(3,1,5,1)` and `(3,5,1,1)` exceeded a 120-second cap before
freezing. They remain explicitly unresolved and are not counted as evidence.

## Prospective holdouts

The following cases are frozen without opening their exact values:

- binary extrapolations: `(2,1,7,2)`, `(2,7,2,1)`, `(2,2,1,7)`;
- binary cross-regime cases: `(2,3,6,2)`, `(2,6,3,2)`, `(2,2,4,5)`;
- ternary holdouts: `(3,2,2,2)` and `(3,1,2,3)`.

Each completed holdout must match the formula exactly. The ternary mixed-cost
case has a 180-second cap and remains unresolved if it exceeds that cap.

## Proof and executable obligations

Success requires:

1. an executable certificate returning all seven adversarial lower bounds and
   their maximum;
2. exact production-planner agreement on every completed holdout;
3. an independent standard-library solver with zero THEORICA imports;
4. conservative abstention after deletion of one necessary leaf-parent query
   copy;
5. full regression, lint, deterministic rerun, and hosted workflow evidence.

Any mismatch falsifies the candidate and must be preserved. A merely fitted
regression without lower-bound and policy interpretations is failure.

## Bounded novelty claim

Adversarial decision trees and repetition codes are classical. The bounded
claim sought here is the sharp seven-face weighted law for this depth-three
prefix family, its fault-budget-insurance interpretation, and an executable
policy/lower-bound certificate. It is not a general weighted liar-game
capacity theorem and makes no claim beyond one substitution, one recognized
erasure, positive integer costs, and finite exact decision families.
