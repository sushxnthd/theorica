# Exact complement duality for dense suffix families

## Central theorem

Let `U=[q]^h` be the leaves of the complete rooted `q`-ary tree and let `G`
be its automorphism group.  Complement is `G`-equivariant:

`g(U \ A) = U \ g(A)`.

It therefore induces an exact involutive bijection between the orbit classes of
`k`-leaf and `(q^h-k)`-leaf suffix tries.  Paired classes have the same orbit
size and stabilizer order.  If the empty family is included, the complete orbit
polynomial is palindromic:

`x^(q^h) P_{q,h}(x^(-1)) = P_{q,h}(x)`.

This sharpens the prior cycle-index counting law with an executable dense-to-
sparse classifier.  A dense family is classified by its sparse complement;
the complement class map selects the corresponding dense representative, and
the existing trie isomorphism constructs the full completion/query/response-
cell transport within that dense class.  It does **not** assert that a family
and its complement have equal minimax values or transport policies to one
another.

## Prospective exact result

The protocol-frozen unseen ternary `q=3,h=3,k=22` universe passed every check.

- All `C(27,22)=80,730` dense families split into exactly 18 classes.
- Their class sizes were
  `81, 4374, 6561, 1458, 19683, 13122, 8748, 486, 4374, 972, 13122, 729, 1458, 2187, 2916, 243, 162, 54`
  in canonical dense-shape order; the sorted multiset exactly equals the prior
  `k=5` class-size multiset.
- The sparse-to-dense class permutation was
  `0→12, 1→15, 2→17, 3→14, 4→6, 5→10, 6→8, 7→13, 8→16, 9→5, 10→3, 11→9, 12→0, 13→7, 14→11, 15→4, 16→1, 17→2`.
- Every paired orbit size and stabilizer order matched under the complete-tree
  automorphism group of order `6^13 = 13,060,694,016`.
- Every dense family received an edge-checked constructive transport from its
  class representative.
- All 18 frozen transformed-complement holdouts passed full-map transport.
- All 153 representative pairs were separated as non-isomorphic level-coloured
  query systems.
- The symbolic `q=4,h=3,k=5/59` complement identity produced 24 classes on
  each side with orbit sizes summing to `7,624,512`.

The executable reduction is exact: 80,730 dense-family policy syntheses reduce
to 18 representative syntheses plus sparse-complement classification and
constructive transport.

## Independent falsification

A zero-production-import audit regenerated the palindromic coefficient vector,
all sparse and dense classes, the complement permutation, all 80,730 transport
digests, all 18 class streams, all 18 holdouts, every stabilizer equality, and
the quaternary symbolic identity.  A separately implemented coloured-graph
refinement produced 18 distinct signatures, independently separating every
dense representative pair.  The audit passed.

- Frozen protocol commit: `6ce94436133637b02585c0c7456c03362f9b0842`.
- All-family transport stream SHA-256:
  `2b3ed399e1140e5b96c7a914c361eea3882f7b0b3e60718a299f7416860e53a4`.
- Result artifact SHA-256:
  `19d5c283695c9119fb8b970ea9caf81e9cf52bc173f18cc87321650609ab0fef`.
- Audit artifact SHA-256:
  `6c3bb2160973d93781967a029cb58141e47595b6cd8914cb1ebb237439fe166f`.

## Limits

The orbit theorem concerns complete rooted-tree automorphisms.  Its executable
query-system consequence uses the existing binary cube base, a separate outside
sentinel, a complete prefix-query library, and level-only positive costs.  The
experiment does not cover incomplete libraries, aliased outside responses,
non-level costs, cross-branch DAG sharing, or arbitrary adversarial semantics.
It does not solve a dense class by reusing its sparse complement's policy; it
uses the complement only to identify the dense class whose own representative
policy is transported.  The draft PR remains unmerged pending scientific
review.
