# Exact four-word suffix-trie recurrence

## Central result

For the depth-four explicit-sentinel query system with a binary cube base and four distinct added words from `{2} x [3]^3`, the complete family universe has exactly **eleven** query-system isomorphism classes.  The classes are generated directly by the bounded-multiset suffix-trie recurrence frozen before enumeration.

In canonical shape order, the predicted and observed counts agree exactly:

| Class | Predicted | Observed |
|---:|---:|---:|
| 0 | 81 | 81 |
| 1 | 2,916 | 2,916 |
| 2 | 243 | 243 |
| 3 | 243 | 243 |
| 4 | 1,458 | 1,458 |
| 5 | 2,187 | 2,187 |
| 6 | 54 | 54 |
| 7 | 162 | 162 |
| 8 | 2,187 | 2,187 |
| 9 | 6,561 | 6,561 |
| 10 | 1,458 | 1,458 |
| **Total** | **17,550** | **17,550** |

The executable consequence is an exact classifier plus policy transport: solve one representative per shape, then constructively transport its completion, query, and response-cell policy to the requested family.  This replaces 17,550 family-specific solves with eleven representative solves.

## Proof mechanism

An unlabelled height-`h`, `k`-leaf suffix shape is a multiset of at most `q` height-`h-1` shapes whose leaf counts sum to `k`.  If the root has `m` children and equal child shapes occur with multiplicities `a_i`, the number of labelled embeddings is

`E_q(T) = (q)_m / product(a_i!) * product(E_q(child))`.

Generating the recurrence at `q=3,h=3,k=4` yields the eleven shapes above without inspecting a family.  The embedding counts partition `C(27,4)` exactly.  An unseen symbolic alphabet check at `q=4` independently produces fourteen shapes with counts

`864, 55296, 4608, 3456, 27648, 73728, 768, 3072, 16, 55296, 294912, 49152, 1024, 65536`,

which sum exactly to `C(64,4) = 635,376`; the `q=4` family universe was not enumerated.

## Exhaustive falsification

- All 17,550 ternary families were classified and received an edge-checked constructive transport.
- All eleven lexicographically last frozen families passed as full-map holdouts.
- All 55 pairs of class representatives were checked and remained non-isomorphic.
- A zero-production-import audit regenerated every family, class, transport digest, holdout map, recurrence count, global stream, and eleven per-class streams.
- The verifier and audit reproduced byte-identical outputs on deterministic reruns.

The canonical all-family transport stream commits to SHA-256 `7b93e9dfe3dca7735a4e9c7be17d7ec7dc653ec4edd42011a366eaae17d32370`.  The result artifact SHA-256 is `5e8fed6e2f919a862fbe91ade8e6e7782b9b0474a82dcf963ee49dab9d6aae39`; the audit artifact SHA-256 is `4ea90a0048fc58e4ee098e29d831715a9734933c9c6e52fda3c5b97da3dc0911`.

## Limits

This exhaustive result is specific to a binary cube base, a common explicit outside-sentinel prefix, four added words, ternary suffix symbols, depth four, complete prefix libraries, and positive level-only costs.  The symbolic `q=4` check certifies the recurrence count identity, not all 635,376 transports.  The result does not cover aliased outside responses, incomplete libraries, non-level costs, arbitrary adversarial semantics, or a general induction over every depth and family size.  The draft PR remains unmerged pending scientific review.
