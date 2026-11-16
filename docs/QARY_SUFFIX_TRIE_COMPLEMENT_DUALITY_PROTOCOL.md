# Protocol: complement duality for dense suffix families

## Question frozen before the decisive enumeration

The active explicit-sentinel kernel classifies a family of added completions by
the unlabelled shape of its suffix trie.  The latest generating polynomial for
ternary depth-three suffixes has symmetric coefficients away from the full-set
endpoint.  Is this symmetry forced by an exact complement involution, and can
that involution turn dense-family classification into a sparse executable
classifier without weakening the constructive policy-transport guarantee?

## Theorem-side prediction

Let `U=[q]^h` and let `G` be the automorphism group of the complete rooted
`q`-ary tree of height `h`.  For every `g in G` and `A subseteq U`,

`g(U \ A) = U \ g(A)`.

Thus complement is a `G`-equivariant involution.  It must induce a bijection
between the `G`-orbits of `k`-subsets and `(q^h-k)`-subsets, preserve each
stabilizer, and preserve each labelled orbit size.  If the empty suffix family
is included, the orbit polynomial

`P_{q,h}(x) = 1 + F_{q,h}(x)`

must therefore satisfy

`x^(q^h) P_{q,h}(x^(-1)) = P_{q,h}(x)`.

For `q=3,h=3`, the unseen dense `k=22` universe is predicted to contain exactly
18 query-system classes.  Its class-size multiset must equal the already proved
`k=5` multiset

`54, 81, 162, 243, 486, 729, 972, 1458, 1458, 2187, 2916, 4374, 4374, 6561, 8748, 13122, 13122, 19683`,

summing to `C(27,22)=80,730`.  Classifying a
dense family must require only constructing and classifying its five-element
complement, followed by the canonical complement-shape lookup.  Within every
dense class, the existing trie isomorphism must still induce a full
completion/query/response-cell transport, so one exact policy per dense class
is sufficient.

The symbolic `q=4,h=3` prediction is 24 classes at both `k=5` and `k=59`, with
identical labelled orbit-size multisets summing to `C(64,5)=C(64,59)=7,624,512`.

## Frozen dense holdouts

For each of the 18 existing canonical `k=5` representatives, apply the fixed
suffix-coordinate permutations `(0 1 2)`, `(0 2)`, and `(1 2)` respectively at
coordinates 1, 2, and 3, then take its complement in `[3]^3`.  These 18
algorithmically specified 22-element families are reserved as full-map
holdouts.  Their predicted dense class is the complement image of the source
sparse class; their orbit size is unchanged.

## Decisive experiment

1. Recompute `P_{3,3}` with exact integer cycle-index arithmetic and require all
   28 coefficients, including the empty family, to be palindromic.
2. Enumerate all `C(27,22)=80,730` dense families after this protocol is
   committed, classify their actual suffix tries, and require exactly 18
   classes with the frozen class-size multiset.
3. Independently classify the five-element complement of every dense family;
   require a bijective dense/sparse class map and equality of every paired orbit
   size and stabilizer order.
4. Construct and edge-check a full completion/query/response-cell transport
   from one dense representative to every dense family.
5. Execute all 18 frozen dense holdouts as full transports.
6. Require all `C(18,2)=153` dense representatives to remain pairwise
   non-isomorphic as level-coloured query systems.
7. Reconstruct the coefficient symmetry, enumeration, class map, transports,
   holdouts, stabilizers, and stream commitments with a zero-production-import
   audit.
8. Verify the `q=4,k=5/59` class-count and orbit-size identity symbolically,
   without claiming exhaustive enumeration of 7,624,512 families.

## Falsification and stopping rule

Any non-palindromic coefficient, extra or missing dense class, orbit-size or
stabilizer mismatch, non-bijective complement class map, failed transport,
changed holdout, cross-class isomorphism, audit disagreement, or nondeterministic
artifact falsifies the claimed duality or its executable consequence.  Preserve
the first failure.  Passing proves only the complete-tree automorphism quotient
used by this explicit-sentinel kernel; it does not claim that a dense family and
its sparse complement have equal minimax values or mutually transportable
policies, and it does not cover incomplete query libraries, aliased outside
responses, non-level costs, or compressed DAGs with cross-branch sharing.
