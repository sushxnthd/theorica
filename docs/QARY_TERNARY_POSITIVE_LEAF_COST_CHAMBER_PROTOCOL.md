# Frozen positive-leaf-cost chamber experiment

## Status

Frozen before opening the `c=1` endpoint.  At `(a,b,c)=(4,11,2)`, the clean
P2 family has exact residual `3*b=33`, while non-clean P0 has exact residual
`a+3*b=37`.  This experiment seeks a theorem over a continuous cost chamber
rather than another isolated ray.

## Frozen prospective claim

At the same post-erasure witness state and fixed `(a,b)=(4,11)`, for every
real leaf-query cost `c >= 1`:

- P2 retains exact residual `3*b = 33`;
- P0 retains exact residual `a + 3*b = 37`;
- the exact P0 minus P2 gap remains `a = 4`.

Open only the previously unseen lower endpoint `c=1` for P2 and P0.  Predict
exact unrestricted values 33 and 37 respectively.  Independently compute a
constructive upper bound by restricting every continuation to root and middle
queries; predict the same values 33 and 37.

## Proof rule

For either family, query cost monotonicity gives `V(c) >= V(1)` for every
`c>=1`.  A root/middle-only policy has no leaf-cost dependence, so its exact
restricted value gives `V(c) <= U_RM` for every real `c`.  The chamber theorem
passes only if exact enumeration proves `V(1)=U_RM` at the predicted formula.
Any endpoint mismatch, missing leaf-free policy, or wrong gap falsifies the
claim and must be preserved.

Exactly two family/cost cases are opened.  A pass or falsification leaves 12
reserved cases sealed.

## Required audit

Emit complete endpoint and restricted root-action tables, exact state/action
counts, allowed query levels, structural separator classifications, and the
two sandwich bounds.  A zero-production-import audit must recompute the
formula values, monotonicity sandwich closure, family gap, structural branch,
and reserved-case count from the artifact alone.
