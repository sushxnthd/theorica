# Complete obstruction quotient yields two exact planning laws

## Central result

All 36 unordered two-word extensions of the binary depth-three witness by the
fibre `{(2,x,y): x,y in {0,1,2}}` collapse into exactly two level-coloured
explicit-sentinel query-system classes:

| structural class | families | defining invariant |
| --- | ---: | --- |
| same-middle | 9 | added words share coordinate 2 |
| different-middle | 27 | added words differ in coordinate 2 |

Every one of the 36 representative-to-family isomorphisms was edge-checked.
The finite query-system transport theorem makes this a complete exact quotient:
one synthesized policy per class transports to every family in that class for
every positive level-cost vector.

This reduces family-specific exact synthesis by a factor of 18 at each cost.

## Prospective holdouts

Representative values were opened only after the structural protocol was
published.  Their values, transported query groups, and exact search counts
were then frozen before either reserved family was opened.  Both holdouts
passed every prediction:

| class | leaf cost | value | representative / holdout search counts |
| --- | ---: | ---: | --- |
| same-middle | 1 | 6 | `5600 / 3532 / 49` |
| same-middle | 23 | 69 | `5600 / 3532 / 49` |
| different-middle | 1 | 7 | `20085 / 15794 / 95` |
| different-middle | 23 | 38 | `20085 / 15794 / 95` |

The reserved families matched exact lower/upper bounds, transported optimal
groups, every optimal child-value multiset, and state/action/compatibility
counts.

## Exact integer chamber laws

After the prospective holdouts passed, representative-only exact enumeration
closed every positive integer leaf cost through 23 at fixed `(a,b)=(4,11)`.
By structural transport, these laws hold for all 36 families:

Same-middle class:

`V_same(c) = 6` at `c=1`;

`V_same(c) = 4+3c` for `2<=c<=11`;

`V_same(c) = 15+2c` for `12<=c<=15`;

`V_same(c) = 3c` for `16<=c<=23`.

Different-middle class:

`V_diff(c) = 4+3c` for `1<=c<=10`;

`V_diff(c) = 37` for `11<=c<=22`;

`V_diff(23) = 38`.

Thus the class ordering has a sharp phase pattern:

- at `c=1`, same-middle is cheaper (`6<7`);
- for `2<=c<=11`, the non-isomorphic classes have equal scalar values;
- for `12<=c<=23`, same-middle is strictly harder, reaching `69` versus `38`.

Visible scalar equality therefore does not imply mechanism equivalence.  The
structural distinction predicts when leaf-cost inflation becomes catastrophic:
same-middle pairs ultimately require leaf-level separation, whereas
different-middle pairs retain the root-policy plateau.

## Executable consequence

Given any family in this universe:

1. compare the two added words' middle symbols;
2. select the same-middle or different-middle representative policy;
3. emit and edge-check the completion/query/response-cell isomorphism; and
4. transport the policy and its exact certificate.

This replaces 36 independent search problems with two certified templates and
provides an exact impossibility/cost boundary for every integer `1<=c<=23`.

## Independent audit

The zero-production-import audit independently reconstructed all 36 families,
the 9/27 partition, and every response-cell incidence for 38 class/holdout
maps.  It reconstructed 50 exact root minima and bound equalities and confirmed
the 18-fold representative-solve reduction.

## Limits

The complete classification is restricted to this 36-family finite universe,
the complete depth-three ternary prefix library, explicit outside token,
matched copy/fault/erasure model, and level-only costs.  The numerical chamber
laws are certified only for `(a,b)=(4,11)` and integer `1<=c<=23`.  Larger
fibres, other depths, real-valued costs, and incomplete query libraries remain
open.

## Reproducibility

- Structural protocol: `0fe404a51fa571e6b8875688969d82840b834f1d`.
- Frozen holdout predictions: `492ebf53358189e177701c351f61de938a174565`.
- Results SHA-256: `8efcccb38f5de4c6a1126687b342f8f48f12a273e39b9329c48465862ad16453`.
- Audit SHA-256: `f387492a4adbaf694f3634d7f23c267ba0c0b99550d93862d34abfac928d9254`.
