# Frozen protocol: quaternary explicit-sentinel orbit transfer

## Objective

Test whether the complete ternary two-class quotient is an algebraic property
of the prefix query system or an accident of alphabet size three.  Lift the
unused coordinates to a quaternary alphabet without changing the binary base,
and classify every family before opening reserved exact holdouts.

## Frozen universe and structural experiment

Let the base be all eight binary words in `{0,1}^3`.  Extend it by an unordered
pair from

`F4={(2,x,y): x,y in {0,1,2,3}}`.

There are `C(16,2)=120` families.  Use the complete quaternary depth-three
prefix-query library (21 query groups), explicit outside response `-1`, and
level-coloured query vertices.  Partition the 120 systems by exhaustive,
edge-checked coloured graph isomorphism without evaluating holdout values.

The structural prediction is exactly two classes:

1. **same-middle:** the added words share coordinate 2, 24 families;
2. **different-middle:** the added words differ in coordinate 2, 96 families.

Every nonconstant quaternary query row is predicted to match an active row of
the corresponding ternary class after completion and response relabelling;
the additional query groups are constant and therefore inadmissible at every
nonterminal state.  This active-row reduction predicts minimax equivalence to
the already proved ternary representatives for every positive level-cost
vector and the same fault, erasure, and copy model.

## Frozen exact predictions

At level costs `(4,11,c)`, use representatives
`{(2,0,0),(2,0,1)}` and `{(2,0,0),(2,1,0)}` only as regression anchors.
The unopened symbol-3 holdouts are:

- same-middle: `{(2,3,1),(2,3,3)}`;
- different-middle: `{(2,0,3),(2,3,0)}`.

For both holdouts, open `c=1` and `c=23`.  Frozen predictions are:

| Class | `c=1` | `c=23` |
|---|---:|---:|
| same-middle | 6 | 69 |
| different-middle | 7 | 38 |

The holdouts must also match their representative optimal-root signatures and
exact search counts under a canonical ordering of query groups.

## Decision rule

The generalization passes only if:

1. all 120 families fall into exactly two edge-checked isomorphism classes of
   sizes 24 and 96;
2. class membership is equivalent to equality versus inequality of the
   middle symbols;
3. the active-row reduction removes only constant rows and gives the claimed
   ternary representative system;
4. all four frozen symbol-3 endpoint predictions close exactly;
5. policies transported inside each quaternary class validate; and
6. an independent implementation reconstructs the partition, reductions,
   exact minima, and holdout comparisons.

Any extra class, active-row mismatch, endpoint mismatch, or transport failure
is retained as a falsification.

## Limits

This protocol covers the finite 120-family universe, depth three, the complete
quaternary prefix library, explicit outside token, and the existing residual
fault/erasure/copy state.  It does not establish the quotient for arbitrary
alphabet size or depth.  PR #13 remains draft and unmerged.
