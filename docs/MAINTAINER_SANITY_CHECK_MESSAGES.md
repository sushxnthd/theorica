# Benchmark-Maintainer Sanity-Check Messages

These messages are intentionally framed as requests for correction rather than promotional outreach.

## Active-Causal-Discovery-Bench

**Suggested destination:** qpiai/Active-Causal-Discovery-Bench issue tracker or maintainer contact.

**Subject/title:** Independent canonical-panel reproduction + intervention-efficiency result from THEORICA

Hi — I’m using ACDB as an external validation target for a student-led autonomous-science project called THEORICA.

I wanted to report a reproducible result and, more importantly, ask for a sanity check on whether I am interpreting your protocol correctly.

### What I ran

- pinned ACDB commit: `c9b3018967b6ce798f12add37120b79a963177ed`
- exact 48-instance seed map from `traces/ladder/full_gpt55/run_manifest.json`
- exact runtime RNG rule from `run_ladder.py`: `seed*10000 + level*101 + 7`
- ACDB's own `BenchmarkEnv`, instance builder, submission type, scorer, and official `run_pc_greedy_active` baseline
- THEORICA policy frozen before running this canonical panel

The reproduced official PC-greedy directed-F1 values match the published per-level table to rounding, which was my protocol check.

### Canonical-panel result

| Metric | THEORICA | official pc_greedy |
|---|---:|---:|
| directed F1 | 0.704 | 0.709 |
| DAG SHD | 5.08 | 4.54 |
| ACDB efficiency | 0.824 | 0.730 |
| interventions used | 2.06 | 2.54 |

I am **not** interpreting this as beating PC-greedy: directed F1 does not improve and DAG SHD is worse. The interesting part is the intervention trade-off. THEORICA uses 0.479 fewer interventions/instance on average (paired bootstrap 95% CI [+0.229,+0.750], one-sided Wilcoxon p=0.000536), while ACDB efficiency also improves.

Report:
https://github.com/sushxnthd/theorica/blob/main/results/native/ACDB_CANONICAL_PANEL_REPORT.md

Frozen runner:
https://github.com/sushxnthd/theorica/blob/main/scripts/native_acdb_canonical.py

I’d especially appreciate correction if:
1. using this seed map/runtime-seed rule this way is not equivalent to the intended canonical instance panel,
2. I am misinterpreting the efficiency comparison, or
3. there is another baseline/metric you think is essential before describing this as an intervention-efficiency trade-off.

I’m intentionally trying to keep the claim narrower than the evidence rather than turn this into a leaderboard claim. Thanks for releasing such an unusually reproducible benchmark.

---

## DiscoverPhysics

**Suggested destination:** SampsonML/DiscoverPhysics issue tracker or Matt Wiemann Sampson / benchmark authors.

**Subject/title:** Sanity check: generic 15-experiment policy passes 4/5 native trajectory evaluations on compatible worlds

Hi — I’m using DiscoverPhysics as an external target for a student-led autonomous-science project called THEORICA and wanted to ask for a sanity check on a deliberately narrow result.

Pinned DiscoverPhysics commit:
`33b7fa9df96de9c35744efd181ca7e5a8dd60ad5`

I wrote one generic system-identification policy for five static two-particle worlds that expose the same experiment interface:
- gravity
- yukawa
- fractional
- coulomb_easy
- extra_dimensions

The policy spends exactly **15 experiments/world**:
- 5 scaling interventions,
- 10 radial probes.

It estimates exposed parameter exponents plus a non-parametric radial acceleration map, freezes that model, and then submits it to DiscoverPhysics' native `Evaluator` trajectory axis.

During discovery the adapter does **not** access `true_law`, optimal explanations, explanation rubrics, or evaluator holdout trajectories.

### Native trajectory result

| world | mean particle MSE | native trajectory pass |
|---|---:|---:|
| gravity | 3.91e-10 | PASS |
| yukawa | 2.89e-05 | PASS |
| fractional | 3.39e-12 | PASS |
| coulomb_easy | 5.39e-01 | FAIL |
| extra_dimensions | 1.61e-05 | PASS |

So the narrow result is **4/5 trajectory-axis passes on this selected compatible panel**. Coulomb is retained as a failure; I have not tuned a Coulomb-specific fix after seeing it.

Report:
https://github.com/sushxnthd/theorica/blob/main/results/native/DISCOVERPHYSICS_REPORT.md

Frozen adapter:
https://github.com/sushxnthd/theorica/blob/main/scripts/discoverphysics_native_forcemap.py

I am explicitly **not** calling this an official leaderboard result, an 80% overall benchmark pass rate, or a full DiscoverPhysics pass because I did not run the separate explanation-judge axis and the panel is selected for a compatible interface.

Would you consider use of the native trajectory `Evaluator` in this way a valid external trajectory-generalization test? If there is a more appropriate no-API-cost evaluation surface in the repo, I’d be very interested in using that instead.

Thanks for making the simulator/evaluator open enough to allow this kind of adversarial replication.
