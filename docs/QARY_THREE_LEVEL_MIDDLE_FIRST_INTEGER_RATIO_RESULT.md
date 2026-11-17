# Exact integer-ratio middle-first theorem

## Theorem

For every integer $k\ge2$ and positive integer costs $x,y$, the exact
binary middle-first worst-case costs are

\[
R_k(x,y)=\max\{(4k+2)x+y,(3k+3)x+3y,(2k+3)x+4y\}
\]

for level costs $(kx,x,y)$, and

\[
M_k(x,y)=\max\{(5k+1)x+y,(4k+2)x+3y,(3k+2)x+4y\}
\]

for level costs $(x,kx,y)$. Both laws have phase boundaries
$2y=(k-1)x$ and $y=kx$.

## Lower certificate and breakpoint lemma

The exact adversary recursion retains each projected coordinate as an affine
exposure $kr+m$ or $r+km$. There are at most four root queries and eight
middle queries, so every possible dominance-order change occurs before the
integer tail $k\ge9$. Exact symbolic elimination matched the predicted
antichains for all sixteen orientation-ratio regimes at $k=2,\ldots,9$.
At $k=9$, the stable symbolic sources are exactly

- root-heavy: $(2,3,4),(3,3,3),(4,2,1)$;
- middle-heavy: $(1,5,1),(2,3,4),(2,4,3)$.

The order is fixed thereafter, proving the lower certificate for every integer
$k\ge2$.

## Universal upper certificate

Six policies were synthesized at $k=2$, one for each orientation and closed
cost cone. For every terminal exposure and both extreme rays of its cone, the
policy margin is affine in $k$. Every margin has nonnegative value at $k=2$
and nonnegative slope. The same finite policy set therefore certifies every
integer $k\ge2$, rather than merely the tested ratios.

## Prospective and independent checks

All 40 frozen cases at $k\in\{3,4,7,11\}$ matched exactly, including both
phase boundaries and extreme regimes. The independent implementation imported
zero THEORICA modules, recomputed all eight frozen antichains, solved all 40
holdouts, and replayed all six symbolic cone certificates. Evidence reproduces
byte-for-byte.

## Executable consequence

`certify_binary_middle_first_integer_ratio(heavy_level, k, x, y)` returns the
exact optimum, active phase, projected faces, and level costs. Ratios below two,
unknown levels, and invalid costs fail closed.

## Scope

The theorem is limited to the binary, four-copy, one-substitution, one-erasure,
middle-first conditioned class and integer ratios $k\ge2$. It does not prove
arbitrary rational ratios, unrestricted first actions, higher arity, or
leaf-first exactness.
