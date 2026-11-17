# Protocol: fixed classes at the complement half-density boundary

## Question frozen before the holdout enumeration

Complement already gives a class bijection between sparse and dense suffix
families. When the leaf universe has even cardinality and the family has
exactly half the leaves, complement acts inside one family-size layer. Which
query-system classes are fixed by this involution, how many non-fixed class
pairs remain, and can this be decided recursively without enumerating labelled
families?

## Theorem-side prediction

Let `T_{q,h}` be the number of unlabelled rooted `q`-ary suffix-trie shapes
of height `h`, including empty and full leaf sets. Let `F_{q,h}` be the
number fixed by leaf complement. At height zero,

`T_{q,0}=2` and `F_{q,0}=0`.

A height-`h` shape is a multiset of exactly `q` height-`h-1` child shapes:

`T_{q,h} = binom(T_{q,h-1}+q-1,q)`.

Complement is an involution on child shapes. Write
`P_{q,h-1}=(T_{q,h-1}-F_{q,h-1})/2` for its number of two-cycles. A parent
multiset is complement-fixed exactly when every two-cycle occurs with equal
multiplicity on its two members, while fixed children have arbitrary
multiplicities. Therefore

`F_{q,h} = [t^q] (1-t)^(-F_{q,h-1}) (1-t^2)^(-P_{q,h-1})`.

Equivalently,

`F_{q,h} = sum_j M(P_{q,h-1},j) M(F_{q,h-1},q-2j)`,

where `0<=j<=floor(q/2)`, `M(n,r)=binom(n+r-1,r)`,
`M(n,0)=1`, and `M(0,r>0)=0`.

Every fixed class lies at half density `q^h/2`; hence `F_{q,h}=0` whenever
`q^h` is odd. If `A_{q,h}(k)` is the coefficient of `x^k` in the exact
Pólya orbit polynomial, the half-density layer decomposes into `F_{q,h}`
self-complementary classes and
`(A_{q,h}(q^h/2)-F_{q,h})/2` complement pairs.

For a self-complementary class the existing suffix-trie quotient theorem gives
a constructive query-system isomorphism between a family and its complement,
so exact values agree for all positive level-only cost vectors and policies
transport. No such equality is claimed across a non-fixed complement pair.

The derivation gives, for `q=4,h=3`, `T=1,088,430`,
`A(32)=60,802`, and `F=1,326`, leaving 29,738 non-fixed pairs. This is
the theorem-side derivation, not the reserved holdout.

## Prospectively frozen unseen holdout

The holdout is `q=6,h=2,k=18`. Before opening the direct shape enumerator,
the recurrence and independent cycle-index calculation predict:

- 924 total suffix-trie classes across all family sizes;
- 58 classes at exact half density;
- 20 self-complementary half-density classes;
- 19 non-fixed complement pairs;
- coefficient window `A(15..21) = 51,55,55,58,55,55,51`;
- every fixed class has a constructive child-multiset bijection to its
  complement;
- complement squared returns the identical canonical shape.

The labelled universe has `binom(36,18)=9,075,135,300` families. The test
must operate on the 924 exact orbit representatives, not enumerate labelled
families.

## Decisive experiment

1. Enumerate all multisets of six height-one child shapes independently.
2. Classify each shape by leaf count and require the frozen coefficient window.
3. Complement every half-density shape canonically; require an involution.
4. Require exactly 20 fixed shapes and 19 two-cycles.
5. Construct and verify an explicit child-index bijection for each fixed shape.
6. Recompute the Pólya coefficients and fixed recurrence using a
   zero-production-import implementation.
7. Require deterministic JSON artifacts and an independent digest match.

## Falsification and limits

Any coefficient, fixed-point count, pair count, involution, constructive map,
audit, or deterministic digest mismatch falsifies the claim and must be
preserved. Passing remains bounded to complete rooted-tree automorphisms, the
explicit outside sentinel, complete prefix-query libraries, and positive
level-only costs. It does not equate policies across non-fixed complement
pairs and does not cover incomplete libraries, aliased outside responses,
non-level costs, or DAGs with cross-branch sharing.
