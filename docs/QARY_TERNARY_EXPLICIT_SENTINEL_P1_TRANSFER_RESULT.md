# Explicit-sentinel P1 inherits P0's exact breakpoint by structural transfer

## Prospective result

Every frozen prediction passed.  P1 is not a coordinatewise alphabet image of
P0, but its complete explicit-sentinel query system is level-colour-preserving
isomorphic to P0's.  Exact enumeration at the unopened P1 boundary gave:

| leaf cost | exact value | unique optimal group | root children |
| ---: | ---: | ---: | --- |
| 22 | 37 | 0 | `[33,33,33]` |
| 23 | 38 | 0 | `[34,34,33]` |

Thus P1 inherits the same first positive integer breakpoint at `c=23` as P0.

## Theorem consequence

The checked isomorphism fixes root group 0, exchanges leaf groups 11 and 12,
and preserves every coloured incidence edge.  Transporting a policy tree along
this bijection preserves feasible states, response branches, physical-copy
multiplicities, and accumulated level costs.  Consequently P0 and P1 have the
same adaptive minimax value for every positive level-cost vector under the
explicit-sentinel query library.

Combining this transport theorem with the already exact P0 endpoints and
cost-monotonicity proves the P1 bounded integer law at `(a,b)=(4,11)`:

- `V=37` for every integer `1<=c<=22`;
- `V=38` at `c=23`.

This is an executable capability: synthesize once on either obstruction, use
the emitted query/response bijection to transport the policy, and reject a
claimed family-specific policy difference whenever the coloured query systems
are certified isomorphic.

## Unseen composed-family check

The all-coordinate `0<->2` image of P1 was unopened under the explicit outside
token.  It matched both endpoint values, the transported unique root, child
multisets, and all exact search counts.  At each endpoint, both source and
target solves visited 20,085 states, evaluated 15,794 actions, and solved 95
compatibility states.  The target's `c=23` root children were `[33,34,34]`, the
predicted response-label permutation of P1's `[34,34,33]`.

## Independent audit

The zero-production-import audit reconstructed all four root minima from the
raw action tables, checked exact lower/upper-bound equality, unique transported
roots, child multisets, and search-count equality.  It also independently
checked the two structural certificates: each required three refinement rounds
and 54 backtracking steps, with every edge verified in both directions.

## Scientific consequence and limits

The result separates visible word-label variation from the invariant that
actually controls this finite planning problem.  Explicit sentinel refinement
can change non-isomorphic families differently, as P0 and P2 demonstrated,
while a non-obvious query-system isomorphism forces exact equality between P0
and P1 at all positive costs.

The claim is limited to the complete finite query library, the explicit fixed
outside token, matched physical multiplicities, and transported identification
labels.  It does not classify P2 or arbitrary non-isomorphic families, prove a
real-valued chamber decomposition, or cover incomplete query libraries.

## Reproducibility

- Frozen protocol commit: `19a00d0e3226d5b073608d5e00748dc584274043`.
- Results SHA-256: `663666a0ce020d0df5fe6239a53bc38f2a52d01a639002c2b96d39afdbdb0991`.
- Audit SHA-256: `e064dc30549aaa350b79487e7be636b674feee0149b2438351d5feb9f5092631`.
- Raw exact evidence and the independent audit are stored under
  `results/qary_ternary_explicit_sentinel_p1_transfer/`.
