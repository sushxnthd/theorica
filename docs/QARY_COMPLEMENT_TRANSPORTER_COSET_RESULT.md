# Exact complement-transporter cosets

## Central theorem

Let `G` be the automorphism group of a complete rooted tree and `A` a leaf
family whose orbit class is fixed by complement.  Choose one transporter
`tau` with `tau A=A^c`.  Then

`Trans_c(A)=tau Stab(A)=Stab(A^c) tau`.

Indeed, `gA=A^c` exactly when `tau^-1 g` stabilizes `A`; the right-coset
identity follows symmetrically.  Hence complement transports form a torsor for
the stabilizer and

`|Trans_c(A)|=|Stab(A)|`.

Combining this with orbit-stabilizer gives the exact executable certificate

`|Orb(A)| |Trans_c(A)|=|G|`.

For a child-shape multiset with multiplicities `m_s`, the stabilizer order is

`product_s m_s! |Stab(s)|^(m_s)`.

At height two, a child with `r` selected leaves has stabilizer
`r!(q-r)!`, yielding

`product_r m_r! (r!(q-r)!)^(m_r)`.

This strengthens the prior existence theorem.  THEORICA can now classify a
self-complementary family, construct a full complement policy transport, count
all valid transports exactly, and verify the count without enumerating the
tree group.

## Prospectively frozen q=10 holdout

The direct `q=10,h=2,k=50` experiment passed every frozen prediction:

- all **184,756** suffix-shape representatives were enumerated;
- exactly **5,448** lay at half density;
- exactly **252** classes were complement-fixed;
- the remaining classes formed exactly **2,598** complement pairs; and
- these representatives quotient
  **100,891,344,545,564,193,334,812,497,256** labelled half-density
  families.

For every fixed class, the primary implementation constructed a complete
100-leaf tree automorphism.  The root exchanges branches of weights `r` and
`10-r`; each source branch rotates its leaf indices by `10-r`.  The resulting
map was bijective, tree-level preserving, involutive, and sent the canonical
labelled family exactly to its literal complement.

All 252 stabilizers divided the full group order

`(10!)^11 =`
`1,436,790,214,985,056,541,243,375,671,256,147,299,530,515,278,725,120,000,000,000,000,000,000`

exactly, and all 252 orbit-size times transporter-count products returned that
group order.  The holdout also produced 252 distinct stabilizer orders, so the
certificate distinguishes every fixed class in this experiment.  The fixed
classes cover `23,173,023,634,861,942,513,276,322,256` labelled families.

The full fixed-record stream commitment is
`82237f3894b2eee585260a488ca3b1fc82a5e1c844af41de3c44a8f20bc67f87`.

## Independent falsification

A zero-production-import audit regenerated all 184,756 representatives as
weak compositions of ten over eleven child weights.  It independently rebuilt
all 252 full maps, stabilizers, orbit sizes, and stream records.  It also
enumerated all eight automorphisms of the smallest `q=2,h=2` tree: both fixed
classes had complement-transporter counts exactly equal to their independently
counted stabilizers (`4=4` and `2=2`).

The first audit run preserved a useful negative result: all mathematical
checks passed, but its record stream differed because weak-composition order
was not canonical-shape order.  After sorting the independently generated
records by expanded shape, the audit reproduced the primary stream exactly.

- Primary artifact SHA-256:
  `a6e3f025f9604bdaae012379b7326f1b05731e0672e5774b01664b44787ef5de`.
- Audit artifact SHA-256:
  `32340f87480b13318541f1be09e8a85f58106917aad080892fba41c5a4a6a67b`.
- Ruff passed for all new Python files.
- Targeted regression: **1/1 passed**.

## Limits

The algebraic coset statement is general for group actions commuting with
complement.  The executable policy consequence here still assumes a complete
rooted-tree action, binary cube base, complete prefix-query library, separate
outside sentinel, and positive level-only costs.  A large transporter count
does not imply distinct semantic mechanisms.  No equality is claimed across a
non-fixed complement pair, and no incomplete-library, aliased-response,
non-level-cost, or cross-branch-DAG case was tested.
