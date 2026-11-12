# Frozen protocol: explicit-sentinel P2 policy reversal at c=11,12

## Motivation

The prospectively frozen invariance test was falsified: with a distinguished
outside token, P2 has exact values 25 and 28 at leaf costs 7 and 8 instead of
the aliased model's 33 and 34.  A labeled post-falsification sweep found the
source-family law

`V(4,11,c)=4+3c`

at every integer `1<=c<=8`.  The old clean middle separator remains
available but loses optimality at the frozen endpoints.

This protocol is frozen before opening either new endpoint.  It tests the next
mechanistic event rather than extending the exploratory law uncritically.

## Candidate branches

The emitted exact actions at `c=7,8` identify two affine candidates:

1. root/leaf branch `4+3c`;
2. clean-middle branch `15+2c`.

They collide exactly at `c=11`.  The clean-middle branch is smaller at
`c=12`.  This predicts a policy reversal relative to the old aliased model,
where group 3 ties group 0 at 11 but group 0 becomes uniquely optimal at 12.

## Frozen endpoint predictions

For source P2 under the explicit outside token:

| c | exact value | optimal groups | group-0 children | group-3 children | group-11 children |
| ---: | ---: | --- | --- | --- | --- |
| 11 | 37 | `[0,3,11,12]` | `[22,22,33]` | `[26,22,22]` | `[26,22]` |
| 12 | 39 | `[3]` | `[23,23,36]` | `[28,24,24]` | `[28,24]` |

Thus the sentinel model is predicted to hand off *toward* the clean middle
query at 12, the opposite direction from the aliased model.

## Prospective unseen-family transport

Apply the all-coordinate involution `0<->2` with the outside token fixed.
The already certified query map sends source groups `0,3,11,12` to target
groups `0,1,5,4`.  Predict:

- target optimal groups `[0,1,4,5]` at `c=11`;
- target unique optimal group `[1]` at `c=12`;
- identical exact values, transported child signatures, and identical
  state/action/compatibility counts.

## Decision rule

The replacement mechanism is supported only if all source endpoint values,
optimal sets, nominated child vectors, target transports, exact bound
equalities, and search-count equalities pass.  Any mismatch is preserved as a
falsification.  No claim about real-valued costs or costs beyond 12 is made.

## Required verification

Run the production exact enumerator on four source/target endpoint cases.  A
separate zero-production-import audit must reconstruct root minima, the affine
collision, the direction of the handoff, query transport, and deterministic
hashes.  Run targeted lint and the full regression suite.  Keep the PR draft
and unmerged.

## Limits

This protocol is bounded to the frozen P2 witness, its `0<->2` image,
positive integer leaf costs, the explicit outside token, and fixed
`(a,b)=(4,11)`.  Passing would certify an executable two-endpoint policy
consequence, not a universal response-refinement theorem.
