# THEORICA: Open-Ended Theory Synthesis, Active Causal Discovery, and Native Evaluation for Autonomous Experimental Science

**Sushanth Dasari — Preprint draft, 25 September 2026**

## Abstract

Scientific agents are often evaluated on question answering, coding, simulation, or laboratory automation in isolation, while experimental science requires a coupled loop: form hypotheses, choose measurements, revise theories, distinguish physical effects from instrument faults, and survive tests not used during discovery.

THEORICA is a student-led research program organized around these failure modes. A frozen internal test first rejected our strongest initial hypothesis: an adaptive falsification-oriented experiment policy did not reliably outperform a matched uniform design. Independent equation tasks then exposed a deeper bottleneck because the agent could only select among complete equations already present in its hypothesis menu. We replaced fixed-family selection with bounded compositional symbolic synthesis and later extended it to multivariate relationships. A subsequent frozen misspecification study tested whether the scientist could revise the language itself rather than only search inside it. On 100 unseen noisy periodic-law tasks, a cross-fitted spectral-closure mechanism reduced median extrapolation NRMSE from **0.22759** for the current grammar and **0.09739** for a stronger fixed integer-frequency bank to **0.002293**, with **97/100** runs below 0.01 NRMSE and 100/100 paired wins against both baselines. The method estimates a missing continuous frequency from held-out evidence before injecting the corresponding operator pair into the grammar.

A separate structural-discovery branch asks whether the scientist can infer mathematical organization before fitting an equation. The current system generically enumerates shallow composed terms of an unknown black-box operation, mines empirical equalities among them, verifies additional premises required by candidate representation theorems, abstains when those premises fail, and then allocates subsequent experiments in the selected latent representation. On a frozen panel it correctly routed **125/125** noisy structural worlds. On 50 hidden-coordinate worlds, representation-aware active design achieved median NRMSE **0.000636** versus **0.001345** for random sampling in the same representation and **0.004679** for an active polynomial baseline. A separate untouched panel beat an active RBF Gaussian process on **39/40** worlds at a 20-query budget at each of two noise levels. External falsification substantially narrowed the novelty claim: sample-to-axiom discovery, identity testing, black-box operation recovery, algebraic representation learning, and active symbolic experimentation all have prior art. On 11 published Binary Operation Completion tasks, the generic miner nevertheless matched **88/88** exhaustive identity labels; a named-template tester achieved the same labels about **228x** more query-efficiently, which is retained as a negative result. The surviving research hypothesis concerns the integrated equation-discovery -> theorem-routing -> representation-conditioned experiment loop, not any component in isolation. A further translation-base reconstruction then removed the named-family router: on 1,100 external BOC task/repeat cases it made 1,100/1,100 correct decisions, exactly reconstructed 500/500 compact permutation-action operations using 2.75%-6.50% mean table-query fractions, rejected 600/600 other cases, and automatically recovered distinct action laws such as `XY`, `XYx`, and `XYX`. The accompanying conditional recovery theorem gives an `n(r+b)` upper bound and a natural `Omega(n)` lower bound, yielding order-optimal linear scaling when translation-generator rank and permutation-base size are bounded. A follow-up frozen BOC run then tested that integration end-to-end: across **1,100** task/repeat cases, all route decisions were correct, **200/200** true-group cases were accepted and exactly reconstructed, and **900/900** non-group cases were rejected or abstained. This external result strengthens the integration hypothesis but does not establish field-first priority or sample-efficiency superiority over group-specialized methods.

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

## 5. Cross-fitted grammar closure under misspecification

Compositional synthesis still leaves a deeper limitation: its operator vocabulary is fixed before the data arrive. THEORICA therefore tests whether predictive failure can become evidence about the **hypothesis language itself**.

The first bounded grammar-closure mechanism targets one deliberately omitted structure: an unknown continuous periodic frequency. The current grammar contains fixed-frequency trigonometric primitives such as `sin(x)` and `cos(x)`, but it does not contain a continuously fitted frequency parameter. The closure procedure:

