# Frozen protocol: suffix-trie quotient for arbitrary added families

## Objective

Remove the current theorem's restriction to exactly two added words.  Test the
stronger mechanism that the complete explicit-sentinel query system is
classified exactly by the unlabeled rooted trie of the added suffixes.

## Parametric theorem prediction

For `q>=3`, `d>=2`, let the base be `B_d={0,1}^d` and add any set `S` of `k`
distinct words from

`F_{q,d}={2} x {0,...,q-1}^{d-1}`.

Discard the common leading symbol 2 and build the rooted depth-`d-1` trie of
the suffix set.  Forget edge-symbol names but retain node depth and leaf
structure.  The frozen prediction is:

1. two extensions have level-cost-preserving active query-system isomorphisms
   exactly when their unlabeled suffix tries are isomorphic;
2. every trie isomorphism constructively induces a completion, query, and
   response-cell transport for every positive level-cost vector;
3. distinct trie shapes are non-isomorphic because active prefix partitions
   reconstruct the rooted trie level by level; and
4. globally constant outside-token rows are minimax-dominated and irrelevant.

For a trie node with child-shape multiset containing `m` children and shape
multiplicities `a_1,...,a_t`, the number of embeddings into a q-symbol level is
predicted recursively by

`E_q(T) = (q)_m / product_i(a_i!) * product_child E_q(child)`.

This supplies an exact class-size formula and an executable canonicalization
algorithm for arbitrary `k`.

## Unseen complete three-word test

Open the complete `q=3,d=4,k=3` universe only after this protocol is pushed.
There are `C(27,3)=2925` extensions.  Canonical trie enumeration predicts six
classes with sizes:

`1458, 729, 486, 162, 81, 9`.

The class sizes must sum to 2925.  One representative policy per trie shape
would replace 2925 family-specific solves with six representative solves.

Reserve the lexicographically last family of each predicted shape as a
prospective structural holdout.  In suffix notation these are:

1. `{(2,1,2),(2,2,1),(2,2,2)}`;
2. `{(1,2,2),(2,2,1),(2,2,2)}`;
3. `{(2,2,0),(2,2,1),(2,2,2)}`;
4. `{(1,2,2),(2,1,2),(2,2,2)}`;
5. `{(2,0,2),(2,1,2),(2,2,2)}`;
6. `{(0,2,2),(1,2,2),(2,2,2)}`.

Every suffix receives the common leading symbol 2 in the actual completion.

## Decision rule

The theorem passes only if:

- all 2925 extensions appear exactly once;
- canonical trie enumeration finds exactly six shapes with the frozen sizes;
- the recursive embedding formula reproduces each size;
- each family receives an edge-checked constructive transport from its
  canonical representative;
- all six reserved holdouts match their predicted trie classes;
- all 15 representative pairs are certified non-isomorphic; and
- a zero-production-import audit reconstructs the universe, tries, counts,
  transports, holdouts, and synthesis reduction.

Any extra class, count error, failed transport, or holdout mismatch is retained
as a falsification.  This is a structural experiment; no new minimax values
are opened.  PR #13 remains draft and unmerged.
