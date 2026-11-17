# Frozen protocol: explicit-sentinel first leaf-cost breakpoint

UTC date: 2026-11-11

## Question

The explicit outside-prefix token restored alphabet covariance and falsified the
old P0 breakpoint at leaf cost 19. This experiment locates the replacement
first positive integer breakpoint at the same witness state and fixed
root/middle costs `(a,b)=(4,11)`.

## Derivation frozen before endpoint enumeration

The certified explicit-sentinel endpoints give root-group-0 children
`[29,29,33]` at `c=18` and `[30,30,33]` at `c=19`. The candidate local
branch is therefore

`group0_children(c) = [c+11,c+11,33]`

and the corresponding root action is

`4 + max(c+11,33) = max(37,c+15)`.

This predicts a constant chamber through `c=22` and the first increase at
`c=23`.

## Prospective endpoints

Open exactly two new source-family endpoints:

- `c=22`: exact value 37, unique root group 0, children `[33,33,33]`;
- `c=23`: exact value 38, unique root group 0, children `[34,34,33]`.

By monotonicity, if both predictions pass, the certified `c=1` value 37 and
the `c=22` endpoint establish `V(c)=37` for every positive integer
`1<=c<=22`, while `c=23` is the first breakpoint.

## Independent checks

A zero-production-import audit will reconstruct both root minima from emitted
actions, check exact lower/upper-bound equality, ordered children, uniqueness,
and the claimed monotonicity argument. Deterministic replay, targeted lint, and
the full regression suite are required.

## Falsifiers and limits

Any endpoint, child-vector, or optimizer mismatch falsifies the candidate
branch. A pass is bounded to this P0 witness state, positive integer leaf costs,
the explicit outside token, and fixed `(a,b)=(4,11)`. It does not prove the
branch after `c=23` or cover arbitrary families and states.
