# Protocol: arbitrary-family suffix-trie generating law

## Question frozen before the decisive enumeration

For the existing depth-four explicit-sentinel kernel, can the bounded-multiset recurrence be promoted from a fixed-`k` enumerator to one ordinary generating function that counts every isomorphism class by added-family size?  Does its unseen `k=5` coefficient also deliver an exact executable quotient of all ternary families, with constructive policy transport?

## Theorem-side prediction

Let `F_{q,h}(x)` be the ordinary generating polynomial for unlabelled rooted suffix tries of exact height `h`, with at most `q` children per internal node, weighted by leaf count.  Freeze

`F_{q,0}(x) = x`

and

`F_{q,h}(x) = sum_{m=1}^q Z(S_m)(F_{q,h-1}(x), F_{q,h-1}(x^2), ..., F_{q,h-1}(x^m))`,

where `Z(S_m)` is the cycle-index polynomial of the symmetric group.  For the ternary case this is

`F_h = A + (A^2 + A(x^2))/2 + (A^3 + 3 A A(x^2) + 2 A(x^3))/6`,

with `A = F_{h-1}`.  Therefore

`F_{3,3}(x) = x + 3x^2 + 6x^3 + 11x^4 + 18x^5 + 31x^6 + 44x^7 + 63x^8 + 84x^9 + 104x^10 + 122x^11 + 138x^12 + 144x^13 + 144x^14 + 138x^15 + 122x^16 + 104x^17 + 84x^18 + 63x^19 + 44x^20 + 31x^21 + 18x^22 + 11x^23 + 6x^24 + 3x^25 + x^26 + x^27`.

The unseen ternary `k=5` universe must consequently contain exactly **18** isomorphism classes.  In canonical shape order, their frozen labelled embedding counts are

`1458, 243, 54, 2916, 8748, 13122, 4374, 2187, 162, 13122, 1458, 972, 81, 486, 729, 19683, 4374, 6561`.

They sum to `C(27,5) = 80,730`.  The unseen quaternary symbolic lift must contain **24** shapes with embedding counts

`41472, 6912, 1152, 82944, 331776, 884736, 221184, 6144, 110592, 4608, 884736, 73728, 393216, 36864, 3072, 18432, 49152, 192, 768, 1769472, 294912, 1572864, 786432, 49152`,

which sum to `C(64,5) = 7,624,512`.

## Frozen holdouts

The lexicographically last family in each canonical ternary class is frozen as follows; suffixes omit the common sentinel prefix.

0. `122, 211, 212, 221, 222`
1. `202, 211, 212, 221, 222`
2. `211, 212, 220, 221, 222`
3. `121, 122, 212, 221, 222`
4. `112, 122, 212, 221, 222`
5. `022, 122, 212, 221, 222`
6. `122, 202, 212, 221, 222`
7. `022, 121, 122, 221, 222`
8. `121, 122, 220, 221, 222`
9. `022, 121, 122, 212, 222`
10. `121, 122, 202, 212, 222`
11. `122, 212, 220, 221, 222`
12. `202, 212, 220, 221, 222`
13. `120, 121, 122, 212, 222`
14. `022, 122, 220, 221, 222`
15. `022, 112, 122, 212, 222`
16. `112, 122, 202, 212, 222`
17. `022, 122, 202, 212, 222`

## Decisive experiment

1. Derive `F_{3,3}` independently with exact integer polynomial arithmetic and compare all 27 coefficients with the frozen vector.
2. Enumerate all `C(27,5)` ternary families only after the predictions above are committed.
3. Classify every family by its unlabelled suffix-trie shape and compare all 18 observed class sizes with the frozen embedding counts.
4. Construct and edge-check a full completion/query/response-cell transport from one representative to every family.
5. Require full-map transport equality for all 18 frozen holdouts.
6. Check all `C(18,2)=153` representative pairs for non-isomorphism.
7. Reconstruct the experiment with a zero-production-import audit and reproduce the global and per-class transport streams.
8. Recompute the quaternary `k=5` symbolic identity without enumerating its 7,624,512-family universe.

## Falsification and stopping rule

Any coefficient mismatch, missing or extra shape, class-size mismatch, failed transport, changed holdout, isomorphic cross-class pair, audit mismatch, nondeterministic artifact, or failed quaternary identity falsifies the claimed law or its executable consequence.  A falsification is retained as a negative result.  Passing establishes the theorem for this exact-height suffix-trie model; it does not establish equivalence under incomplete query libraries, aliased outside responses, non-level costs, or arbitrary adversarial semantics.
