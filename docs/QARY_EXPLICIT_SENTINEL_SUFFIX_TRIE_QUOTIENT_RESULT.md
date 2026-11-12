# Suffix-trie quotient for arbitrary added families

## Central theorem

Let `q>=3`, `d>=2`, and start with the binary cube `B_d={0,1}^d`. Add any set
`S` of distinct words from

`F_{q,d}={2} x {0,...,q-1}^{d-1}`.

For the complete q-ary prefix library with an explicit outside response, two
extensions have level-cost-preserving active query-system isomorphisms if and
only if the unlabeled rooted tries of their suffix sets are isomorphic.

This strictly generalizes the two-word divergence theorem. Pairwise common
prefix length is simply the trie shape when the added family has two leaves.

## Constructive mechanism

Every active prefix query is a trie node. Its response cells are the node's
children plus the outside cell. A rooted trie isomorphism therefore induces:

1. a leaf/completion bijection;
2. a same-level prefix-query bijection; and
3. a response-cell bijection preserving every completion edge.

Conversely, the active response partitions reconstruct the rooted trie one
level at a time, so different trie shapes cannot be isomorphic. Prefixes
outside the binary base and added trie are constant outside-token rows and are
minimax-dominated.

For a trie node `T` with `m` children and multiplicities `a_i` of repeated
child shapes, the exact number of embeddings into a q-symbol level is

`E_q(T) = (q)_m / product_i(a_i!) * product_child E_q(child)`.

Thus class sizes are available in closed form by a recursive computation.
Canonicalize the trie, choose one stored policy per shape, and transport it to
the requested family. This removes family-specific policy synthesis for any
number of added words covered by the model.

## Complete unseen three-word test

The complete `q=3,d=4,k=3` universe contains 2,925 families and exactly six
classes:

| Class | Families |
|---:|---:|
| 0 | 162 |
| 1 | 486 |
| 2 | 9 |
| 3 | 1,458 |
| 4 | 81 |
| 5 | 729 |

The multiset of sizes is exactly the frozen prediction
`{1458,729,486,162,81,9}`. The recursive formula reproduced every size, all
six lexicographically reserved holdouts passed, and all 15 representative
pairs were certified non-isomorphic.

One representative per trie shape replaces 2,925 family-specific solves with
six representative solves: a **487.5-fold** reduction.

## Independent verification

The zero-production-import audit independently:

- reconstructed all 2,925 three-word extensions and six canonical tries;
- regenerated and edge-checked all 2,925 constructive transports;
- reproduced every transport digest and all six full holdout maps;
- checked all 15 cross-class separations; and
- verified the recursive embedding formula on 12 additional `(q,d,k)` grids
  with `q in {3,4}`, `d in {2,3,4}`, and `k in {2,3}`.

The deterministic compact-catalogue result SHA-256 is
`b721e31e0bbe23169abf233c1833b7e7813bb2b9c72de423353ff0b5b90fff48`;
the audit SHA-256 is
`06237ce85c09ff07abd76879d88cb4728fdfa840d7f7b1ea5f0eab28758af7a7`.

## Limits

The theorem assumes a binary cube base, a common leading symbol for the added
family, a complete prefix library, explicit outside responses, and positive
level-only costs. It does not cover aliased outside responses, incomplete
libraries, arbitrary non-level costs, or other adversarial semantics. The
complete experiment tests three added words at one unseen `(q,d)` setting;
the arbitrary-family statement follows from the constructive trie proof, not
from exhaustive enumeration of all parameter sizes. No new numerical minimax
values were opened. PR #13 remains draft and unmerged.