1. fits a deliberately low-complexity cubic scaffold in two cross-fitting folds;
2. asks whether adding `sin(ωx)` and `cos(ωx)` sharply reduces held-out error;
3. searches `ω` continuously from the observations rather than loading a target-frequency bank;
4. opens the grammar only when a frozen held-out error-ratio gate is crossed; and
5. injects the inferred operator pair into the full bounded grammar and reruns sparse theory synthesis.

The frozen evaluation used 100 unseen seeds (1000–1099). Each hidden law had the form `A sin(ωx + phase) + b x + c`, with `ω` sampled continuously from **[1.35, 5.65]**, 40 noisy training measurements on **[-2,2]**, and fresh noiseless validation on 401 points spanning **[-2.5,2.5]**. Measurement noise had standard deviation 1% of the clean training-output standard deviation.

Two fixed-language baselines were strengthened for the comparison: the current THEORICA grammar used trial width 200, and a separate Fourier-bank baseline additionally preloaded integer frequencies `k = 2,...,6`.

| Metric | Current grammar | Fixed integer bank | Spectral closure |
|---|---:|---:|---:|
| Median validation NRMSE ↓ | 0.22759 | 0.09739 | **0.002293** |
| Mean validation NRMSE ↓ | 0.25184 | 0.11720 | **0.003748** |
| Runs below 0.01 NRMSE | 1/100 | 6/100 | **97/100** |
| Paired wins by closure | — | — | **100/100 vs both** |

Median absolute frequency error was **0.00268**, with 90th-percentile error **0.02494**. Against the current grammar, mean paired NRMSE improvement was **0.24810**, bootstrap 95% CI **[0.21461, 0.28395]**, with one-sided paired Wilcoxon **p = 1.95e-18**. The same paired test against the stronger fixed integer-frequency bank also gave **p = 1.95e-18**.

The repository's clean GitHub Actions workflow successfully reruns the new unit tests and the complete 100-task holdout before uploading the result artifact.

This result changes the internal scientific question from only **"which theory inside H?"** toward **"does held-out evidence show that H itself is missing structure?"** The claim remains narrow: this is one successful periodic grammar-expansion mechanism. It is not universal operator invention, a state-of-the-art symbolic-regression claim, or evidence that arbitrary missing mathematical operators can be discovered.

## 6. Equational-theory discovery, theorem routing, and external falsification

Equation discovery normally assumes the representation in which a law should be expressed. THEORICA tests an earlier question: can black-box experiments reveal algebraic structure strongly enough to determine which representation should be learned?

The current structural branch no longer begins with bespoke named associativity or commutativity tests. It enumerates a bounded language of composed terms over the unknown binary operation and evaluates those terms on noisy assignments. Pairs whose empirical signatures are indistinguishable become candidate equations. Named properties are read from that empirically mined equivalence relation only afterward.

Candidate equations do not directly authorize a representation theorem. THEORICA separately verifies additional premises required by the surviving family, including monotonicity and bisymmetry where relevant, calibrates thresholds from repeated measurements, uses replicated confirmation for borderline cases, and abstains when the theorem gate fails.

The currently supported representation routes include additive-generator operations, quasi-arithmetic means, and commutative semilattices. For generator families, the next experiments are selected to reduce uncertainty in the one-dimensional latent coordinate rather than uncertainty of the original two-dimensional output surface.

### Frozen structural and active-design results

A 125-world noisy structural holdout contained equal numbers of additive-generator operations, quasi-arithmetic means, commutative semilattices, ordinary unresolved controls, and smooth adversarial mean-like decoys that satisfy several superficial properties while violating the additional theorem premises.

**125/125** worlds were classified correctly.

On 50 hidden-coordinate worlds with a 20-measurement budget:

| Metric | Result |
|---|---:|
| Active representation median NRMSE | **0.0006357** |
| Random representation median NRMSE | 0.001345 |
| Active degree-6 polynomial median NRMSE | 0.004679 |
| Wins vs random representation | **46/50** |
| Wins vs active polynomial | **50/50** |
| Wilcoxon p vs random | **6.77e-13** |
| Wilcoxon p vs polynomial | **8.88e-16** |

