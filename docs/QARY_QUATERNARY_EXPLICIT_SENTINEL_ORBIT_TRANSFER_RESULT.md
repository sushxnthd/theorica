# Quaternary orbit transfer: an alphabet-stable two-class theorem

## Central result

The ternary two-class quotient is not an alphabet-size accident.  All 120
two-word extensions of the binary depth-three base by pairs from

`F4={(2,x,y): x,y in {0,1,2,3}}`

fall into exactly two level-coloured explicit-sentinel query-system classes:

| Class | Quaternary families | Invariant |
|---|---:|---|
| same-middle | 24 | added words share their middle symbol |
| different-middle | 96 | added words have different middle symbols |

Every family was classified by an edge-checked graph isomorphism.  The class
sizes and membership rule were fixed before the exact symbol-3 holdouts were
opened.

## Mechanism and general theorem

For any alphabet size `q>=3`, globally nonconstant prefix rows have the
following canonical partitions of the ten completions:

1. the root separates the two binary first-symbol blocks and the two added
   completions;
2. the binary middle-prefix rows have the same partitions for every `q`;
3. the added prefix `(2,m)` either separates the two added completions at one
   shared middle prefix or at two different middle prefixes; and
4. all remaining prefix rows are constant outside-token rows.

Constant rows are minimax-dominated: at a nonterminal state they do not
separate any live completions, and in the worst case an erasure need not be
spent on them.  Removing them leaves exactly the ternary active query system.
Thus the active system depends only on whether the two middle symbols agree,
not on `q` or the names of the symbols.

Consequently, for every integer `q>=3`, this family has exactly two active
query-system classes with counts

`same = q^2(q-1)/2`,

`different = q^3(q-1)/2`.

Every policy and minimax value transports from one representative per class
for every positive level-cost vector under the fixed fault, erasure, and copy
model.  For `q=4`, this replaces 120 family-specific solves by two: a 60-fold
representative-solve reduction.

## Prospective symbol-3 holdouts

At costs `(4,11,c)`, every frozen value and transported root signature passed:

| Holdout class | Pair | `c=1` | `c=23` |
|---|---|---:|---:|
| same-middle | `{(2,3,1),(2,3,3)}` | 6 | 69 |
| different-middle | `{(2,0,3),(2,3,0)}` | 7 | 38 |

The exact state/action/compatibility counts matched their ternary-class
representatives: `5600/3532/49` for same-middle and `20085/15794/95` for
different-middle at both endpoints.  Transported optimal query groups also
matched after the edge-checked query permutation.

## Independent verification

The zero-production-import audit independently reconstructed:

- all 120 unordered pairs and the 24/96 class split;
- 122 completion/query/response-cell edge maps;
- both q=3-to-q=4 active-row reductions;
- eight exact root minima; and
- the 60-fold solve reduction.

The result artifact SHA-256 is
`781ac503e4fe85a70699aed2d811a3f948587a3adca6b27bc8d968a52c5b5e94`.
The targeted regression test and Ruff checks pass.

## Limits

The all-`q` statement is for this depth-three binary base, two added words with
first symbol 2, the complete prefix library, explicit outside response, and
the fixed fault/erasure/copy semantics.  It does not classify more than two
added words, larger depths, incomplete libraries, aliased outside responses,
or different adversarial models.  The exact numerical validation opens only
the frozen q=4 endpoints; the all-cost equality follows from active-system
transport, not from an exhaustive numerical sweep.
