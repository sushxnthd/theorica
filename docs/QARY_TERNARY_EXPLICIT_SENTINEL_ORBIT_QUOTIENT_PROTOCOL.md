# Frozen protocol: complete explicit-sentinel obstruction orbit quotient

## Objective

Replace family-by-family exact planning with an algebraic quotient over the
complete two-word extension universe of the binary depth-three witness.
Experimental values for the previously unopened structural class remain sealed
until this protocol is pushed.

## Frozen universe and structural classification

Let the base be all eight binary words in `{0,1}^3`.  Extend it by an unordered
pair from the nine-word fibre

`F={(2,x,y): x,y in {0,1,2}}`.

There are `C(9,2)=36` families.  Under the complete ternary prefix-query
library, explicit outside token `-1`, physical-copy model, and level-coloured
query costs, exhaustive edge-checked graph isomorphism partitions them into
exactly two classes:

1. **same-middle class:** the two added words share coordinate 2 (`9`
   families);
2. **different-middle class:** the two added words differ in coordinate 2
   (`27` families).

The classification was obtained without evaluating any new minimax value.

## Theorem prediction and executable consequence

A colour-preserving query-system isomorphism transports completions, query
groups, response cells, physical multiplicities, feasible states, and policy
trees.  Therefore every family in one class has exactly the same minimax value
for every positive level-cost vector, and a policy synthesized for one
representative transports to all other class members.

The quotient predicts that one exact solve per class and cost replaces 36
family-specific solves: an 18-fold reduction in representative solves, before
accounting for policy-search state reuse.

## Sealed numerical experiment

At fixed root/middle costs `(a,b)=(4,11)`, open leaf costs `c=1` and `c=23` for
one representative of each class:

- same-middle representative: `{(2,0,0),(2,0,1)}`;
- different-middle representative: `{(2,0,0),(2,1,0)}`.

The different-middle values are existing anchors.  The same-middle values and
optimal root signatures are sealed discovery outcomes.  After the
representative values are opened, freeze transported predictions before
opening these reserved exact holdouts:

- same-middle: `{(2,2,1),(2,2,2)}`;
- different-middle: `{(2,1,2),(2,2,1)}`.

## Decision rule

The quotient theorem passes only if:

1. all 36 families are assigned to exactly two edge-checked isomorphism
   classes with sizes 9 and 27;
2. membership is equivalent to equality versus inequality of the added words'
   middle symbols;
3. representative exact bounds close at both costs;
4. transported policies and response-cell maps validate for every family;
5. both reserved holdouts match their prospectively frozen class values,
   transported root policies, and exact search counts; and
6. an independent zero-production-import audit reconstructs the partition,
   representative minima, holdout checks, and claimed solve reduction.

Any extra class, failed transport, or holdout mismatch is retained as a
falsification.

## Limits

This protocol covers this finite 36-family universe, complete query library,
explicit outside token, fixed fault/erasure and copy model, and the two frozen
costs for numerical validation.  Isomorphism implies equality for all positive
costs, but the experiment does not classify larger fibres, incomplete query
libraries, other depths, or non-isomorphic systems.  Keep PR #13 draft and
unmerged.
