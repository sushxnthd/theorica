# Result: cycle parity exactly counts complement-fixed policy classes

## Central claim

Let a finite permutation group `G` act on a finite leaf universe `U`, and let
set complement `C(A)=U\A` commute with `G`.  If `F` is the number of `G`-orbits
of subsets that are fixed by complement, then

`F = |G|^-1 sum_{g in G} |Fix(Cg)|`

and the summand is determined by the leaf-cycle type of `g`:

- an odd cycle forces `|Fix(Cg)|=0`;
- if all cycles are even, `|Fix(Cg)|=2^c(g)`, where `c(g)` is the number of
  cycles.

This yields an executable impossibility test and exact counter: reject a
candidate transporter as soon as its first odd leaf cycle is found; otherwise
the compatible family count is `2^c(g)` without enumerating subsets.

## Proof

Count pairs `(g,A)` satisfying `gA=A^c` in two ways.  Summing over `g` gives
`sum_g |Fix(Cg)|`.  A complement-fixed orbit contributes one complement
transporter coset for every family in the orbit.  The earlier transporter-coset
law gives `|Trans_c(A)|=|Stab(A)|`, while orbit-stabilizer gives
`|Orb(A)| |Stab(A)|=|G|`.  Thus each fixed orbit contributes exactly `|G|`
pairs, proving the trace identity after division by `|G|`.

On a leaf cycle `(u_0,...,u_{m-1})`, the equation `gA=A^c` forces membership to
alternate.  Closing the cycle is impossible for odd `m`.  For even `m`, either
choice at `u_0` uniquely determines one of two alternating assignments.
Different cycles are independent, giving `2^c(g)`.

## Prospectively frozen holdout

The protocol commit froze the complete binary tree at height four before the
group enumerator was opened:

- 16 leaves and 15 internal nodes;
- group order `2^15=32,768`;
- predicted suffix-shape count `231`;
- predicted complement-fixed half-density classes `23`; and
- predicted twisted weight `23 * 32,768 = 753,664`.

The number of eligible automorphisms and their cycle-type distribution were
explicitly left unopened.

## Exact result

The explicit local-swap enumerator constructed every one of the 32,768 induced
leaf permutations.  It found:

| Quantity | Exact result |
|---|---:|
| Distinct leaf-cycle types | 36 |
| All-even-cycle automorphisms | 24,305 |
| Automorphisms rejected by an odd cycle | 8,463 |
| Rejection fraction | 25.8270263671875% |
| Twisted even-cycle weight | 753,664 |
| Weight divided by group order | 23 |
| Unlabelled suffix shapes | 231 |
| Half-density suffix shapes | 35 |
| Complement-fixed half-density shapes | 23 |

The frozen prediction passed exactly.  In this family, the parity obstruction
eliminates 8,463 automorphisms before any subset search, and the remaining
cycle types count all compatible labelled families directly.

## Independent verification

The audit does not import the explicit enumerator.  It reconstructs the group
cycle distribution from the binary wreath recurrence:

- without a root swap, concatenate the two independent child cycle types;
- with a root swap, double every cycle length in the cross-half composition;
  every child-group element occurs as that composition for exactly
  `|G_child|` ordered pairs.

This recurrence independently recovered all 32,768 elements, all 36 cycle
types, 24,305 eligible elements, and weighted sum 753,664.  Its distribution
digest exactly matched the explicit enumeration.  A separate integer-ID shape
recurrence independently recovered `231`, `35`, and `23`.

Both programs were run twice with byte-identical JSON artifacts.  The primary
results SHA-256 is
`c31fb1da166d5d1c159872835c0472dea45db2ec710274f2524f6728b097c2dc`; the
audit artifact SHA-256 is
`7f43f41ba8b9b249a1e6a5c5a21c579a68336a424fee8e37a7bf504f8b9e2e83`.

## Scope and limitations

Twisted Burnside counting is classical; novelty is not claimed for that
machinery.  The contribution here is the exact complement specialization, the
cycle-parity certificate, its executable policy-class consequence, and an
independently checked prospective tree-family holdout.  The current query
interpretation still assumes complete trees, the complete prefix library, an
explicit sentinel, and positive level costs.  This experiment proves an exact
finite-family law, not an asymptotic speed guarantee for arbitrary group
representations.
