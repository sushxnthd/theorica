# Frozen protocol: explicit-sentinel P2 second breakpoint

## Motivation

The frozen `c=11,12` experiment confirmed a four-way collision at 11 but
falsified the predicted reversal at 12.  Group 0 remains optimal with value 37.
Its ordered child values change from `[22,22,33]` to `[23,23,33]`, showing that
the apparent saturation still depends on leaf-cost-sensitive subproblems.

This protocol is frozen before opening either new endpoint.  It tests the next
predicted policy boundary instead of extrapolating the temporary plateau to
all larger costs.

## Candidate mechanism

At the root action, two children advance as `11+c` while the third remains 33.
The resulting candidate action is

`4 + max(11+c,33) = max(37,15+c)`.

It is flat through `c=22` and first rises at `c=23`.  Combined with the exact
low-cost branch `4+3c` through `c=10`, this predicts the bounded chamber law

- `V=4+3c` for positive integers `1<=c<=10`;
- `V=37` for integers `11<=c<=22`;
- `V=38` at `c=23`.

## Frozen endpoint predictions

For the explicit-sentinel P2 source witness at `(a,b)=(4,11)`:

| leaf cost | exact value | optimal groups | group-0 children |
| ---: | ---: | --- | --- |
| 22 | 37 | `[0]` | `[33,33,33]` |
| 23 | 38 | `[0]` | `[34,34,33]` |

Thus 23 is predicted to be the first integer increase after the `c=11`
collision.

## Prospective unseen-family transport

Apply the all-coordinate involution `0<->1` with the outside token fixed.  This
family has not been opened at `c=22,23`.  Predict identical values, unique root
group 0, transported child multisets, and identical state/action/compatibility
counts at both endpoints.

## Decision rule

The second-breakpoint mechanism is supported only if both source endpoint
values, unique optima, ordered root children, exact bound equalities, unseen
transport, and search-count equalities pass.  Any mismatch is retained as a
falsification.  Passing proves the bounded integer chamber only through 23; it
does not establish behavior for real-valued costs or integers above 23.

## Independent verification

Run the production exact enumerator on the four source/target endpoint cases.
A separate zero-production-import audit must reconstruct root minima, the
monotonicity argument, the first post-collision increase, query transport, and
deterministic hashes.  Run targeted lint and the full regression suite.  Keep
the PR draft and unmerged.
