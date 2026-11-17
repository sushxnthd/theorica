# Frozen clean-separator second-ray experiment

## Status

Frozen before opening the reserved case.  The first unseen ray `(3,10,3)`
supported the exact state-local boundary `3*b` for clean P2 and `a+3*b` for
non-clean P0.  This experiment changes both the root/leaf balance and the
middle cost rather than opening the remaining isomorphic P1 case.

## Frozen prospective claim

Open exactly one reserved family/cost case:

- family: P2 = `{0,1}^3 union {(2,1,0),(2,2,0)}`;
- level costs: `(a,b,c)=(4,11,2)`;
- state: the same post-erasure witness state, with eight cube completions at
  lie count one, two added completions at lie count zero, three remaining
  copies of query groups 0 and 1, and four copies of all other groups;
- structural prediction: middle query group 3 remains a clean separator;
- policy prediction: query group 3 is an optimal first continuation;
- numerical prediction: the exact residual value is `3*b = 33`.

The claim passes only if exact Bellman enumeration proves matching lower and
constructive upper bounds of 33 and retains query group 3 as optimal.  Any
other exact value, infeasibility, or loss of clean-separator optimality
falsifies the cross-ray law and must be preserved.  No other reserved case may
be opened in this run.  A pass leaves 15 reserved cases sealed.

## Required audit

Emit every root action and child-value vector, all clean-separator cells, and
exact state/action counts.  A zero-production-import audit must recompute the
separator property, `3*11`, Bellman root minimum, and reserved-case count from
the artifact alone.