A separate untouched confirmation compared the representation learner with an RBF Gaussian process that actively chose experiments by predictive variance. At the 20-query budget, THEORICA won **39/40** paired worlds at noise fraction 0.001 and **39/40** at noise fraction 0.003, with one-sided paired Wilcoxon p-values **6.37e-11** and **4.07e-10**, respectively.

A separately frozen sequential theorem router achieved **125/125** correct routing at each of two noise levels with median **128** oracle calls. A broad generic-miner reference required 1,540 median calls on its measured subset. This comparison is an internal cost diagnostic, not a published-baseline superiority claim.

### External falsification

We then attempted to falsify the novelty claim rather than extend it by internal benchmark iteration.

The priority search found substantial prior art for every broad component:

- Barzdin & Barzdin and later QuickSpec-style systems discover algebraic/equational laws from samples or tests.
- RoughSpec efficiently searches supplied identity templates.
- Classical and modern identity/property-testing work gives efficient procedures for associativity, group properties, and related identities.
- Black-box group/ring work recovers hidden operation tables from chosen oracle queries under algebraic assumptions.
- Functional Networks and aggregation-function methods learn generator representations when the structural family is supplied.
- HyperCube (ICLR 2025) recovers finite group/group-like operations and learned unitary representations from partial operation tables.
- Active symbolic regression, Bayesian experimental design, and active Koopman learning already choose informative experiments for model discovery.

Therefore none of those components is claimed as field-first.

To test transfer beyond THEORICA-generated worlds, we constructed an external audit from 11 total Binary Operation Completion operations published in the Power/Huh benchmark family. The generic miner enumerated 471 terms with at most three operation applications and used 32 random assignments. Exhaustive full-table verification supplied ground truth for eight identities.

It matched **88/88** identity labels. On the published S5 conjugation operation, for example, it recovered idempotence, left self-distributivity, and flexibility while rejecting associativity and the other tested laws.

However, a hostile named-template baseline matched all **88/88** labels in **100/100** independent repeats using only **65.58** operation calls per task on average, versus **14,976** calls/task for generic mining. This roughly 228-fold gap is retained as a negative result: generic equation mining is useful when the relevant laws are not known in advance, but is profoundly inefficient when the identity templates are already supplied.

We also implemented a clean-room reproduction of the HyperCube architecture and regularizer printed in the ICLR 2025 paper. Under a deliberately minimal fixed-epsilon 500-step protocol and ten 60%-training splits, H-regularized HyperCube achieved mean test accuracy **1.00** on C6 addition, **1.00** on C6 subtraction, **1.00** on S3 composition, and **0.893** on C6 squared addition. The published method therefore provides a strong specialized counterpoint to THEORICA's generic routing approach.

The external audit rejects novelty claims for sample-to-axiom discovery, query-efficient identity testing, black-box operation recovery, learned algebraic representations, and active experimentation individually. The narrower surviving hypothesis is the integration:

**black-box experiments -> empirical equational theory -> theorem-premise verification/abstention -> representation selection -> representation-conditioned experiment design -> held-out falsification.**

We then froze a second external experiment to test that surviving loop end-to-end on the same published BOC family. THEORICA was not given the identity of the group tasks. A shallow generic equation-mining stage first decided whether associativity was empirically supported. Only routed candidates proceeded to two-sided-identity verification and active acquisition of right-regular generator actions. The learned generator actions and their inverses were then used to reconstruct the complete multiplication table without further operation queries.

Across **100 repetitions of all 11 external operations (1,100 task/repeat cases)**, the route decision was correct in **1,100/1,100** cases. It accepted **200/200** true-group cases (modular addition and S5 composition), abstained on **900/900** non-group cases, and reconstructed the complete hidden table exactly on **200/200** accepted cases.

For modular addition on 97 elements, complete discovery and reconstruction used **991 operation queries**, equal to **10.53%** of the 9,409-entry table. For S5 composition on 120 elements, the mean was **1,221.8 queries** (median 1,157), equal to **8.48%** of the 14,400-entry table.

