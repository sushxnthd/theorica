# THEORICA: Equational Structure Discovery and Theorem-Routed Active Experimentation

**Status:** field-level novelty candidate, not yet a certified field-first claim  
**Frozen evidence date:** 25 September 2026

## Research question

Can an autonomous experimental scientist infer which algebraic identities an unknown black-box operation obeys, use those empirically discovered identities to select an appropriate mathematical representation, and then design experiments in that representation more efficiently than generic function-learning baselines?

This branch differs from the earlier axiom-to-coordinate prototype in one important way: it does not begin by calling bespoke named associativity or commutativity tests. It first evaluates a bounded language of operation terms and mines empirical equalities among them.

For an unknown binary operation F, the term language contains expressions such as

- F(x,y)
- F(y,x)
- F(F(x,y),z)
- F(x,F(y,z))
- F(x,x)

The equality structure is mined from black-box measurements. Named properties are interpreted only after the equivalence relation has been observed.

## Pipeline

1. **Generic equational mining**
   Enumerate operation terms up to two applications of F and evaluate them on random assignments under measurement noise.

2. **Empirical identity graph**
   Form candidate equalities when term-pair residuals remain below the frozen noise-normalized tolerance.

3. **Theorem-premise verification**
   Candidate representation families are not accepted directly from the shallow identity miner. The system verifies additional premises such as strict monotonicity and bisymmetry, with repeat-noise calibration and targeted replicated measurements for borderline cases.

4. **Theorem routing**
   Surviving premises route the scientist to one of the currently supported representation classes:
   - additive-generator operations;
   - quasi-arithmetic means;
   - commutative semilattices;
   - unresolved / abstain.

5. **Representation-aware active design**
   For generator families, the scientist chooses new measurements to reduce uncertainty in the latent one-dimensional coordinate rather than fitting the original two-dimensional surface directly.

6. **Held-out falsification**
   The resulting representation is evaluated on fresh operation pairs and compared with random representation-space sampling, active polynomial fitting, and active Gaussian-process regression.

## Frozen structural holdout

The clean equational-discovery workflow evaluated 125 noisy structural worlds:

- 25 additive-generator operations;
- 25 quasi-arithmetic means;
- 25 commutative semilattices;
- 25 generic unresolved controls;
- 25 smooth adversarial mean-like decoys that are symmetric, idempotent, and monotone but violate the extra representation premises.

Measurement-noise standard deviation was 0.1% of the domain span.

**Result: 125/125 structural classifications correct.**

The same clean workflow then evaluated 50 hidden-coordinate worlds using a 20-measurement budget.

| Metric | Result |
|---|---:|
| Structural worlds | 125 |
| Correct structural classifications | **125/125** |
| Coordinate worlds | 50 |
| Active representation median NRMSE | **0.0006357** |
| Random representation median NRMSE | 0.001345 |
| Active degree-6 polynomial median NRMSE | 0.004679 |
| Active representation wins vs random representation | **46/50** |
| Active representation wins vs active polynomial | **50/50** |
| Median active/random error ratio | **0.514** |
| Median active/polynomial error ratio | **0.154** |
| Wilcoxon p vs random representation | **6.77e-13** |
| Wilcoxon p vs active polynomial | **8.88e-16** |

Clean workflow:
https://github.com/sushxnthd/theorica/actions/runs/36081990976

## Untouched active-GP confirmation

A separate 5000-series panel was frozen after routing changes and then executed as a confirmatory comparison against an RBF Gaussian process whose experiments are selected by posterior predictive variance.

Routing succeeded on **80/80** worlds.

At noise fraction 0.001:

| Budget | Representation median NRMSE | Active GP median NRMSE | Wins |
|---|---:|---:|---:|
| 10 | **0.000884** | 0.007677 | **40/40** |
| 20 | **0.000563** | 0.001374 | **39/40** |

At noise fraction 0.003:

| Budget | Representation median NRMSE | Active GP median NRMSE | Wins |
|---|---:|---:|---:|
| 10 | **0.002262** | 0.010334 | **40/40** |
| 20 | **0.001553** | 0.002715 | **39/40** |

All four paired one-sided Wilcoxon tests favored the representation learner, with p-values from 9.09e-13 to 4.07e-10.

Clean confirmatory workflow:
https://github.com/sushxnthd/theorica/actions/runs/36081990923

