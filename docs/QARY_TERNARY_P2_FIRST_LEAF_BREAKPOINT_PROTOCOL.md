# Frozen P2 first integer leaf-cost breakpoint

## Status

Frozen before opening either endpoint.  At fixed `(a,b)=(4,11)`, P2 has
exact value 33 at `c=1` and `c=2`.  The `c=1` clean middle action has child
values `[16,22,22]`; the only leaf-cost-sensitive child rose to 17 at `c=2`.
This experiment tests the resulting prospective breakpoint rather than
sampling another arbitrary ray.

## Frozen prospective claim

Open exactly two P2 family/cost cases:

- at `c=7`, exact value remains 33, clean middle query group 3 is optimal,
  and its child values are `[22,22,22]`;
- at `c=8`, exact value becomes 34, clean middle query group 3 remains
  optimal, and its child values are `[23,22,22]`.

Equivalently, the tested root-action branch is `max(33,26+c)` at the two
boundary integers.  Since exact value is monotone nondecreasing in `c`, a
value of 33 at `c=7`, together with the already certified `c=1` value, proves
that every integer `1<=c<=7` has value 33.  A value of 34 at `c=8` then makes
8 the first integer breakpoint.

Any different exact value, child vector, optimality result, or clean-separator
classification falsifies this prediction and must be preserved.  No P0 case
or other cost point may be opened in this run.  Two cases are opened, leaving
10 reserved cases sealed.

## Required audit

Emit full root-action tables and exact state/action counts at both endpoints.
A zero-production-import audit must recompute the frozen branch values,
critical-child crossing, clean-separator classification, monotonic first-
integer-breakpoint inference, and reserved-case count from the artifact alone.