This is not a sample-efficiency superiority result. HyperCube-SE reports approximately **5%** training data for perfect accuracy on true group operations when its group-representation inductive bias is supplied in advance. THEORICA pays additional queries to decide whether that representation is appropriate before using it.

Two dedicated literature searches did not identify an exact predecessor for the full equation-discovery -> theorem-routing -> representation-conditioned experimental-design chain, but absence from search is not proof of priority. The supported status is therefore **a plausibly novel integrated methodology with third-party end-to-end validation**, not a certified field-first breakthrough.

## 7. Translation-base reconstruction without family labels

The external theorem-routing study still selected from a named representation
taxonomy. We therefore tested a stricter question: can a useful algebraic
representation be discovered directly from how an unknown operation acts on its
carrier, without first classifying it as a group, quandle, subtraction law, or
other named family?

For a finite operation `F:SxS->S`, define the left translation

```
L_x(y)=F(x,y).
```

THEORICA queries a small number of complete translations. If they are
permutations, it generates their permutation group and computes a base `B`
for that action. The image tuple of `B` uniquely identifies a permutation
inside the generated group. The scientist therefore queries every remaining
carrier element only on the base. A translation whose signature is missing,
ambiguous, or collides with another carrier element triggers acquisition of
that row in full.

### Conditional reconstruction theorem

Suppose all left translations lie in a permutation group `G`, the map
`x -> L_x` is injective, `G` is generated by `r` translations, and
the action has a base of size `b`. Querying the `r` generator rows and the
`b` base images of every carrier element reconstructs the full operation
using at most

```
n(r+b)
```

oracle values before validation.

A matching information-theoretic argument gives linear lower-bound scaling on a
natural promise subclass. If `|G|=|S|=n`, every bijection
`lambda:S->G` defines `F_lambda(x,y)=lambda(x)(y)`, yielding `n!`
possible tables. Since one query returns one of `n` symbols, any exact
learner requires

```
q >= log_n(n!) = Omega(n).
```

Thus the `O(n)` scaling is order-optimal whenever `r+b=O(1)`.

### Frozen failure and correction

The first 100-repeat external implementation did not pass its frozen gate. It
reconstructed 480/500 expected compact-action cases. The failure exposed a
missing premise in the code and theorem: a base signature can uniquely identify
an element *within the current generated group* while several carrier elements
still collapse onto that same translation.

The corrected implementation explicitly enforces faithfulness of
`x -> L_x`. Signature collisions cause another unresolved translation to be
queried rather than premature acceptance or rejection. A regression test forces
cyclic addition to begin with its identity translation, the degenerate case
that exposed the error.

### External BOC holdout

The corrected method was frozen and run on the same 11 published Binary
Operation Completion operations, with **100 independent acquisition seeds per
operation**. The learner received no family labels.

| Metric | Corrected frozen result |
|---|---:|
| Task/repeat cases | **1,100** |
| Correct accept/reject decisions | **1,100/1,100** |
| Expected compact-action cases | 500 |
| Accepted compact-action cases | **500/500** |
| Exact complete reconstructions | **500/500** |
| Other cases | 600 |
| Unexpected acceptances | **0/600** |

Five algebraically different operations were reconstructed by the same learner:

| Operation | Mean query fraction of full table |
|---|---:|
| modular addition | **2.752%** |
| modular subtraction | **4.761%** |
| S5 composition | **3.377%** |
| S5 conjugation | **4.616%** |
| S5 sandwich `aba` | **6.501%** |

These are chosen-query measurements, so they are not a direct sample-efficiency
comparison with passive table-completion systems.

### Public GAP cross-family challenge

To test whether the BOC result reflected a narrow collection of readable
operations, we constructed a second external benchmark directly from public GAP
catalogues. The workflow regenerates the corpus from SmallGrp and pinned
RightQuasigroups rather than storing hand-authored hidden laws.

The cross-family holdout contains **165 unique public algebras**:

- 80 SmallGrp groups at orders 36, 40, and 48;
- 50 sampled SmallQuandle controls at orders 8 and 9;
- 10 public faithful connected quandles at orders 8 and 9;
- 25 public nonassociative loops of order 6.

