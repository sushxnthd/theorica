# Q-ary three-level binary middle-first ratio-two theorem protocol

**Frozen before exact evaluation.**

## Scope

This protocol tests two unequal-cost binary middle-first slices of the current
three-level identification kernel.  Let (x,y) be positive integer costs.

1. Root-double slice: root (=2x), middle (=x), leaf (=y).
2. Middle-double slice: root (=x), middle (=2x), leaf (=y).

No unrestricted unequal-cost theorem is claimed.

## Precomputed predictions from the six surviving affine faces

For the root-double slice the predicted exact value is

[
R(x,y)=max{10x+y,;9x+3y,;7x+4y}.
]

For the middle-double slice the predicted exact value is

[
M(x,y)=max{11x+y,;10x+3y,;8x+4y}.
]

Both predictions have phase boundaries (y=x/2) and (y=2x).

## Prospective holdouts

The unopened ((x,y)) pairs are:

[
(79,1),(81,40),(41,40),(40,41),(40,81),(1,79),(2,1),(1,2).
]

They cover both extreme cones, the middle cone, and the two exact phase
boundaries.  Every pair is evaluated on both slices.

## Decisive lower-bound test

Generalize the exact componentwise adversary recursion to project transcript
exposures to

- ((2r+m,l)) for the root-double slice, and
- ((r+2m,l)) for the middle-double slice.

The complete maximal antichains must be exactly

- root-double: ((7,4),(9,3),(10,1));
- middle-double: ((8,4),(10,3),(11,1)).

Any extra maximal point, missing point, or recursion disagreement falsifies the
stated theorem.

## Decisive upper-bound test

Synthesize exact policies at the two phase boundaries ((x,y)=(2,1)) and
((1,2)).  Boundary policies, not interior policies, must certify the adjacent
closed cones by exposure-vector inequalities.  This choice is fixed in
response to the previously preserved failure of interior-optimal policies to
cover complete cones.

## Independent verification and acceptance

A zero-import standard-library audit must independently recompute the projected
adversary antichains, solve all sixteen prospective instances, and verify all
cone inequalities.  Evidence must be deterministic byte-for-byte; missing
copies must abstain.  The theorem passes only if every lower bound, upper bound,
holdout, independent check, regression test, and scoped lint check passes.

## Bounded interpretation

Passing proves two infinite ratio-two slices only.  It does not prove the full
three-variable six-face formula, arbitrary rational ratios, higher arity, or
an unrestricted convex-hull adversary theorem.
