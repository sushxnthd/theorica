# Frozen protocol: three-level monotonicity correction

Status: frozen after opening one contradiction and before opening the
prospective correction set.

## Trigger

The published seven-face depth-three expression adds the alleged
ancestor-bypass face `(0,4,2)` to the six root-respecting faces. At costs
`(a,b,c)=(1,10,3)` this gives 46, while the proved root-respecting recurrence
gives 45.

Because every root-respecting policy is also an unrestricted policy, the
unrestricted minimax optimum cannot exceed 45. An exact unrestricted binary
solve with a certified feasible upper bound of 45 returned 45 in 0.268 seconds
(12,500 cost-bounded states and 60 compatibility states). Therefore 46 cannot
be an adversarial lower bound.

## Correction hypothesis

For binary depth-three prefix queries with four copies per prefix, one
substitution, one recognized erasure, and positive integer level costs, the
exact unrestricted optimum is the maximum of the six root-respecting faces:

```text
(2,2,4), (2,3,3), (2,4,1),
(3,2,3), (3,3,1), (4,1,1).
```

The `(0,4,2)` term is retired. For any arity, monotonicity already proves that
it is not a valid lower face wherever it exceeds the six-face maximum.

## Frozen prospective set

The following binary cases lie in or near the cone where `(0,4,2)` exceeds
the six-face maximum. Their exact values are sealed until execution:

- `(1,20,3)`;
- `(1,7,3)`;
- `(2,17,5)`;
- `(3,25,7)`;
- boundary probes `(1,6,3)` and `(2,14,5)`.

Additionally, exhaustively test all binary costs in `{1,...,6}^3` against the
six-face law. Opened legacy cases remain controls, not prospective evidence.

## Acceptance criteria

1. All six frozen holdouts equal the six-face maximum.
2. All 216 exhaustive binary-grid cases equal the six-face maximum.
3. At least one holdout has a strict gap between the retired seven-face value
   and the exact optimum.
4. An independent stdlib-only solver reproduces every holdout without
   importing THEORICA.
5. Missing-copy evidence remains fail-closed.
6. The production certificate no longer labels `(0,4,2)` an adversarial lower
   bound, and regression tests explicitly enforce minimax monotonicity.

## Kill criteria

- any exact binary case lies below the six-face maximum;
- any exact binary case lies above the root-respecting feasible cost; or
- the independent implementation disagrees.

## Scope

Passing establishes the corrected unrestricted **binary** depth-three law and
retracts the invalid q-ary seven-face claim. It does not automatically prove
unrestricted exactness for arity greater than two or depth greater than three.
