# Frozen protocol: orbit-balanced minimax compression

**Frozen before executing the theorem verifier or exhaustive finite checker.**

## Precise question

When may THEORICA replace uniform randomization over all (inom nk) admissible (k)-label query plans by uniform randomization over the orbit of one structured query under a finite permutation group, without losing the exact (k/n) minimax guarantee for every certified ambiguity set containing the uniform prior?

## Candidate theorem

Let a finite permutation group (G) act on a label carrier (X), with point orbits (O_1,ldots,O_r). Fix a seed query (Ssubseteq X), (|S|=k), and choose uniformly from the distinct translates (G S).

For every (xin O_j),

[
Pr_{Tsimmathrm{Unif}(GS)}[xin T]
=rac{|Scap O_j|}{|O_j|}.
]

Consequently:

1. the orbit mixture has label-independent inclusion (k/n) iff
   [
   rac{|Scap O_j|}{|O_j|}=rac{k}{n}quad	ext{for every }j;
   ]
2. under this balance condition it is minimax with exact value (k/n) for every ambiguity set containing uniform;
3. against the full probability simplex its exact value is
   [
   min_j |Scap O_j|/|O_j|,
   ]
   so an unbalanced action/seed is strictly suboptimal;
4. transitivity is sufficient, but not necessary;
5. support size is (|GS|=|G|/|mathrm{Stab}_G(S)|).

## Proof plan

Double-count incidences ((g,x)) with (xin gS) inside each point orbit. Constancy follows from transitivity on (O_j), and summing inclusion probabilities over (O_j) gives (|Scap O_j|). The previous uniform-prior theorem supplies the upper bound (k/n). Balance makes payoff prior-invariant; imbalance is exposed by a point mass in the least-covered orbit.

## Exact objective

The production certificate and an independent implementation must agree on:

- point-orbit partition;
- distinct query orbit;
- every exact rational inclusion probability;
- orbit-balance ratios;
- balanced iff criterion;
- full-simplex value;
- support size and orbit-stabilizer identity.

## Finite verification

Enumerate:

- cyclic actions for (2le nle10);
- dihedral actions for (3le nle9);
- all seed subsets for these actions;
- intransitive direct-product cyclic actions on two blocks through total size 9;
- all admissible seed subsets for the intransitive cases;
- exact sampler reproducibility and membership;
- malformed/non-closed action rejection.

## Strongest alternative explanation

The result may only restate the classical fact that a block orbit under a transitive group is a 1-design. The project contribution must therefore be bounded to the sharp intransitive balance criterion, fail-closed executable certificate, support-compression accounting, and integration with THEORICA's ambiguity-set contract. No broad design-theory novelty is claimed.

## Cheapest decisive falsification

One finite action/seed for which the production inclusion vector disagrees with direct orbit enumeration, or one unbalanced seed incorrectly certified as universally minimax, kills the implementation. A proof counterexample kills the theorem.

## Publishable threshold

An exact theorem with a sharp iff boundary, independent exhaustive verification, explicit prior-art boundary, and a system consequence for structured query planning. Historical novelty remains unclaimed unless a stronger literature audit supports it.

## Project-consequence threshold

THEORICA must be able to:

1. validate an explicitly enumerated finite permutation group;
2. compute point and query orbits;
3. certify or reject balance exactly;
4. sample exactly and reproducibly from a certified query orbit;
5. expose full-simplex failure value for unbalanced seeds;
6. show a structured family where support drops from (inom nk) to (O(n)).

## Kill condition

Kill if the iff boundary fails, if the checker and production code disagree, if malformed actions are accepted, or if no nontrivial support compression is demonstrated.