## Query-efficient theorem routing

A separately frozen router tests cheap theorem premises first, calibrates thresholds from repeated measurements, invokes expensive premises only when required, and abstains on unresolved structures.

On an untouched 6000-series confirmation panel:

- 125 worlds at noise 0.001: **125/125 correct**
- 125 worlds at noise 0.003: **125/125 correct**
- median total black-box oracle calls: **128**
- 90th percentile: **200**
- broad generic miner reference median: **1,540 calls**

The broad reference is not a separate competing published method; it is THEORICA's own generic bounded equational miner plus verifier. Its purpose is to measure the query reduction from theorem-directed sequential testing.

Clean workflow:
https://github.com/sushxnthd/theorica/actions/runs/36081990910

## Why this is a stronger scientific claim than the earlier coordinate result

The earlier coordinate experiment assumed the route "associative operation -> additive generator" was the relevant structural hypothesis.

This branch moves the decision boundary earlier.

The scientist observes a black-box operation and asks which equations among composed experiments appear invariant. Those observed equations determine which theorem premises deserve verification. Only after that evidence is obtained does the scientist choose a representation.

That changes the core inference problem from

> fit an unknown function

to

> infer the equational structure that determines which function class should even be learned.

## Literature boundary checked so far

The closest bodies of work found are:

1. **Functional Networks / associative functional networks.** These learn unknown generators for an associative operation when associativity is part of the problem statement. This is a direct predecessor to the latent-coordinate estimator, not to empirical equational-theory discovery.

2. **AI-Descartes / AI-Hilbert.** These combine data with logical or scientific background knowledge, but the background axioms are supplied to the system rather than inferred from black-box experiments.

3. **Discovering Group Structures via Unitary Representation Learning (ICLR 2025).** This learns finite group operations/representations from partial observations using a representation-specific differentiable architecture. It demonstrates that automated algebraic-structure discovery is an active field, but it does not match THEORICA's generic equation-mining -> theorem-routing -> experiment-design pipeline.

4. **Automated verification of algebraic laws.** Program verifiers can prove properties such as associativity and commutativity of known code. That is theorem verification over a provided program, not noisy experimental discovery of an unknown operation.

5. **Active learning / experimental design.** Large literatures optimize measurement locations for predictive or causal models. THEORICA's distinguishing hypothesis is that experiment design can occur **after empirical discovery of the operation's equational theory**, in the lower-dimensional representation implied by that theory.

A targeted web and academic-index search has not yet surfaced a prior paper implementing the exact full chain:

**black-box experiments -> generic empirical term equalities -> algebraic identity interpretation -> theorem-premise verification -> representation selection -> representation-space active experiment design -> held-out falsification.**

Absence from the searches is not proof of priority. This remains a candidate novelty claim pending deeper literature review and external expert scrutiny.

## Claim boundary

### Supported

- Generic shallow term equality mining can recover the tested structural distinctions under the stated noise model.
- Additional theorem premises prevent the tested adversarial mean-like decoys from being accepted as quasi-arithmetic means.
- The frozen 125-world panel achieved 125/125 correct classifications.
- The representation-aware experiment policy significantly outperformed random sampling in the same representation and an active polynomial baseline.
- An untouched confirmatory panel significantly outperformed an active RBF-GP experiment policy at both tested budgets and noise levels.
- A sequential theorem router reproduced 125/125 correctness at each of two noise levels while using a median of 128 black-box calls.

### Not established

- A universal algorithm for algebraic structure discovery.
- Coverage of arbitrary groups, rings, fields, higher-dimensional Lie structures, partial operations, stochastic operations, or discontinuous operations.
- State of the art against every modern symbolic-regression, system-identification, or active-learning method.
- Field-first priority.
- Real-world physical validation.
- A guarantee of publication, funding, admission, or external recognition.

## Field-level novelty hypothesis

The strongest defensible research hypothesis is:

> **Empirically discovered equational structure can serve as a routing layer for autonomous science: rather than fit a black-box phenomenon in its observed coordinates, an AI scientist can infer algebraic identities from experiments, use those identities to choose a representation theorem, and then allocate subsequent experiments in the theorem-induced latent coordinate.**

The existing frozen evidence makes this hypothesis worth external review. A field-level impact claim requires independent reproduction, stronger external baselines, and extension beyond the current one-dimensional operation families.