Each algebra is evaluated under three frozen acquisition seeds.

The scorer uses the full table only after evaluation to determine whether the
operation satisfies the compact translation-action promise. Family labels and
GAP identifiers are not supplied to the learner.

#### Frozen v1.1 failure

The first cross-family run was frozen before evaluation and **failed**:

| Source | Eligible cases | Exact reconstructions |
|---|---:|---:|
| SmallGrp | 240 | **240/240** |
| faithful connected quandles | 30 | **30/30** |
| nonassociative loops | 75 | **27/75** |
| sampled SmallQuandle controls | 0 | — |

Overall, v1.1 reconstructed **297/345** eligible task/repeat cases while making
**0/150** false acceptances.

All 48 failures were public nonassociative loops. The full-table scorer verified
that those loops satisfied the theorem promise, so this was an algorithmic
failure rather than an out-of-scope benchmark case.

The failure exposed a second partial-representation problem. A translation
outside the current generated subgroup can imitate an element of that subgroup
on the subgroup's current base. If a fresh query then finds

```
L_x(y) != h_x(y),
```

the true `L_x` cannot belong to the current subgroup: if it did, agreement on
the base would have uniquely forced `L_x=h_x`.

This gives a falsification-driven acquisition rule. A counterexample now causes
THEORICA to acquire the complete `L_x`, strictly enlarge the representation
when necessary, and retry. The proposition is formalized in
`docs/TRANSLATION_BASE_RECONSTRUCTION.md`.

#### Frozen v1.2 result

Challenge v1.2 keeps the **same public corpus, split, budgets, eligibility
scorer, and success gates**. The only learner change relative to failed v1.1 is
the counterexample-driven refinement above.

| Metric | v1.2 |
|---|---:|
| Holdout task/repeat cases | **495** |
| Eligible cases | **345** |
| Exact reconstructions | **345/345** |
| Ineligible controls | **150** |
| False acceptances | **0/150** |
| Unique eligible holdout algebras | **115** |
| Unique eligible non-group algebras | **35** |
| Median total table fraction, adaptive | **0.1302** |
| Median total table fraction, random-row | 0.1506 |

Cross-family exactness is:

- SmallGrp: **240/240**;
- faithful connected quandles: **30/30**;
- nonassociative loops: **75/75**.

The same representation learner with random full-row acquisition reconstructs
342/345 eligible cases. Restricting the query-count comparison to cases where
both policies are exact, the adaptive policy uses mean **174.20** calls versus
**193.80** for random acquisition, with outcomes **98 wins / 225 ties / 19
losses** and one-sided paired Wilcoxon **p=3.31e-14**. The adaptive policy also
succeeds on three public group cases where the random policy fails.

The faithful-quandle and loop tables are very small. The frozen 64-query
validation budget effectively exhausts those tables, so the non-group result
supports cross-family correctness rather than subquadratic efficiency. On the
larger SmallGrp holdout, median total query fraction is **0.1098** for adaptive
acquisition versus **0.1302** for random acquisition.

This versioning is intentional: the failed v1.1 result remains public rather
than being overwritten by the corrected v1.2 result.

### Automatic action-law compression

After reconstructing the action representation, THEORICA searches a short word
language over

```
X=L_x, Y=L_y, x=L_x^{-1}, y=L_y^{-1}.
```

If `F(t,t)` is a carrier-wide constant `c`, it also permits
`C=L_c` and its inverse.

The following identities were discovered and then verified exhaustively over
the complete reconstructed external tables:

| Operation | Recovered translation identity |
|---|---|
| modular addition | `L_F(x,y)=XY` |
| modular subtraction | `L_F(x,y)=XYC`, `c=0` |
| S5 composition | `L_F(x,y)=XY` |
| S5 conjugation | `L_F(x,y)=XYx` |
| S5 sandwich `aba` | `L_F(x,y)=XYX` |

The conjugation relation is classical rack/quandle mathematics; the claim is
not that these identities are new. The research object is the family-agnostic
**discovery and reconstruction procedure** that reaches them without a supplied
algebraic label.

