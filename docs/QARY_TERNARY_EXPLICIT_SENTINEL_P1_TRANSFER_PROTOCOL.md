# Frozen protocol: explicit-sentinel P1 transfer boundary

## Motivation

The explicit outside token changed the scalar boundary in opposite ways for
the previously opened P0 and P2 obstructions.  P1 has not been opened under
this encoding.  It is not a coordinatewise alphabet image of P0, so this is a
genuinely out-of-orbit test of whether the stronger partition-hypergraph
mechanism, rather than visible word labels, controls query complexity.

This protocol is frozen before opening any P1 endpoint.

## Structural prediction fixed before outcomes

With outside-prefix represented by the fixed token `-1`, the complete
level-coloured query systems for

- `P0={(2,0,0),(2,1,0)}`, and
- `P1={(2,0,0),(2,2,0)}`

remain isomorphic.  The pre-outcome checker found a bijection after three
refinement rounds and 54 backtracking steps, checked every incidence edge in
both directions, fixed root group 0, and exchanged leaf groups 11 and 12.

The finite-query-system transport theorem therefore predicts equality for
every positive level-cost vector, not only at the two endpoints below.  At
fixed root and middle costs `(a,b)=(4,11)`, P1 must inherit P0's bounded integer
law

- `V=37` for every integer `1<=c<=22`;
- `V=38` at `c=23`.

## Frozen exact endpoint predictions

| P1 leaf cost | exact value | optimal groups | group-0 children |
| ---: | ---: | --- | --- |
| 22 | 37 | `[0]` | `[33,33,33]` |
| 23 | 38 | `[0]` | `[34,34,33]` |

The ordered child signature is frozen because the structural bijection fixes
root group 0 and its response-cell labels.

## Prospective composed-family holdout

Apply the all-coordinate involution `0<->2` to P1 while fixing outside token
`-1`.  This P1 image has not been opened under the explicit-sentinel encoding.
The composed structural transport predicts the same values, transported
unique root, child multiset, and exact search counts at `c=22,23`.

## Decision rule

The mechanism passes only if:

1. the P0/P1 explicit-sentinel isomorphism is independently edge-checked;
2. both P1 endpoint values, unique optima, and ordered root children match;
3. exact lower and constructive upper bounds agree in all cases;
4. the unseen composed-family transport matches values, policies, child
   multisets, and state/action/compatibility counts; and
5. a zero-production-import audit reconstructs the root minima and transport.

Any mismatch is retained as a falsification.  Passing proves a constructive
transfer capability and the P1 bounded integer chamber by theorem plus the
already exact P0 endpoints; it does not classify non-isomorphic families,
real-valued costs, incomplete query libraries, or alternative physical-copy
models.

## Verification plan

Run exact enumeration only after this protocol is pushed.  Preserve raw JSON,
an independent audit, deterministic hashes, a targeted regression, lint, and
the full test suite.  Update the existing draft PR; do not merge it.
