# Exact ratio-two middle-first slice theorems

## Result

For positive integer costs (x,y), binary middle-first identification with
one substitution, one erasure, and four copies per prefix query has the exact
values

\[
R(x,y)=\max\{10x+y,9x+3y,7x+4y\}
\]

when level costs are ((2x,x,y)), and

\[
M(x,y)=\max\{11x+y,10x+3y,8x+4y\}
\]

when level costs are ((x,2x,y)).

## Proof certificate

The exact adversary recursion visited 178,964 states per projection. Its
complete maximal projected guarantee antichains were respectively

- root-double: ((7,4),(9,3),(10,1));
- middle-double: ((8,4),(10,3),(11,1)).

These give the lower bounds. For the upper bounds, a two-budget policy search
synthesized one tree for each of the three closed cones. Each tree satisfies
both extreme-ray inequalities for its cone. This detail is essential: the
ordinary exact solver's canonical boundary-optimal tree did not cover the
middle cone under either projection, even though another boundary-optimal tree
did. The theorem therefore records policy selection inside the optimal face,
not merely scalar optimality at a boundary point.

All sixteen frozen prospective instances matched exactly. They include both
phase boundaries (y=x/2) and (y=2x), interior points on both sides of each
boundary, and 79:1-scale extremes. A standard-library audit with zero THEORICA
imports independently recomputed both antichains, all sixteen exact optima,
and all six cone certificates.

## Executable consequence

`certify_binary_middle_first_ratio_two(doubled_level, base_cost, leaf_cost)`
returns the exact optimum, active phase, projected faces, and level costs for
either proved slice. Invalid levels and non-positive or non-integral costs fail
closed.

## Limitations

This proves two infinite unequal-cost slices. It does not prove the full
three-variable six-face conjecture, arbitrary rational ratios, higher arity,
or a general convex-hull adversary theorem. The synthesized upper trees are
certificates of existence; the current production planner still canonically
selects a different boundary-optimal tree in the middle-cone tie case.
