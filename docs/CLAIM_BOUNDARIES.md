# Claim Boundaries

## Supported now

- THEORICA v0.3 moved from fixed complete-equation selection to compositional symbolic theory synthesis.
- v0.4 extends synthesis to two-variable interactions and solves the included 70-run multivariate suite.
- A greedy ambiguity-targeting causal policy improves directed graph recovery over random target selection on a separately frozen 72-world internal holdout.
- THEORICA has been executed against the **native Active-Causal-Discovery-Bench package/API** on 48 independently generated official-configuration instances; directed F1 was **0.647 vs 0.599** for paired random targeting while interventions fell from **2.90 to 1.83**.
- The native ACDB replay committed in this repository reproduces the aggregate result exactly at the pinned upstream commit.
- THEORICA has also been executed against the **native DiscoverPhysics trajectory evaluator** on a selected panel of five compatible static two-particle worlds using one generic 15-experiment force-map policy. Four worlds passed the benchmark's native trajectory criterion: gravity, Yukawa, fractional gravity, and extra dimensions. Coulomb failed and remains published.
- Source-derived Science-Gym equations and Nguyen functions are external compatibility tests rather than native benchmark scores.
- The physical sim-to-real protocol was written before any official hardware result exists.

## Not supported yet

- No physical laboratory has been built or operated.
- The DiscoverPhysics result is **not** an official leaderboard score or an overall benchmark pass rate. It covers five selected compatible worlds and only the native trajectory axis; the benchmark's separate LLM-judged explanation axis was not run.
- The native ACDB result is **not** an official ACDB leaderboard placement and does not use the paper's canonical leaderboard seed panel.
- No fresh paid-provider frontier-model + THEORICA comparison has yet been executed under the frozen protocol.
- No result establishes that THEORICA generally outperforms frontier LLM scientific agents.
- The project does not demonstrate general autonomous science.
- No claim should imply that a college admission, grant, publication, or external collaboration is guaranteed.

## Zero-personal-spend constraint

The project does not require the author to pay for APIs, compute subscriptions, domains, publication fees, or hardware. Any paid resource used in future official work must be supplied through a genuinely free tier, grant, sponsor, collaborator, institution, or in-kind support.

These boundaries are part of the research artifact and should remain in public releases.
