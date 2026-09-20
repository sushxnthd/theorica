# THEORICA

**Autonomous Experimental Science**

THEORICA studies whether an AI scientist can **invent quantitative theories, choose informative interventions, and eventually survive contact with a real laboratory**.

The project is being developed under a hard constraint:

> **Zero personal spend.** No paid API, compute subscription, hardware purchase, domain, publication fee, or competition fee is required from the author. Paid resources may only enter through a grant, sponsor, collaborator, institution, or genuinely free tier.

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
6. Active causal discovery survived a separately frozen internal holdout and then a native ACDB execution.
7. Generic trajectory-driven physical-law identification then passed four of five native DiscoverPhysics trajectory tests.

Negative results remain part of the repository rather than being deleted after the project changes direction.

## Three research branches

### 1. Theory formation

Construct predictive symbolic relationships from a bounded compositional grammar rather than choosing among pre-written complete equations.

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

Evidence:

- `results/native/NATIVE_ACDB_REPORT.md`
- `results/native/REPLAY_PROVENANCE.md`
- `results/native/DISCOVERPHYSICS_REPORT.md`

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
