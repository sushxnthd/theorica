# THEORICA: Open-Ended Theory Synthesis, Active Causal Discovery, and Native Evaluation for Autonomous Experimental Science

**Sushanth Dasari — Preprint draft, 20 September 2026**

## Abstract

Scientific agents are often evaluated on question answering, coding, simulation, or laboratory automation in isolation, while experimental science requires a coupled loop: form hypotheses, choose measurements, revise theories, distinguish physical effects from instrument faults, and survive tests not used during discovery.

THEORICA is a student-led research program organized around these failure modes. A frozen internal test first rejected our strongest initial hypothesis: an adaptive falsification-oriented experiment policy did not reliably outperform a matched uniform design. Independent equation tasks then exposed a deeper bottleneck because the agent could only select among complete equations already present in its hypothesis menu. We replaced fixed-family selection with bounded compositional symbolic synthesis and later extended it to multivariate relationships.

A separate causal branch uses interventions to resolve graph ambiguity. On 48 paired instances generated with the native Active-Causal-Discovery-Bench package, THEORICA achieved directed F1 **0.647 vs 0.599** for random intervention targeting, with fewer interventions (**1.83 vs 2.90**). The paired F1 gain was **+0.048**, bootstrap 95% CI **[+0.015,+0.082]**, one-sided Wilcoxon **p=0.00195**. The pinned replay committed in this repository reproduces the aggregate result exactly.

Separately, a generic 15-experiment force-map identification policy was evaluated with the native DiscoverPhysics trajectory evaluator on five compatible static two-particle worlds and passed the benchmark trajectory threshold on **4/5** worlds: gravity, Yukawa, fractional gravity, and extra dimensions. Coulomb failed and is retained as a negative result.

These are bounded claims, not leaderboard placements or evidence of general autonomous science. The next phase is preregistered before hardware data collection: freeze the scientist and test transfer to an unfamiliar physical optics rig under calibration error, drift, saturation, noise, and actuator uncertainty.

## 1. Research discipline

THEORICA uses a versioned workflow intended to reduce post-hoc benchmark optimization:

1. Development environments may be used for debugging.
2. Designated holdout seeds are not reused as tuning data.
3. Method files are frozen before important holdout evaluations.
4. Source-derived compatibility tests are distinguished from native third-party package execution.
5. Negative results remain in the public record.
6. The physical experiment is preregistered before official hardware data exist.

The first major frozen result is a failure of the project's original strongest claim.

## 2. Failure of the original active-sampling claim

The v0.2 simulator instantiated ten randomized laboratory families with hidden drift, bias, outliers, saturation, heteroscedastic noise, and regime changes. The agent maintained competing models, selected experiments from predictive disagreement, replicated anomalous measurements, and opened instrument-fault hypotheses only when residual evidence justified them.

After matching the estimator used by the active and uniform policies, the frozen comparison did not show a reliable active-design advantage. Mean NRMSE was **0.0205** for selective sampling and **0.0192** for matched uniform sampling; the selective policy won **49/100** paired worlds and the paired confidence interval crossed zero.

That rejected the claim that the heuristic reliably outperformed a competent space-filling design.

## 3. Fixed hypothesis languages create a discovery ceiling

External equation tasks exposed a deeper limitation. The v0.2 scientist selected among eleven complete model families and solved only **2/8** one-dimensional Nguyen symbolic-regression tasks.

If the correct function is not representable in the hypothesis language, experiment selection alone cannot recover it. This shifted the project from **model selection** toward **theory construction**.

## 4. Compositional theory synthesis

v0.3 replaced complete-equation selection with a bounded grammar of reusable terms: variables, polynomial atoms, nonlinear transforms, products, nested transforms, and fitted constants. Sparse compositions are ranked by predictive fit plus structural complexity.

On Nguyen 1–8, predictive recovery increased from **2/8 to 8/8**. The method was frozen before coefficient-perturbed variants and solved **5/5** designated transfer tasks.

A multivariate extension added cross-monomials, nonlinear interactions, variable powers, and dimensional utilities. On the included 70-run low-dimensional suite, all runs achieved **NRMSE < 0.01**.

These suites are development and transfer evidence, not claims of universal symbolic discovery.

## 5. Active causal discovery

THEORICA maintains a separate causal branch because graph orientation is not the same problem as equation fitting. The causal scientist estimates an observational skeleton with conditional-independence tests, orients available v-structures, applies Meek-style closure, and then spends an intervention budget on unresolved relationships.

### Frozen internal holdout

After development on one seed family, the causal method was frozen and tested on 72 unseen generated worlds. Mean directed-edge F1 was **0.588 vs 0.519** for random intervention targeting, while mean intervention count fell from **2.06 to 1.57**.

### Native ACDB execution

To remove the self-authored-evaluator concern, THEORICA was executed against the native Active-Causal-Discovery-Bench package. The workflow uses ACDB's own benchmark instance builder, observational data, intervention sampler, graph-submission representation, and scorer.

| Metric | THEORICA | Random target |
|---|---:|---:|
| Directed F1 ↑ | **0.647** | 0.599 |
| Skeleton F1 ↑ | 0.790 | 0.790 |
| DAG SHD ↓ | **5.48** | 6.17 |
| Efficiency ↑ | **0.839** | 0.624 |
| Interventions used ↓ | **1.83** | 2.90 |

Across 48 paired native instances:

- paired directed-F1 gain: **+0.04796**
- paired bootstrap 95% CI: **[+0.01480,+0.08181]**
- one-sided paired Wilcoxon: **p=0.00195**
- pair outcomes: **21 wins / 24 ties / 3 losses**

