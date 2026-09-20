# Native ACDB evaluation report

## Status

**Native third-party package execution: COMPLETE.**

Original GitHub Actions run: `35505166307`

The run cloned and installed the official `qpiai/Active-Causal-Discovery-Bench` repository, then used its native APIs for benchmark generation, intervention sampling, graph submission and scoring.

Upstream benchmark commit:

`c9b3018967b6ce798f12add37120b79a963177ed`

Frozen THEORICA adapter SHA-256 from the original run:

`882668a02041fceb8c462b130e5dc10e10972c39179664fab81f88b57829b8f2`

## Protocol

- Official ACDB v1 level configurations, levels 0-5.
- 8 independently generated accepted seeds per level.
- 48 paired benchmark instances total.
- Same native ACDB instance for THEORICA ambiguity-targeting and random intervention targeting.
- Native ACDB `sample_interventional_data`, `GraphSubmission`, and `score_submission`.
- This is a **native-package evaluation on independently generated official-config instances**, not an official leaderboard submission or the canonical paper seed map.

## Result

| Metric | THEORICA ambiguity targeting | Random targeting |
|---|---:|---:|
| Directed F1 | **0.647** | 0.599 |
| Skeleton F1 | 0.790 | 0.790 |
| DAG SHD (lower better) | **5.48** | 6.17 |
| Efficiency | **0.839** | 0.624 |
| Interventions used | **1.83** | 2.90 |

Paired directed-F1 mean difference: **+0.04796**.

Bootstrap 95% CI (20,000 paired bootstrap resamples): **[+0.01480, +0.08181]**.

One-sided paired Wilcoxon: **p = 0.00195**.

Paired outcomes: **21 wins / 24 ties / 3 losses**.

The policy also reduced DAG SHD by 0.6875 on average and used 1.0625 fewer interventions per instance on average.

## Claim boundary

Allowed: *“THEORICA was executed against the native ACDB package on 48 independently generated official-configuration instances and outperformed a paired random-intervention baseline in directed F1 and intervention efficiency.”*

Not allowed: *“THEORICA is #1 on ACDB”*, *“THEORICA beat GPT-5.5”*, or *“official ACDB leaderboard score”*. The public ACDB leaderboard uses its own canonical seed manifest and agent panels.
