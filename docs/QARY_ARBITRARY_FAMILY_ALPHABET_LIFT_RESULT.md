# Alphabet lift for arbitrary three-word families

## Exact count theorem

For a binary depth-four cube extended by three distinct words from
`{2} x [q]^3`, the complete explicit-sentinel query system has exactly six
unlabeled rooted suffix-trie classes for every `q>=3`. In canonical shape
order, their exact counts are:

| Class | Exact count |
|---:|---:|
| 0 | `q^4 (q-1)^2 / 2` |
| 1 | `q^5 (q-1)^2 / 2` |
| 2 | `q^2 C(q,3)` |
| 3 | `q^6 (q-1)^2 / 2` |
| 4 | `q^4 C(q,3)` |
| 5 | `q^6 C(q,3)` |

Each expression is the recursive embedding number
`E_q(T)=(q)_m/product_i(a_i!)*product_child E_q(child)` of one rooted shape.
Their sum is `C(q^3,3)`, so the classes partition the complete three-word
universe.

This gives an executable policy capability: canonicalize the suffix trie,
select one of six representative policies, and transport it to the requested
family. No family-specific minimax synthesis is required under the theorem's
assumptions.

## Complete unseen q=4 test

The complete `q=4,d=4,k=3` universe contains 41,664 families. Every frozen
prediction passed:

| Class | Predicted | Observed |
|---:|---:|---:|
| 0 | 1,152 | 1,152 |
| 1 | 4,608 | 4,608 |
| 2 | 64 | 64 |
| 3 | 18,432 | 18,432 |
| 4 | 1,024 | 1,024 |
| 5 | 16,384 | 16,384 |

All six symbol-3 holdouts passed and all 15 representative pairs remained
non-isomorphic. Six representative solves replace 41,664 family-specific
solves, a **6,944-fold** reduction.

## Compact exhaustive evidence

The verifier constructed and edge-checked the completion, same-level query,
and response-cell transport for every family. Rather than publishing a large
repetitive catalogue, it commits a canonical stream containing each family ID,
class, and full-map SHA-256 digest. The independent audit regenerated all
41,664 transports and reproduced both the global stream commitment and all six
class commitments.

The audit also reproduced all six full holdout maps, the six class counts, all
15 cross-class separations, and the `q=5` count identity. It imports no
production modules.

The result SHA-256 is
`539903d62ddf653dcac5713d7099c2fee6fe3a9c68ce6d32c1c57cb96a2cf82f`;
the audit SHA-256 is
`6706949573e8571c362d92613b36e131d29245d927f98387df6bef60d4546989`.

## Limits

The result assumes a binary cube base, a common leading symbol for the added
family, three added words, complete prefix libraries, explicit outside
responses, and positive level-only costs. The general suffix-trie transport
proof covers arbitrary family size, but this exhaustive alphabet-lift test is
specific to `k=3,d=4`. It does not cover aliased outside responses, incomplete
libraries, non-level costs, or other adversarial semantics. No new minimax
values were opened. PR #13 remains draft and unmerged.
