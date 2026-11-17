# Frozen protocol: alphabet lift for arbitrary three-word families

## Objective

Test the suffix-trie quotient on an unseen alphabet and a 14.2-fold larger
complete family universe. The prior experiment established six rooted suffix
trie shapes for `q=3,d=4,k=3`. The recursive embedding theorem predicts that
the shapes persist for every `q>=3`, with exact polynomial class counts.

## Frozen count law

Order the six canonical shapes by the same recursive tuple representation used
in the ternary experiment. Their predicted counts are:

| Class | Exact count for alphabet q |
|---:|---:|
| 0 | `q^4 (q-1)^2 / 2` |
| 1 | `q^5 (q-1)^2 / 2` |
| 2 | `q^2 C(q,3)` |
| 3 | `q^6 (q-1)^2 / 2` |
| 4 | `q^4 C(q,3)` |
| 5 | `q^6 C(q,3)` |

These expressions are obtained only from the frozen recursive embedding law
`E_q(T)=(q)_m/product_i(a_i!)*product_child E_q(child)` applied to the six
already observed shapes.

For the unopened complete `q=4,d=4,k=3` universe of `C(64,3)=41,664`
families, the class counts are prospectively frozen as:

`1152, 4608, 64, 18432, 1024, 16384`.

They sum to 41,664. One representative policy per shape would replace 41,664
family-specific solves with six representative solves, a 6,944-fold reduction.

## Frozen symbol-3 holdouts

Reserve the lexicographically last q=4 family of each canonical shape:

1. `{(3,2,3),(3,3,2),(3,3,3)}`;
2. `{(2,3,3),(3,3,2),(3,3,3)}`;
3. `{(3,3,1),(3,3,2),(3,3,3)}`;
4. `{(2,3,3),(3,2,3),(3,3,3)}`;
5. `{(3,1,3),(3,2,3),(3,3,3)}`;
6. `{(1,3,3),(2,3,3),(3,3,3)}`.

Every suffix receives the common leading symbol 2 in the full completion.

## Decision rule

The alphabet-lift theorem passes only if:

- all 41,664 q=4 families are enumerated exactly once;
- exactly six canonical trie shapes appear with the frozen counts;
- the recursive formula reproduces every class count;
- every family receives an edge-checked constructive completion, query, and
  response-cell transport from its canonical representative;
- a streaming SHA-256 commitment over all family IDs, classes, and transport
  digests reproduces deterministically without storing a multi-megabyte
  catalogue;
- all six frozen symbol-3 holdouts match and their full maps reproduce;
- all 15 representative pairs remain non-isomorphic; and
- a zero-production-import audit independently regenerates the complete
  universe, counts, 41,664 transports, holdouts, and aggregate commitment.

Any new shape, count mismatch, failed transport, or holdout mismatch is
preserved as a falsification. No minimax values are opened. The claim remains
bounded to a binary cube base, common added leading symbol, complete prefix
library, explicit outside response, and positive level-only query costs. PR
#13 remains draft and unmerged.
