# Native ACDB replay provenance

THEORICA replayed the native ACDB experiment inside its own repository after publication.

- GitHub Actions run: `35507882460`
- Workflow commit: `3661c925c22da2f03b2528511b8dc5be85b66706`
- Upstream ACDB commit: `c9b3018967b6ce798f12add37120b79a963177ed`
- Replay adapter SHA-256: `f32849dee43c67e132a1775fa7855d5cc7e8270c7a146ccc884b7b1564973eb3`
- Artifact: `theorica-native-acdb-replay`

## Reproduced aggregate result

| Metric | THEORICA | Random target |
|---|---:|---:|
| Directed F1 | **0.6470411382** | 0.5990798518 |
| Skeleton F1 | 0.7900351075 | 0.7900351075 |
| DAG SHD ↓ | **5.479166667** | 6.166666667 |
| ACDB efficiency ↑ | **0.838541667** | 0.624305556 |
| Interventions ↓ | **1.833333333** | 2.895833333 |

Paired directed-F1 difference: **+0.0479612865**.

Paired bootstrap 95% CI: **[0.0147965, 0.0818129]**.

One-sided paired Wilcoxon: **p = 0.00195263**.

Pair outcomes: **21 wins / 24 ties / 3 losses**.

The replay reproduces the original native-package aggregate metrics exactly. This remains a comparison against the paired random-target policy on independently generated official-configuration instances, not an official ACDB leaderboard placement.
