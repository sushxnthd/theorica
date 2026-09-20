# Native ACDB result

On 2026-09-20, THEORICA was executed against the **native Active-Causal-Discovery-Bench package/API** in an isolated GitHub Actions run.

Protocol:
- 6 official v1 ACDB level configurations
- 8 independently generated accepted seeds per level
- 48 paired benchmark instances
- identical observational data and native ACDB sampling/scoring APIs for both policies
- comparison: THEORICA ambiguity-targeting vs random intervention targeting

Result:
- directed F1: **0.6470 vs 0.5991**
- paired mean directed-F1 gain: **+0.0480**
- bootstrap 95% CI: **[+0.0148, +0.0818]**
- one-sided paired Wilcoxon: **p = 0.00195**
- DAG SHD: **5.48 vs 6.17**
- interventions used: **1.83 vs 2.90**
- ACDB efficiency: **0.839 vs 0.624**

Upstream ACDB commit:
`c9b3018967b6ce798f12add37120b79a963177ed`

THEORICA native adapter SHA-256:
`882668a02041fceb8c462b130e5dc10e10972c39179664fab81f88b57829b8f2`

This is a native package/API result against a paired random-target baseline. It is **not** an official ACDB leaderboard placement and should not be compared numerically to leaderboard model scores obtained on different seed manifests/panels.