### Priority audit

A dedicated hostile search covered black-box group/ring recovery, Cayley-table
completion, quasigroups and loops, racks and quandles, multiplication/operator
groups, permutation-group base algorithms, active algebraic learning, and
operation-table machine learning.

The search found the constituent mathematics separately:

- specialized black-box Abelian-group recovery with linear query complexity;
- classical Sims/Leon permutation bases and strong generating sets;
- permutation representations and translation identities for racks/quandles;
- specialized neural group-representation learning for partial operation
  tables.

It did **not** identify an earlier family-agnostic operation learner that
combines acquired translation generators, automatic permutation-group base
construction, base-image experiments for every unknown translation, adaptive
row acquisition, exact table reconstruction across multiple operation
families, and automatic action-law compression. It also did not locate the same
conditional `n(r+b)` reconstruction guarantee.

This is evidence for priority, not historical proof. The supported wording is
therefore **plausible first-priority field-level methodological contribution**,
not certified first-ever publication.

## 8. Active causal discovery

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

## 9. Native DiscoverPhysics trajectory evaluation

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

## 10. Instrument reasoning and identifiability

An earlier design allowed drift and calibration nuisance parameters in every model. That reduced accuracy because physical parameters and instrument parameters can be non-identifiable under small experiment budgets.

The current instrument critic is evidence-gated: it opens a fault hypothesis only when residual diagnostics support doing so and retains extra nuisance parameters only when penalized evidence improves.

This motivates the physical phase because a real apparatus forces the agent to distinguish **the world changed** from **the instrument changed**.

## 11. Preregistered physical phase

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

## 12. Zero-personal-spend constraint

THEORICA is being built under a hard rule: **₹0 personal spend by the author**.

No paid API, compute subscription, hardware purchase, publication fee, domain, or competition fee is required. Any paid resource used in future official work must be supplied through a genuinely free tier, grant, sponsor, collaborator, institution, or in-kind support.

## 13. Limitations

THEORICA remains a bounded prototype.

- The symbolic grammar is not unrestricted theorem proving or program synthesis.
- The spectral-closure result demonstrates only one periodic operator-family expansion and does not establish universal grammar induction.
- The structural-discovery result uses established ingredients from equational theory exploration, representation theorems, and active learning. The later translation-base result has third-party end-to-end validation and a targeted priority search found no exact predecessor, but certified first-publication priority and peer-reviewed field acceptance remain unestablished.
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

A frozen test rejected the original active-sampling claim. External equations exposed a hypothesis-language ceiling. Compositional synthesis reduced that ceiling on the included suites. A frozen grammar-misspecification study then showed that, for one omitted periodic structure, held-out evidence could trigger a continuous-frequency language expansion that sharply improved unseen extrapolation. A separate black-box structural study then moved the problem one level earlier: THEORICA experimentally diagnosed algebraic identities and recovered latent coordinates that linearized unseen nonlinear composition laws, including a 50/50 frozen hidden-world result. A separate causal policy then survived native ACDB execution and exact replay. A distinct trajectory-driven policy subsequently passed four of five native DiscoverPhysics trajectory evaluations on a compatible panel without reading their hidden laws.

The remaining decisive test is physical: whether a scientist frozen in simulation can enter an unfamiliar real laboratory, infer a predictive relationship, and remain reliable when the apparatus itself is imperfect.

## References

1. Cerrato, M., Baur, L., Brugger, J., et al. **Science-Gym: a simple testbed for AI-driven scientific discovery.** *Machine Learning* 115:16 (2026). DOI: 10.1007/s10994-025-06914-x.
2. Wiemann, M. L., Smith, L. M., Melchior, P., Mishra-Sharma, S., Wilson, A. G., Izmailov, P., & Cuesta-Lázaro, C. **DiscoverPhysics: Benchmarking LLMs for Out-of-the-Box Scientific Thinking.** arXiv:2605.26087 (2026).
3. QpiAI. **Active-Causal-Discovery-Bench.** Public benchmark repository (2026).
