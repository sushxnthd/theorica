# ACDB Canonical Paper-Panel Evaluation

## Why this run is stronger

This evaluation uses the **exact 48-instance seed map published in ACDB's `full_gpt55` run manifest**, together with the paper runner's exact runtime RNG rule:

```
runtime_seed = seed * 10000 + level * 101 + 7
```

The workflow also runs ACDB's own `pc_greedy` implementation on the same instances. Its per-level directed-F1 values reproduce the published aggregate table to rounding, validating the panel reconstruction.

GitHub Actions run: `35508894745`

Pinned ACDB commit:
`c9b3018967b6ce798f12add37120b79a963177ed`

Frozen THEORICA adapter commit:
`0bdc5a3f6ed25030622904439d375cc160faef28`

## Aggregate results

| Metric | THEORICA | Official ACDB PC-greedy |
|---|---:|---:|
| Directed F1 ↑ | 0.704 | **0.709** |
| Skeleton F1 ↑ | **0.814** | 0.813 |
| DAG SHD ↓ | 5.08 | **4.54** |
| ACDB efficiency ↑ | **0.824** | 0.730 |
| Interventions used ↓ | **2.06** | 2.54 |

## Paired inference

### Directed F1

THEORICA did **not** outperform PC-greedy in directed F1.

- mean THEORICA − PC-greedy: **−0.0048**
- bootstrap 95% CI: **[−0.0513, +0.0488]**
- one-sided Wilcoxon for THEORICA > PC-greedy: **p = 0.845**
- 14 wins / 14 ties / 20 losses

This supports neither a superiority claim nor a formal equivalence claim.

### Intervention efficiency

THEORICA used **0.479 fewer interventions per instance** on average.

Intervention reduction (positive = THEORICA better):
- mean: **+0.479**
- bootstrap 95% CI: **[+0.229, +0.750]**
- one-sided paired Wilcoxon: **p = 0.000536**
- 21 wins / 22 ties / 5 losses

ACDB's efficiency metric also favored THEORICA:
- mean gain: **+0.0944**
- bootstrap 95% CI: **[+0.0260, +0.1615]**
- one-sided paired Wilcoxon: **p = 0.00850**

### Graph-edit trade-off

The reduced intervention count did not improve every structural metric. THEORICA's DAG SHD was **0.542 worse** on average.

Using lower SHD as better:
- THEORICA improvement: **−0.542**
- bootstrap 95% CI: **[−1.021, −0.083]**

This trade-off is retained rather than hidden.

## Per-level directed F1

| Level | THEORICA | Official PC-greedy | ACDB published PC-greedy |
|---:|---:|---:|---:|
| 0 | **0.958** | 0.808 | 0.808 |
| 1 | 0.801 | **0.802** | 0.802 |
| 2 | **0.645** | 0.613 | 0.613 |
| 3 | 0.637 | **0.697** | 0.697 |
| 4 | 0.609 | **0.690** | 0.690 |
| 5 | 0.573 | **0.642** | 0.642 |

The classical baseline's reproduced values matching ACDB's published table is an important protocol check.

## Interpretation

The canonical panel changes the earlier causal story in a useful way:

- Against random intervention targeting on independently generated official configurations, THEORICA showed a clear directed-F1 gain.
- Against ACDB's stronger **PC-greedy** policy on the exact paper panel, THEORICA does **not** improve directed F1 and has worse DAG SHD.
- It does, however, achieve higher ACDB efficiency and significantly lower intervention usage.

The defensible contribution is therefore not "THEORICA beats classical causal discovery." It is that a simple ambiguity-targeting policy reaches comparable mean directed-F1 on this panel while spending fewer interventions, with a measurable structural-error trade-off that remains unresolved.

## Claim boundary

Allowed:
> On ACDB's exact 48-instance canonical paper seed panel, THEORICA achieved directed F1 0.704 versus 0.709 for the official PC-greedy baseline while using 2.06 versus 2.54 interventions; intervention count and ACDB efficiency favored THEORICA, while DAG SHD favored PC-greedy.

Not allowed:
- THEORICA beats PC-greedy overall.
- THEORICA is equivalent to PC-greedy.
- THEORICA beats GPT-5.5 or Gemini on ACDB.
- THEORICA is an official leaderboard entry.
