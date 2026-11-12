# Frozen protocol: multiset quotient for unrestricted depth-four insurance

Status: frozen before implementation.

## Question

Can exact unrestricted weighted mixed-fault synthesis be quotiented by
permutations of physically identical query copies without changing the policy
class or minimax value, and does that quotient resolve the depth-four cases
that previously exceeded 240 seconds?

## Mechanism

The current solver removes one indexed physical query after use. Four copies
of the same prefix row and cost are therefore represented by many different
remaining-index tuples even though those states have identical legal actions
and continuations.

Group queries by the exact pair `(outcome row, integer cost)`. A remaining
query state is the count vector of unused copies in each group. Querying a
group decrements its count by one. For the returned executable tree, assign
the next unused original physical index from that group. No query rows are
merged across different costs, and no adaptive action is removed.

The proposed quotient is a state-space isomorphism under permutation of
identical physical copies. Therefore it predicts exactly the same optimum as
the indexed solver whenever either finishes.

## Opened calibrations

- binary depth four, costs `(1,1,1,1)`: unrestricted exact cost 10;
- binary depth four, costs `(1,1,1,20)`: unrestricted exact cost 86;
- all existing weighted-fault unit tests and depth-two/depth-three exact laws.

## Frozen prospective cases

The following binary depth-four cases are frozen without opening their exact
values:

- `(20,1,1,1)`;
- `(1,20,1,1)`;
- `(1,1,20,1)`;
- unseen interior permutation `(2,7,1,3)`.

Each case uses four physical copies per prefix, one substitution, one
recognized erasure, and the complete unrestricted prefix-query library.

## Acceptance criteria

1. The quotient and indexed solvers agree on every tractable opened case.
2. The quotient reproduces both opened depth-four optima exactly.
3. At least one formerly timed-out prospective case finishes under a
   240-second per-case cap, yielding either a new unrestricted optimum or a
   preserved negative result.
4. Every returned tree uses each original physical query index at most once.
5. Removing a required physical copy still causes conservative abstention in
   the established attack case.
6. An independent implementation validates the quotient mapping and every
   completed prospective optimum without importing THEORICA.

## Falsifiers

- any value mismatch with the indexed solver;
- any repeated physical index along a root-to-leaf path;
- a quotient transition unavailable in the original indexed state; or
- no formerly timed-out case completes within the cap.

## Scope

Success accelerates exact unrestricted synthesis and may expose the missing
ancestor-bypass law. It does not by itself prove a closed-form depth-four law,
and it does not quotient nonidentical rows, distinct costs, or semantic query
types that merely happen to be correlated.
