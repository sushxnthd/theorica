# Frozen Frontier-Model Evaluation Protocol

## Question
Does adding THEORICA's experimental-science scaffold improve a frontier model's scientific behavior under a fixed experiment budget?

## Freeze rule
This protocol, prompts, task seeds, scoring code, and tool schemas must be committed before the first API result is inspected. After results exist, changes require a new version and a new untouched seed panel.

## Conditions
For every model and task seed run both:

1. **Vanilla** — minimal instruction: discover the hidden relationship using the laboratory tools.
2. **THEORICA scaffold** — same model and tools, plus the frozen THEORICA scientist instruction requiring competing hypotheses, discriminatory experiments, replication of suspicious observations, explicit falsification, instrument-fault hypotheses only when evidence supports them, and calibrated final uncertainty.

## Primary endpoints
- held-out predictive NRMSE
- valid discovery rate under the fixed budget
- experiment count
- unsupported-measurement claims
- fault-diagnosis precision/recall on faulted tasks

## Statistical design
- paired seeds across conditions
- report raw per-run scores
- bootstrap paired mean differences
- paired Wilcoxon as a secondary nonparametric test
- never discard valid failures

## Models
Record exact API model identifiers returned by the provider. Do not relabel aliases after the run.

## Claim boundary
A positive result supports only that the scaffold improves the evaluated model/task panel. It does not establish general autonomous-science superiority.
