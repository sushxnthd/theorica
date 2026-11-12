# Frozen protocol: two-level fault-budget insurance law

Status: frozen before implementation and before prospective enumeration.

## Candidate theorem

Fix `q >= 2`. Index `q^2` pairwise-incompatible exact robust decisions by
two-symbol q-ary words. Expose four physical copies of the root query and four
copies of every child-prefix query, with positive integer costs `a` and `b`
respectively. Allow one adversarial answer substitution and one recognized
erasure globally.

The candidate exact adaptive minimax cost is

`C_q(a,b) = max(2a + 4b, 3a + 3b, 4a + b)`.

Equivalently, the three cost regimes are:

- `2a + 4b` when `a <= b`;
- `3a + 3b` when `b <= a <= 2b`;
- `4a + b` when `a >= 2b`.

The prediction is independent of `q`; arity changes the number of possible
decisions and the fixed-schedule burden, but not the worst-path adaptive cost.

## Mechanism and proof obligation

The three affine pieces are separate adversarial certificates. They represent
paths on which uncertainty is retained while faults are respectively preserved,
partly exposed, or fully exposed at the root. The upper-bound policy must price
the information gained from a conflict or erasure: observable fault expenditure
reduces the confirmations required at the child. A valid proof must establish
both a decision tree of cost at most the maximum of the three pieces and three
matching adversarial lower bounds. Merely fitting enumerated costs is failure.

## Frozen experiment

Opened calibration cases:

- `(q,a,b) = (2,1,1), (2,1,3), (2,3,1)`.

Prospective cases, untouched before the exact run:

- `(3,2,7)` in the child-expensive regime;
- `(4,5,3)` in the intermediate regime;
- `(5,9,4)` in the root-expensive regime;
- `(3,6,6)` on the first phase boundary;
- `(4,8,4)` on the second phase boundary.

An independent standard-library solver must reconstruct the physical query
library and reproduce every optimum without importing THEORICA. The production
planner must also abstain after deletion of one necessary child-query copy.

## Success and kill criteria

Success requires every opened and prospective optimum to match the formula,
valid exact certificates, exact independent replay, and conservative abstention
under the missing-copy attack. Any mismatch falsifies the candidate law and is
preserved. If the large-arity holdout exceeds the declared run cap, it remains
unresolved rather than being silently removed.

## Bounded novelty claim

Repetition codes, adversarial decision trees, and minimax recurrences are
classical. The bounded contribution would be the sharp three-phase weighted
law for this two-level algebraic prefix family, an executable policy and lower
certificate, and an explicit phase diagram for fault-budget insurance. It is
not a general weighted liar-game capacity theorem.
