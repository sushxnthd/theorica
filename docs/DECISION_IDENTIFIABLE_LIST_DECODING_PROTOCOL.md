# Decision-identifiable list decoding protocol

Status: frozen before opened search or holdout execution.

## Question

Can THEORICA certify an exact robust plan from a corrupted feature-query
transcript even when the underlying payoff model is not uniquely decodable?

## Proposed law

For a two-action finite robust game, enumerate every feature-span payoff completion
within the certified row-corruption and erasure budget. For each completion
(	heta), compute its exact minimax value (v_	heta) and exact interval
(P_	heta) of optimal action-zero probabilities.

The transcript identifies an exact robust value and executable policy if and only
if:

1. all (v_	heta) are equal; and
2. the interval intersection (igcap_	heta P_	heta) is nonempty.

Any point in that intersection is optimal in every feasible world. If either
condition fails, two feasible worlds have different values or disjoint optimal
sets, so no transcript-only exact answer can be guaranteed.

## Frozen gates

- Preserve at least 40 opened non-uniquely-decodable but decision-identifiable
  cases and 20 prospective unseen-family holdouts.
- Preserve at least 40 indistinguishable-world abstention attacks spanning both
  unequal-value and disjoint-policy failures.
- Compare with unique-model decoding, which must abstain on every positive case.
- Recompute every version space and interval using an independent Fraction-only
  checker with zero production imports.
- Require exact policy/value replay, deterministic evidence, full regression,
  Ruff, and hosted exact workflows.

## Scope

Feature rows, payoff-in-span status, corruption budget, erasure locations, and
query transcript are externally certified. The first implementation is limited
to one two-action component and explicitly bounded finite version spaces. It does
not cover noisy approximate structure, probabilistic corruption, hidden feature
maps, or more than two actions.
