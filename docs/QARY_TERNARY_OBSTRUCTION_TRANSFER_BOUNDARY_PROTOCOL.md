# Frozen protocol: algebraic obstruction-pair transfer boundary

## Question and theorem target

The preceding column-generation experiment missed cost `51` on the second
minimal obstruction pair after learning a cost-`51` policy on the first pair.
This experiment tests whether that miss reflects genuinely different adaptive
query systems or failure to close the learned policy set under algebraic
isomorphism.

Represent a restricted prefix-query problem by its **level-coloured partition
hypergraph**.  It has completion vertices, logical-query vertices coloured by
query level, and nonempty response-cell vertices.  A response cell is adjacent
to its query and to precisely the completions producing that response.  The
frozen theorem target is:

> A colour-preserving isomorphism of these hypergraphs transports every
> adaptive mixed-fault policy, including erasure and substitution branches,
> while preserving its terminal level-exposure vectors.  Hence it preserves
> the exact minimax cost for every positive level-cost vector.

The executable consequence must be an explicit checked bijection, not only an
equality of scalar optima.

## Frozen families and predictions

Let `B={0,1}^3` and augment it by one of

1. `P0={(2,0,0),(2,1,0)}`;
2. `P1={(2,0,0),(2,2,0)}`;
3. `P2={(2,1,0),(2,2,0)}`.

The predictions, fixed before the formal run, are:

- `B+P0` and `B+P1` are isomorphic as level-coloured partition hypergraphs;
- the exact cost-`51` policy at level costs `(2,9,3)` transports from `P0` to
  `P1`, explaining the prior `52` prediction as missing orbit closure;
- `B+P2` is not isomorphic to the first two and is separated already by stable
  one-dimensional Weisfeiler--Leman colour multiplicities.

These predictions formalize the mechanism suggested by the already-opened
counterexample.  No reserved cost triple is opened here.

## Exact procedure

1. Build logical query rows by collapsing the four identical physical copies.
2. Refine initial vertex colours jointly across two hypergraphs until stable.
   A colour-multiplicity mismatch is a machine-checkable non-isomorphism
   certificate.
3. When multiplicities agree, run deterministic exact backtracking within
   stable colour classes.  Emit a full vertex bijection and verify colours and
   every edge in both directions.
4. Synthesize the `P0` policy at `(2,9,3)`, transport every logical query and
   non-erasure response cell through the bijection, and independently replay
   the transported tree on `P1`.  The worst cost and Pareto terminal-exposure
   antichain must remain exactly equal.

## Unseen algebraic-family test

Before solving, freeze the seven nonidentity coordinatewise permutations that
independently swap symbols `1` and `2` while fixing `0`.  Apply each permutation
to all ten words of `B+P0`.  These seven transformed ten-word families are the
unseen algebraic holdouts.  For each one:

- construct and edge-check the induced partition-hypergraph isomorphism;
- transport the frozen `P0` policy at `(2,9,3)`;
- replay the transported policy and require exact worst cost `51`;
- independently solve the exact boundary and require optimum `51`.

The transformations and cost are fixed here; the 19 reserved cost holdouts
remain unopened.

## Falsification and independence

The theorem/mechanism is falsified by any invalid emitted bijection, changed
exposure antichain, transported-policy cost other than `51`, or exact holdout
optimum other than `51`.  A stdlib-only audit, with no import from the
production module or primary verifier, must reconstruct the graphs, validate
the mapping, replay the serialized policy, and check the exact boundaries.
Negative results are retained verbatim.
