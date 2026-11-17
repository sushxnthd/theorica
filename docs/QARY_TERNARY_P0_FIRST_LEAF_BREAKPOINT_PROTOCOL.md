# Frozen P0 first integer leaf-cost breakpoint

## Status

Frozen before opening either endpoint.  At fixed `(a,b)=(4,11)`, P0 has
exact value 37 at `c=1` and `c=2`.  Its root group-0 action has child vector
`[15+c,15+c,33]` at those opened points, yielding the candidate upper branch
`max(37,19+c)`.

## Frozen prospective claim

Open exactly two P0 family/cost cases:

- at `c=18`, exact value remains 37, root group 0 is optimal, and its child
  values are `[33,33,33]`;
- at `c=19`, exact value becomes 38, root group 0 is optimal, and its child
  values are `[34,34,33]`.

Together with the certified `c=1` value and cost monotonicity, these endpoints
would prove `V_P0(4,11,c)=37` for every integer `1<=c<=18` and make 19 the
first integer leaf-cost breakpoint.  The prediction is intentionally stronger
than the available upper bound: the `c=19` solve must rule out every alternative
policy of cost 37.

Any different exact value, child vector, or root-group optimality result
falsifies this prediction and must be preserved.  No P2 case or other cost
point may be opened in this run.  Two cases are opened, leaving six reserved
cases sealed.

## Required audit

Emit full root-action tables and exact state/action counts at both endpoints.
A zero-production-import audit must recompute the nominated root branch,
endpoint minima, monotonic first-breakpoint inference, and reserved-case count
from the artifact alone.
