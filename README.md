# THEORICA

**Autonomous Experimental Science**

THEORICA studies whether an AI scientist can **invent quantitative theories, choose informative interventions, and eventually survive contact with a real laboratory**.

The project is being developed under a hard constraint:

> **Zero personal spend.** No paid API, compute subscription, hardware purchase, domain, publication fee, or competition fee is required from the author. Paid resources may only enter through a grant, sponsor, collaborator, institution, or genuinely free tier.

## Experimental axiom discovery and latent coordinates

THEORICA now has a separate structural-discovery branch that starts from a
black-box binary operation rather than an equation-fitting task.

The scientist experimentally tests algebraic identities, and when the evidence
supports a commutative associative structure it searches for a latent coordinate
`g` in which the observed nonlinear composition becomes additive:

```
g(F(x,y)) = g(x) + g(y).
```

It then compresses the learned coordinate into an interpretable symbolic law.
The named answer transforms are not supplied as candidates.

On the frozen clean workflow:

- **5/5** canonical black-box laws had their symbolic coordinate structure
  recovered, including logarithmic multiplication, relativistic rapidity,
  probabilistic-OR, reciprocal/harmonic, and cubic coordinates;
- **3/3** invalid structural controls were rejected;
- **50/50** unseen noisy hidden-coordinate worlds met the frozen recovery gates;
- median hidden-coordinate derivative-shape error was **0.001584**;
- median unseen composition error was **0.0003931**;
- the latent-coordinate representation beat a direct degree-6 bivariate
  polynomial baseline on **46/50** paired worlds.

This result is reproduced by
`.github/workflows/axiom_coordinate_holdout.yml` and documented in
`results/AXIOM_COORDINATE_REPORT.md`.

The representation mathematics is classical. The potentially novel research
question is the automated **experiment → axiom diagnosis → representation
choice → latent coordinate → symbolic law** chain. We do not currently claim a
certified field-first result.

## Self-expanding theory language

THEORICA now contains a narrow **grammar-closure** mechanism for a failure mode the earlier project exposed: the correct law may be outside the scientist's current hypothesis language.

On a frozen panel of **100 unseen noisy periodic-law tasks** (seeds 1000–1099), the original bounded grammar, a stronger fixed integer-frequency Fourier bank, and the adaptive spectral-closure method were evaluated on a fresh extrapolation sweep:

| Metric | Current grammar | Fixed integer bank | Spectral closure |
|---|---:|---:|---:|
| Median validation NRMSE ↓ | 0.22759 | 0.09739 | **0.002293** |
| Mean validation NRMSE ↓ | 0.25184 | 0.11720 | **0.003748** |
| Runs below 0.01 NRMSE | 1/100 | 6/100 | **97/100** |
| Paired wins by closure | — | — | **100/100 vs both** |

The method uses cross-fitted residual evidence to test whether a missing continuous frequency scale is needed, estimates that frequency from data, injects the inferred `sin(ωx)` / `cos(ωx)` operator pair into the grammar, and reruns sparse theory synthesis. Median absolute frequency error was **0.00268**; the paired NRMSE improvement over the current grammar was **0.24810** with bootstrap 95% CI **[0.21461, 0.28395]** and one-sided paired Wilcoxon **p = 1.95e-18**.

A clean GitHub Actions run reproduced the full 100-task holdout and uploaded the result artifact. This is evidence for **one bounded form of data-driven hypothesis-language expansion**, not universal operator invention or a state-of-the-art symbolic-regression claim.

## Native external evidence

### Active-Causal-Discovery-Bench

THEORICA was run against the **native ACDB package/API** on 48 paired independently generated official-configuration instances.

| Metric | THEORICA | Random target |
|---|---:|---:|
| Directed F1 ↑ | **0.647** | 0.599 |
| DAG SHD ↓ | **5.48** | 6.17 |
| Efficiency ↑ | **0.839** | 0.624 |
| Interventions ↓ | **1.83** | 2.90 |

Paired directed-F1 gain: **+0.048**, bootstrap 95% CI **[+0.0148,+0.0818]**, one-sided Wilcoxon **p=0.00195**.

The pinned replay in this repository reproduces the aggregate result exactly.

A stronger follow-up used **ACDB's exact 48-instance canonical paper seed panel** and the paper runner's runtime-seed rule. On this panel, THEORICA did **not** outperform the official PC-greedy baseline in directed F1:

| Metric | THEORICA | Official PC-greedy |
|---|---:|---:|
| Directed F1 ↑ | 0.704 | **0.709** |
| DAG SHD ↓ | 5.08 | **4.54** |
| ACDB efficiency ↑ | **0.824** | 0.730 |
| Interventions ↓ | **2.06** | 2.54 |

