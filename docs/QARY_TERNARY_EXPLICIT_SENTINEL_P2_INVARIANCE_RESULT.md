# Explicit response refinement does not preserve P2's boundary

## Frozen prediction falsified

The protocol predicted that replacing the aliased outside response with a
separate sentinel would leave P2's old breakpoint behavior unchanged.  Exact
enumeration falsified that prediction at both frozen endpoints:

| leaf cost | predicted value | observed value | observed optimal groups |
| ---: | ---: | ---: | --- |
| 7 | 33 | 25 | `[0,11,12]` |
| 8 | 34 | 28 | `[0,11,12]` |

Each sentinel solve enumerated 20,085 Bellman states, evaluated 15,794 actions,
and certified 95 compatibility states.  The clean middle separator at group 3
remains structurally present, but is no longer optimal at either endpoint.

## Mechanism discovered after falsification

A clearly labeled exploratory sweep over all positive integer costs `1<=c<=8`
found the exact law

`V_explicit,P2(4,11,c)=4+3c`.

The sentinel therefore eliminates P2's old constant value-33 chamber rather
than extending it.  At `c=1`, the value drops from 33 under the aliased model to
7 under the sentinel model.  At `c=7,8`, root group 0 ties two leaf queries;
the exact policies use the newly separated response cells instead of the old
clean-middle mechanism.

This is a stronger negative result than a shifted breakpoint: response
refinement can reverse which algebraic mechanism controls planning and replace
a constant chamber by a cost-sensitive branch.

## Unseen-family theorem check still passes

The all-coordinate `0<->2` image of P2 was opened prospectively.  Its values,
search counts, and transported optimal sets matched exactly:

- source optimal groups `[0,11,12]` map to target `[0,4,5]`;
- values are 25 and 28 at `c=7,8`;
- the structural map sends middle group 3 to group 1;
- all state, action, and compatibility counts agree.

Thus the explicit-sentinel alphabet-covariance theorem survives, while the
separate claim that response refinement preserves boundaries is falsified.

## Independent verification

- A zero-production-import replay reconstructed both source and target root
  minima, the transported optimal sets, the query map, and all search counts.
- Deterministic SHA-256:
  - results: `c1d6c0833dabeefe269c55fff57d285babe15f6b932a86d307183472687a946b`;
  - audit: `9d1b6b1865d8c4311757bc155a022e045b9add6d2f302aa8fcf93eb51f914bda`.
- Targeted lint passed and the complete regression suite passed 332/332 tests.

## Product consequence

Encoding outside-prefix as a distinct observation is not merely a symmetry
repair.  Exact planners must be recalibrated from scratch: in P0 it delays the
first increase, whereas in P2 it exposes much cheaper leaf-sensitive policies
and destroys the old plateau.  Reusing either values or policy thresholds from
the aliased model is unsafe even when a familiar separator remains visible.

## Limits

The prospective result covers only P2, its `0<->2` image, the frozen witness
state, `c=7,8`, and fixed `(a,b)=(4,11)`.  The `1<=c<=8` law is exploratory,
not prospectively confirmed beyond the frozen endpoints.  Its next policy
collision and validity beyond eight require a new frozen experiment.