The native replay inside this repository reproduces these aggregate values exactly.

This is not an official ACDB leaderboard submission and does not use the paper's canonical leaderboard seed panel.

## 6. Native DiscoverPhysics trajectory evaluation

DiscoverPhysics places scientific agents in unfamiliar simulated physical worlds, lets them design experiments, and evaluates executable discovered laws on held-out trajectories plus a separate explanation axis.

Under THEORICA's zero-personal-spend constraint, we evaluated a deterministic scientific policy on the native trajectory axis without a paid LLM judge.

The panel contains five static two-particle worlds sharing the same public experiment interface:

- gravity
- Yukawa
- fractional gravity
- Coulomb
- extra dimensions

The same generic policy is used for every world. It spends exactly **15 experiments**:

- five scaling interventions to estimate how the exposed physical parameters affect acceleration;
- ten radial probes to estimate a non-parametric acceleration map.

The force map and scaling exponents are then frozen before native held-out trajectory evaluation. The adapter does **not** read the world's hidden law, optimal explanation, explanation rubric, or evaluator holdout trajectories during discovery.

| World | Mean particle MSE | Native trajectory criterion |
|---|---:|---:|
| gravity | **3.91e-10** | **PASS** |
| Yukawa | **2.89e-05** | **PASS** |
| fractional | **3.39e-12** | **PASS** |
| Coulomb | 5.39e-01 | FAIL |
| extra dimensions | **1.61e-05** | **PASS** |

Thus the generic policy passes **4/5** native trajectory evaluations on this selected compatible panel.

The scaling interventions independently recovered approximately:

- gravity: p1^1 p2^-1
- Yukawa: p1^1 p2^-1
- fractional: p1^1 p2^-1
- extra dimensions: p1^1 p2^-1
- Coulomb: p1^1 p2^1

The Coulomb failure was published before any Coulomb-specific retuning.

The supported claim is limited to four trajectory-axis passes on this selected compatible panel. It is **not** an 80% overall DiscoverPhysics score, not a full benchmark pass, and not a frontier-model comparison.

## 7. Instrument reasoning and identifiability

An earlier design allowed drift and calibration nuisance parameters in every model. That reduced accuracy because physical parameters and instrument parameters can be non-identifiable under small experiment budgets.

The current instrument critic is evidence-gated: it opens a fault hypothesis only when residual diagnostics support doing so and retains extra nuisance parameters only when penalized evidence improves.

This motivates the physical phase because a real apparatus forces the agent to distinguish **the world changed** from **the instrument changed**.

## 8. Preregistered physical phase

The next decisive experiment is designed before official hardware data exist.

Rig 001 is a motorized optics apparatus with:

- controlled light source;
- fixed polarizer;
- driven analyzer;
- independent angular sensing;
- photodiode/TIA/ADC detector;
- append-only host logs.

The agent receives only the tool schema, allowed ranges, observations, experiment budget, and requirement to submit a quantitative predictive model. It is not told the governing law, calibration offsets, or hidden validation settings.

After **START**, human measurement choices, hints, adjustments, selective restarts, or data deletion invalidate the official trial.

The first preregistered success criterion is:

> **physical holdout NRMSE ≤ 0.10**, with no human intervention and no hidden-validation leakage.

Later tasks add angular bias, source drift, sparse outliers, detector saturation, and composite faults.

## 9. Zero-personal-spend constraint

THEORICA is being built under a hard rule: **₹0 personal spend by the author**.

No paid API, compute subscription, hardware purchase, publication fee, domain, or competition fee is required. Any paid resource used in future official work must be supplied through a genuinely free tier, grant, sponsor, collaborator, institution, or in-kind support.

## 10. Limitations

THEORICA remains a bounded prototype.

- The symbolic grammar is not unrestricted theorem proving or program synthesis.
- Low predictive error may hide non-equivalent explanations.
- The multivariate suite is low-dimensional.
- The causal policy has not been shown superior to every classical intervention strategy.
- The ACDB result is not an official leaderboard placement.
- The DiscoverPhysics result covers only five selected compatible worlds and only the trajectory axis.
- No fresh paid-provider frontier-model augmentation comparison is reported.
- No physical sim-to-real result exists yet.

These limitations are experimental targets, not claims to be papered over.

## Conclusion

THEORICA's main contribution is a falsifiable research progression rather than one benchmark number.

A frozen test rejected the original active-sampling claim. External equations exposed a hypothesis-language ceiling. Compositional synthesis reduced that ceiling on the included suites. A separate causal policy then survived native ACDB execution and exact replay. A distinct trajectory-driven policy subsequently passed four of five native DiscoverPhysics trajectory evaluations on a compatible panel without reading their hidden laws.

The remaining decisive test is physical: whether a scientist frozen in simulation can enter an unfamiliar real laboratory, infer a predictive relationship, and remain reliable when the apparatus itself is imperfect.

## References

1. Cerrato, M., Baur, L., Brugger, J., et al. **Science-Gym: a simple testbed for AI-driven scientific discovery.** *Machine Learning* 115:16 (2026). DOI: 10.1007/s10994-025-06914-x.
2. Wiemann, M. L., Smith, L. M., Melchior, P., Mishra-Sharma, S., Wilson, A. G., Izmailov, P., & Cuesta-Lázaro, C. **DiscoverPhysics: Benchmarking LLMs for Out-of-the-Box Scientific Thinking.** arXiv:2605.26087 (2026).
3. QpiAI. **Active-Causal-Discovery-Bench.** Public benchmark repository (2026).
