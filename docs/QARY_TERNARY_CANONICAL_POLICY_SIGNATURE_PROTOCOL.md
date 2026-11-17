# Canonical policy-signature boundary protocol

## Status

Frozen before the signature computation is executed. This experiment uses only
the already-opened `P0` and `P2` families at level costs `(2,9,3)`; it opens no
additional reserved family or cost case.

## Question

`P0` and `P2` are non-isomorphic level-coloured partition hypergraphs, but have
the same exact optimum, sorted middle-root cost profile, unrestricted exposure
antichain, and root-conditioned exposure antichains. Does a canonical signature
of the complete deterministic exact policy tree separate them?

## Frozen invariant

For each exact policy node, recursively record:

1. whether it is terminal;
2. the number and sorted lie-count histogram of feasible completions;
3. erasures already used;
4. for a query node, its logical prefix level and the sorted cardinalities of
   its response cells over feasible completions; and
5. the multiset of child signatures, with the recognized-erasure child marked
   separately and ordinary response labels discarded.

The canonical JSON encoding is hashed with SHA-256. Discarding completion,
query, and ordinary response labels makes equality necessary for transport by
any relabeling preserving the mixed-fault decision problem. The signature is
computed for the unrestricted optimum and for each of the three forced logical
middle roots. Tree cost is independently replayed from the serialized policy.

This is a signature of the deterministic exact optimum returned under the
repository's frozen tie-breaking rule. It is not claimed to enumerate every
optimal policy or to be a complete bisimulation invariant.

## Prediction and decision rule

Prediction: at least one of the four canonical policy signatures differs
between `P0` and `P2`.

- If all four hashes and their canonical encodings agree, reject the invariant.
- If at least one differs, report the first recursively localized witness and
  classify the pair as separated by the canonical policy-tree invariant.
- Preserve either outcome, run a zero-production-import structural audit, and
  do not open a reserved case in this experiment.

## Required evidence

- complete canonical encodings and hashes;
- exact replayed costs and node counts;
- a first-difference witness for every unequal signature;
- independent reconstruction of every hash and cost;
- deterministic reproduction, lint, and the full regression suite.

