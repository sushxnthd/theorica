# Set-valued optimal-policy bisimulation protocol

## Status

Frozen before quotient construction. This experiment uses only the already
opened `P0/P2` comparison at costs `(2,9,3)` and opens no reserved case.

## Question

The selected deterministic exact policy trees for `P0` and `P2` have different
canonical signatures. Is that difference merely tie-breaking, or do the full
sets of cost-optimal policies have different reachable-state structure?

## Frozen quotient

Construct the exact mixed-fault state graph with four interchangeable copies
of each logical query. A state consists of completion lie counts, erasures used,
and the remaining multiplicity of every distinct query row/cost group.

For every state reachable from an optimal root action:

1. compute its exact minimum remaining cost;
2. retain **every** query group whose cost plus its worst exact child value
   equals that minimum;
3. retain every feasible ordinary response and the recognized-erasure response;
4. recursively hash the state from its feasible-completion lie histogram,
   erasure count, and the sorted multiset of all optimal action signatures;
5. hash an action from query level, truthful cell sizes, and the sorted multiset
   of ordinary child-state hashes, with the erasure child marked separately.

Identical query copies are represented by their remaining multiplicity rather
than enumerated as distinct actions. Completion labels, logical-query labels,
and ordinary response labels are discarded. Content-addressed nodes form a
finite DAG because every action consumes one query copy.

The unrestricted root is constrained to the three logical middle queries, as
in the preceding exact experiments. Forced-middle roots 1, 2, and 3 are also
computed.

## Prediction and decision rule

Prediction: the `P0` and `P2` root quotient hashes differ for at least one of
the four root conditions.

- If all four root hashes agree, reject the proposed boundary.
- If any differ, report the first recursively localized state/action witness.
- A separation is a statement about the complete set of optimal policies under
  the frozen grouped-query model, not merely the solver's selected policy.

## Required checks

- exact root costs agree with the prior boundaries;
- every retained action satisfies the Bellman equality;
- every omitted evaluated action has strictly larger value;
- all content hashes and edges are independently replayed without importing
  THEORICA;
- deterministic reproduction, lint, full regression, and exact-head hosted
  execution;
- no reserved family or cost case is opened.

