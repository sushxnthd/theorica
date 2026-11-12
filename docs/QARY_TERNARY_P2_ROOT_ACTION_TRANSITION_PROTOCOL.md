# Frozen P2 root-action transition at high leaf cost

## Status

Frozen before opening either endpoint.  At fixed `(a,b)=(4,11)`, the P2
clean middle query (group 3) has exact root-action value `max(33,26+c)` at
the certified boundary points `c=7,8`.  The nearest competing root query
(group 0) has value 37 there.  This experiment tests the predicted collision
and strict handoff rather than sampling another arbitrary cost.

## Frozen prospective claim

Open exactly two P2 family/cost cases:

- at `c=11`, the exact value is 37; clean group 3 and root group 0 tie as
  optimal actions.  Their child vectors are respectively `[26,22,22]` and
  `[26,26,33]`;
- at `c=12`, the exact value remains 37; root group 0 is uniquely optimal,
  with children `[27,27,33]`, while clean group 3 has value 38 and children
  `[27,22,22]`.

Thus the prospective mechanism is an action collision at `c=11` followed by
a strict root-action handoff at `c=12`.  The experiment does not assume that
these formulas extend to untested real costs or arbitrary states.

Any different exact value, child vector, optimizer set, or clean-separator
classification falsifies the prediction and must be preserved.  No P0 case
or other cost point may be opened in this run.  Two cases are opened, leaving
eight reserved cases sealed.

## Required audit

Emit full root-action tables and exact state/action counts at both endpoints.
A zero-production-import audit must recompute the two nominated action values,
their optimizer status, the tie-to-handoff transition, clean-separator
classification, and reserved-case count from the artifact alone.
