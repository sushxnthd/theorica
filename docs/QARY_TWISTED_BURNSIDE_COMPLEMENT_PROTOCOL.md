# Protocol: twisted Burnside law for complement-fixed policy classes

## Question frozen before group enumeration

The transporter-coset theorem counts complement transports after a fixed class
is known.  Can the number of complement-fixed classes itself be recovered from
the cycle structure of tree automorphisms, independently of suffix-shape
enumeration?

## Theorem-side prediction

Let a finite permutation group `G` act on a leaf universe `U`, and let
complement `C(A)=U\A` commute with `G`.  The number `F` of `G`-orbits fixed by
complement is the twisted Burnside trace

`F = (1/|G|) sum_{g in G} |Fix(Cg)|`.

For subsets, `Cg(A)=A` is equivalent to `gA=A^c`.  Membership must alternate
around every leaf cycle of `g`.  Therefore:

- if any leaf cycle has odd length, `|Fix(Cg)|=0`;
- if all cycles are even, each cycle has two alternating assignments and
  `|Fix(Cg)|=2^(c(g))`, where `c(g)` is the number of leaf cycles.

Hence

`F = (1/|G|) sum_{g: all leaf cycles even} 2^(c(g))`.

This is also a double-counting identity: every complement-fixed orbit
contributes `|Orb(A)| |Trans_c(A)|=|G|` family-transporter pairs, while the
cycle formula counts the same pairs by transporter.

The executable consequence is an independent class counter and certificate
generator that uses only an automorphism's leaf-cycle structure.  It can reject
an impossible complement transport immediately on the first odd cycle and
count every compatible half-density family without enumerating subsets.

## Prospectively frozen unseen holdout

The holdout is the complete binary tree at `q=2,h=4`, with 16 leaves and
`2^(1+2+4+8)=32,768` tree automorphisms.  The previously proved fixed-shape
recurrence predicts, before opening the group enumerator:

- `231` suffix-shape classes across all family sizes;
- `23` complement-fixed classes at half density `k=8`;
- `binom(16,8)=12,870` labelled half-density families; and
- twisted even-cycle weight sum `23 * 32,768 = 753,664`.

No prediction is made for the number or cycle-type distribution of eligible
automorphisms; those are reserved outcomes.

## Decisive experiment

1. Enumerate all 32,768 assignments of swaps to the 15 internal tree nodes.
2. Construct each induced 16-leaf permutation and its complete cycle type.
3. Assign weight zero to every type with an odd cycle and `2^(number of
   cycles)` otherwise.
4. Require the total weight to be exactly 753,664 and its quotient by the group
   order to be exactly 23.
5. Independently enumerate all 231 unlabelled depth-four binary suffix shapes
   and require exactly 23 fixed half-density shapes.
6. Independently audit the cycle distribution by a wreath-product recurrence:
   no root swap gives disjoint child cycle types; a root swap doubles every
   cycle length of the child composition.  This audit must not import the
   explicit group enumerator.
7. Require identical cycle-type distributions and deterministic stream
   commitments.

## Falsification and limits

Any group size, permutation, cycle type, even-cycle weight, quotient,
fixed-shape count, recurrence, distribution, or digest mismatch falsifies the
claim and must be preserved.  Twisted Burnside is classical group-action
machinery; the claim here is the exact complement specialization, its cycle
criterion, executable policy-class consequence, and independent unseen-family
validation.  The query-policy interpretation retains the complete-tree,
complete-prefix-library, explicit-sentinel, and positive level-cost assumptions.
