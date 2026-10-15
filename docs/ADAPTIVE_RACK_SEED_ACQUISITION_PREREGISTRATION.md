# Frozen protocol: adaptive rack-seed acquisition boundary

**Frozen before confirmatory enumeration:** 15 October 2026  
**Classification:** exact theorem / adversarial discrimination

## Active kernel

Can THEORICA automatically acquire a small operation-generating seed set for a
certified finite left rack while preserving the `|S|*n` reconstruction
advantage, or is external seed information essential?

This study uses the **full-row acquisition model** required by the current rack
reconstructor: choosing carrier element `x` reveals the complete translation
`L_x` at cost `n` oracle cells. The only semantic promise is that the unknown
operation is a finite left rack. Labels carry no semantic information.

## Hypothesis and adversarial alternative

**Candidate hypothesis.** Repeatedly choose the least element outside the
operation closure of the queried seeds. This always terminates with a checkable
generating certificate and may track the minimum generating rank.

**Strongest alternative.** Until a distinguished row is queried, many racks are
indistinguishable from the trivial rack. An adversarial labeling can therefore
force every deterministic full-row policy to query all `n` rows on a rack
whose minimum generating rank is only 2.

For `n >= 3` and distinguished `z`, define `R(n,z)` by:
- `L_x = id` for every `x != z`;
- `L_z` fixes `z` and cycles all elements of `X \\ {z}`.

The predicted mechanism is that all identity-row transcripts are identical
until `z` is queried. If `z` is last in the deterministic policy's all-
identity query order, correctness on both the trivial rack and `R(n,z)`
forces the policy to query all `n` rows, although `R(n,z)` has generating
rank 2.

## Preregistered exact predictions

1. Every `R(n,z)` for `3 <= n <= 64` satisfies the left-rack identity.
2. Every `R(n,z)` has minimum operation-generating rank exactly 2.
3. The least-outside-closure policy has a counterexample by order 3.
4. Across every labeled rack through order 4, the policy always returns a valid
   generating set, but is not always minimum.
5. For each `3 <= n <= 64`, choosing `z` last in any fixed deterministic
   all-identity order makes the policy query all `n` rows.
6. The theoretical randomized-label average for this family is
   `(n+1)/2 + 1/n` queried rows, versus optimum 2.
7. A separately written audit must reproduce the family, rack identity,
   generating rank, deterministic worst case, and randomized expectation
   exactly without importing the primary verifier.

## Gates

All gates must pass:

- zero rack-identity failures in the adversarial family through order 64;
- zero generating-rank disagreements;
- a minimized order-3 greedy counterexample;
- exact exhaustive agreement for every rack through order 4;
- zero deterministic worst-case disagreements through order 64;
- zero exact randomized-expectation disagreements through order 64;
- independent audit exact agreement.

## Consequence threshold

A pass changes THEORICA's runtime contract:
- automatic rack-seed acquisition must be explicitly budgeted and may abstain;
- `|S|*n` remains a conditional reconstruction cost after seeds are supplied,
  not a guarantee that near-minimum seeds can be found at that cost;
- external semantic seeds, partial-row probe designs, or distributional
  assumptions are required to beat the deterministic row-acquisition boundary.

## Claim boundary

The result concerns deterministic adaptive algorithms whose acquisition unit is
a complete translation row and whose only algebraic promise is “finite left
rack.” It is not a lower bound for arbitrary cell-query algorithms, randomized
algorithms with a failure probability, or families with additional structure.
Historical priority is not asserted.
