# Protocol: complement-transporter cosets at half density

## Question frozen before the holdout enumeration

The previous result proves that a complement-fixed suffix-trie class admits a
constructive policy transport.  It does not count all such transports.  Is the
complete transporter set algebraically determined by the class stabilizer, and
can that structure be turned into an exact executable certificate rather than
one witness map?

## Theorem-side prediction

Let the complete rooted `q`-ary tree of height `h` have automorphism group
`G_{q,h}` acting on leaf families.  For a family `A`, define

`Stab(A) = {g in G : gA=A}`

and

`Trans_c(A) = {g in G : gA=A^c}`.

If `[A]` is complement-fixed and `tau A=A^c`, then

`Trans_c(A) = tau Stab(A) = Stab(A^c) tau`.

Thus complement transports form a stabilizer torsor, not an unstructured
collection, and

`|Trans_c(A)| = |Stab(A)|`.

Since `|Orb(A)|=|G|/|Stab(A)|`, every fixed class obeys the exact certificate

`|Orb(A)| |Trans_c(A)| = |G|`.

For a canonical child multiset with multiplicities `m_s`, stabilizers recurse
as

`|Stab(T)| = product_s m_s! |Stab(s)|^(m_s)`.

At height two, if the child leaf counts are `r` with multiplicities `m_r`,
this becomes

`product_r m_r! (r!(q-r)!)^(m_r)`.

For an even-`q` complement-fixed height-two shape, pair every branch of weight
`r` with one of weight `q-r`.  At the root exchange the paired branches; inside
the source branch rotate leaf indices by `q-r`.  Branches of weight `q/2` use
the half-turn.  The resulting full tree automorphism is involutive and maps the
canonical 100-leaf representative to its literal labelled complement.

This gives an executable capability: classify a family, return a full
involutive complement transport, compute the exact number of all transports,
and certify the orbit-stabilizer product without enumerating group elements.

## Prospectively frozen unseen holdout

The reserved holdout is `q=10,h=2,k=50`.  A coefficient dynamic program, not
the direct shape enumerator, predicts:

- `binom(20,10)=184,756` total suffix-shape representatives;
- `5,448` classes at exact half density;
- `binom(10,5)=252` complement-fixed classes;
- `2,598` non-fixed complement pairs;
- `binom(100,50)=100,891,344,545,564,193,334,812,497,256` labelled families;
- full group order `(10!)^11 =`
  `1,436,790,214,985,056,541,243,375,671,256,147,299,530,515,278,725,120,000,000,000,000,000,000`;
- every fixed class admits a full 100-leaf involution; and
- every fixed class satisfies the transporter-coset cardinality and
  orbit-stabilizer product exactly.

## Decisive experiment

1. Enumerate the 184,756 sorted ten-child shapes directly.
2. Require the frozen half-density, fixed-class, and complement-pair counts.
3. For all 252 fixed shapes, construct a root permutation and ten leaf
   permutations and verify the induced map on all 100 leaves.
4. Require the map to be bijective, involutive, tree-level preserving, and to
   send the canonical family exactly to its labelled complement.
5. Compute each stabilizer recursively and require exact divisibility of the
   group order and `orbit_size * transporter_count = |G|`.
6. Independently regenerate the layer by weak compositions of ten over eleven
   child weights, reconstruct every certificate without importing the primary
   implementation, and require identical deterministic streams.

## Falsification and limits

Any frozen count, map, involution, complement image, stabilizer, divisibility,
coset-cardinality, stream, or independent-audit mismatch falsifies the claim
and must be preserved.  The query-policy consequence remains bounded to the
binary cube base, complete prefix libraries, a separate outside sentinel, and
positive level-only costs.  The theorem counts tree automorphisms, not distinct
semantic explanations, and it does not equate policies across non-fixed
complement pairs.
