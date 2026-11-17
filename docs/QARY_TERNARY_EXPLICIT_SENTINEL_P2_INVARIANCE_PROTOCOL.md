# Frozen protocol: explicit-sentinel P2 boundary invariance

## Question

The explicit outside-prefix token moved P0's first positive integer leaf-cost
breakpoint from 19 to 23.  This experiment asks whether that four-unit gain is
universal or depends on the algebraic separator mechanism.

P2 is the non-isomorphic ten-word family

`{0,1}^3 union {(2,1,0),(2,2,0)}`.

At the fixed witness state and costs `(a,b)=(4,11)`, the old aliased encoding
has a clean middle separator at query group 3 and first breakpoint 8.

## Structural prediction frozen before exact enumeration

Replacing the outside response by `-1` changes P2's group-3 row only by
relabeling its outside cell:

- aliased row: eight outside candidates answer `0`, followed by `1,2`;
- sentinel row: the same candidates answer `-1`, followed by `1,2`.

Thus the clean separator partition itself is unchanged.  Predict that the
sentinel leaves P2's boundary unchanged:

| leaf cost | exact value | unique optimal group | ordered children |
| ---: | ---: | ---: | --- |
| 7 | 33 | 3 | `[22,22,22]` |
| 8 | 34 | 3 | `[23,22,22]` |

The candidate branch remains `max(33,26+c)`, so monotonicity and the certified
`c=1` anchor imply a constant chamber through 7 if both endpoints pass.

## Prospective unseen-family covariance check

Apply the all-coordinate alphabet involution `0<->2` to P2 while keeping the
outside token fixed.  This target family has not been enumerated under the
explicit-sentinel model.  The covariance theorem predicts:

- an edge-checked level-preserving incidence isomorphism;
- identical exact values and search counts at `c=7,8`;
- transport of the unique optimal middle query from source group 3 (prefix 2)
  to target group 1 (prefix 0);
- target ordered children `[22,22,22]` and `[23,22,22]`.

## Falsification criteria

Preserve the result as negative evidence if any endpoint value, unique root,
ordered child vector, search count, or structural map differs.  In particular,
any breakpoint later than 8 falsifies mechanism-selective invariance, while a
failure of target transport falsifies the claimed unseen-family consequence of
the explicit-sentinel covariance theorem.

## Verification

Run production exact enumeration for the four source/target endpoints.  A
separate zero-production-import audit must reconstruct root minima, endpoint
signatures, the monotonicity implication, and the coordinate map from emitted
artifacts.  Record raw JSON, deterministic hashes, targeted tests, lint, and the
complete regression suite.

## Limits

This protocol is bounded to P2, its `0<->2` image, positive integer leaf costs,
the fixed witness state, explicit outside token, and `(a,b)=(4,11)`.  Passing
does not prove that every family is invariant to response refinement or that
the displayed affine branch remains optimal beyond the tested transition.
