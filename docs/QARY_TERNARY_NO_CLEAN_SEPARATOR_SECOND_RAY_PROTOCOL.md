# Frozen no-clean-separator second-ray experiment

## Status

Frozen before opening the reserved case.  On level costs `(4,11,2)`, the
previously opened clean P2 family had exact residual value `3*b = 33`, with
middle query group 3 uniquely optimal.  This complementary experiment changes
only the algebraic family, so it tests the two-branch boundary without fitting
another cost ray after observing its outcome.

## Frozen prospective claim

Open exactly one reserved family/cost case:

- family: P0 = `{0,1}^3 union {(2,0,0),(2,1,1)}`;
- level costs: `(a,b,c)=(4,11,2)`;
- state: the same post-erasure witness state, with eight cube completions at
  lie count one, two added completions at lie count zero, three remaining
  copies of query groups 0 and 1, and four copies of all other groups;
- structural prediction: no remaining middle query is a clean separator;
- numerical prediction: the exact residual value is `a + 3*b = 37`;
- comparative prediction: the exact P0 minus P2 gap is `a = 4`.

The claim passes only if exact Bellman enumeration proves matching lower and
constructive upper bounds of 37, the emitted middle partitions contain no
clean separator, and the frozen gap to the prior P2 result is exactly 4.  Any
other exact value, infeasibility, clean separator, or gap falsifies this
cross-ray branch law and must be preserved.  No other reserved case may be
opened in this run.  A pass or falsification leaves 14 reserved cases sealed.

## Required audit

Emit every root action and child-value vector, every middle partition cell,
and exact state/action counts.  A zero-production-import audit must recompute
the no-clean-separator predicate, `4 + 3*11`, the Bellman root minimum, the
gap to the already committed P2 value, and the reserved-case count from the
artifact alone.