Directed-F1 difference was **−0.0048**, bootstrap 95% CI **[−0.0513,+0.0488]**. THEORICA used **0.479 fewer interventions per instance**, bootstrap 95% CI **[+0.229,+0.750]**, one-sided Wilcoxon **p=0.000536**; ACDB efficiency also favored THEORICA (**p=0.00850**). DAG SHD favored PC-greedy. The official PC-greedy replay matches ACDB's published per-level values to rounding, validating the reconstructed paper panel.

This is a **trade-off result**, not a superiority claim.

### DiscoverPhysics

A separate generic **15-experiment** system-identification policy was evaluated with the **native DiscoverPhysics trajectory evaluator** on five compatible static two-particle worlds.

| World | Mean particle MSE | Native trajectory threshold |
|---|---:|---:|
| gravity | **3.91e-10** | **PASS** |
| Yukawa | **2.89e-05** | **PASS** |
| fractional | **3.39e-12** | **PASS** |
| Coulomb | 5.39e-01 | FAIL |
| extra dimensions | **1.61e-05** | **PASS** |

**4/5** worlds passed DiscoverPhysics' native trajectory criterion of mean particle MSE < 0.01.

The adapter did not read the worlds' `true_law`, explanation rubric, optimal explanation, or hidden evaluator trajectories during discovery. Coulomb remains published as a failure.

This is **not** an official DiscoverPhysics leaderboard score: the full benchmark also includes an LLM-judged explanation axis, and our current panel is a selected set of compatible worlds.

## How the project got here

THEORICA did not progress through uninterrupted positive results.

1. A frozen holdout rejected our initial hypothesis that a sophisticated active-sampling heuristic reliably beats strong uniform experimental design.
2. Independent equation tasks exposed the deeper problem: a fixed hypothesis menu creates a hard ceiling on discovery.
3. We replaced complete-equation selection with bounded compositional symbolic theory synthesis.
4. The system moved from **2/8 → 8/8** on the Nguyen development suite and retained **5/5** success on a frozen coefficient-perturbed transfer split.
5. A multivariate extension solved **70/70** included two-variable runs below 0.01 NRMSE.
6. A frozen grammar-misspecification study then showed that cross-fitted spectral closure could detect a missing continuous frequency scale and repair the hypothesis language: **97/100** unseen tasks fell below 0.01 NRMSE versus **1/100** for the current grammar and **6/100** for a stronger fixed integer-frequency bank.
7. Active causal discovery survived a separately frozen internal holdout and then a native ACDB execution.
8. Generic trajectory-driven physical-law identification then passed four of five native DiscoverPhysics trajectory tests.

Negative results remain part of the repository rather than being deleted after the project changes direction.

## Three research branches

### 1. Theory formation

Construct predictive symbolic relationships from a bounded compositional grammar rather than choosing among pre-written complete equations, and test whether held-out evidence can identify specific ways that grammar must expand.

### 2. Causal experimentation

Use interventions to resolve graph orientation and causal ambiguity under a strict experimental budget.

### 3. Reality-Gap evaluation

Freeze the scientist before connecting it to physical equipment, then test whether it remains scientifically competent under calibration error, drift, saturation, noise, actuator uncertainty, and hardware faults.

## Reproduce

Install and run the public test suite:

```bash
python -m pip install -e .
pytest -q
```

Native external workflows:

- `.github/workflows/native_acdb_replay.yml`
- `.github/workflows/native_discoverphysics_forcemap.yml`
- `.github/workflows/operator_induction_holdout.yml`
- `.github/workflows/axiom_coordinate_holdout.yml`

Evidence:

- `results/native/NATIVE_ACDB_REPORT.md`
- `results/native/REPLAY_PROVENANCE.md`
- `results/native/DISCOVERPHYSICS_REPORT.md`
- `results/OPERATOR_INDUCTION_REPORT.md`
- `results/AXIOM_COORDINATE_REPORT.md`
- `docs/AXIOM_TO_COORDINATE_THEORY.md`

Read `docs/CLAIM_BOUNDARIES.md` before citing benchmark numbers.

## Physical phase

The physical experiment is preregistered **before hardware data collection** in `docs/SIM_TO_REAL_PREREGISTRATION.md`.

The first official campaign freezes the agent before connecting it to an automated optics rig. Once an official trial begins, human hints, measurement choices, selective restarts, data deletion, or hardware adjustments invalidate that trial.

Hardware will be obtained only through **grant funding, sponsorship, institutional access, or in-kind collaboration**. The author will not personally fund the rig.

## Independent replication

THEORICA actively invites attempts to reproduce or falsify the results:

- `docs/REPLICATION_CHALLENGE.md`
- GitHub issue #1

A credible negative result is treated as scientific evidence, not as something to hide.
