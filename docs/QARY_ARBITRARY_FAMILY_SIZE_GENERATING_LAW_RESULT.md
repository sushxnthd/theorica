# Exact arbitrary-family suffix-trie generating law

## Central result

For the depth-four explicit-sentinel kernel, every unlabelled suffix-trie is counted by one cycle-index recurrence.  If `F_{q,h}(x)` counts exact-height `h` tries by leaf count, then

`F_{q,0}(x) = x`

and

`F_{q,h}(x) = sum_{m=1}^q Z(S_m)(F_{q,h-1}(x), F_{q,h-1}(x^2), ..., F_{q,h-1}(x^m))`.

For `q=3,h=3`, exact integer expansion yields the class-count vector

`1, 3, 6, 11, 18, 31, 44, 63, 84, 104, 122, 138, 144, 144, 138, 122, 104, 84, 63, 44, 31, 18, 11, 6, 3, 1, 1`

for family sizes `k=1,...,27`.  Thus a single closed recurrence replaces separate fixed-size class discovery.

The protocol-frozen unseen `k=5` consequence also held exactly: all **80,730** ternary families split into **18** classes with observed sizes

`1458, 243, 54, 2916, 8748, 13122, 4374, 2187, 162, 13122, 1458, 972, 81, 486, 729, 19683, 4374, 6561`.

These equal the frozen embedding counts and sum to `C(27,5)`.  The executable capability is a complete classifier plus constructive completion/query/response-cell transport: solve one representative per suffix shape and transport the policy to any requested family.  This reduces 80,730 family-specific solves to 18 representative solves.

## Proof mechanism

At a node, the unordered collection of at most `q` child tries is a multiset.  Pólya's cycle index for `S_m` counts these multisets by total leaf weight, giving the generating recurrence above.  For an individual shape `T` with `m` children and equal-child multiplicities `a_i`, the labelled embedding count is

`E_q(T) = (q)_m / product(a_i!) * product(E_q(child))`.

The coefficient `[x^k]F_{q,h}` therefore counts unlabelled shapes, while the sum of `E_q(T)` across those shapes is `C(q^h,k)`.  The independently generated shape recurrence agreed with the first five coefficients of `F_{3,3}` before family classification.

An unseen symbolic alphabet lift at `q=4,h=3,k=5` generated 24 shapes whose embedding counts sum exactly to `C(64,5) = 7,624,512`; that much larger family universe was not enumerated.

## Exhaustive falsification

- All 80,730 ternary families were classified and received an edge-checked constructive transport.
- All 18 lexicographically last protocol-frozen families passed as full-map holdouts.
- All 153 pairs of class representatives were checked and remained non-isomorphic.
- All 27 coefficients of `F_{3,3}` matched the frozen exact vector.
- A zero-production-import audit regenerated all 80,730 families, shapes, transport digests, holdout maps, embedding counts, the global stream, and all 18 per-class streams.
- The verifier and audit reproduced byte-identical outputs on deterministic reruns.

The canonical all-family transport stream commits to SHA-256 `a190d2addcf92f38afd8f3d37787cc9a0282620916a673cc86683d041c37fe50`.  The result artifact SHA-256 is `4df14cd4abda44b684f4bf71add263f997a5bc4bcb6f76df8c078fd7416bb66a`; the independent audit artifact SHA-256 is `e2e9709290b8c049d41f8e32278db4509c208f40bb8d3dd164822a3446f0fd51`.

## Limits

The exact executable equivalence result remains specific to a binary cube base, a common explicit outside-sentinel prefix, ternary suffix symbols, depth four, complete prefix libraries, and positive level-only costs.  The generating recurrence is a combinatorial theorem for bounded exact-height tries; its identification with query-system equivalence relies on the previously established explicit-sentinel suffix-trie quotient.  The `q=4` result is a symbolic count identity, not 7,624,512 checked transports.  The result does not cover aliased outside responses, incomplete libraries, non-level costs, arbitrary adversarial semantics, or compressed DAGs with cross-branch sharing.  The draft PR remains unmerged pending scientific review.
