# Prospective Public-Catalogue Validation of Nonfaithful Reconstruction

**Result date:** 13 October 2026  
**Status:** **PASS — 7/7 frozen scientific gates**

## Supported claim

On 159 previously unopened nonfaithful quandles of orders 8 and 9 from GAP
RightQuasigroups v0.9.12, THEORICA's certified-generator reconstruction path
recovered every complete operation table exactly.  A separately implemented
base-signature reconstruction agreed on every case.  Every reconstruction used
fewer queries than complete-table disclosure, with a median reduction of
44.44%.

This prospectively validates the corrected scoped theorem on an external
public catalogue and changes THEORICA's supported reasoning scope beyond
faithful translation actions.

## Decisive table

| Frozen measure | Required | Observed | Gate |
|---|---:|---:|---:|
| Eligible unopened nonfaithful quandles | >=50 | **159** | PASS |
| Production exact reconstruction | 100% | **159/159** | PASS |
| Independent exact agreement | 100% | **159/159** | PASS |
| Cases below full-table queries | >=90% | **159/159** | PASS |
| Median query reduction | >=25% | **44.44%** | PASS |
| Old learner acceptances | 0 | **0/159** | PASS |
| Overlap with opened v1 IDs | 0 | **0** | PASS |

The smallest and largest observed query reductions were 25.00% and 76.5625%.
Of 160 frozen catalogue IDs, 159 met the nonfaithful eligibility condition;
the single faithful case was excluded by the preregistered rule.

## Mechanism evidence

- Group sizes ranged from 3 to 40.
- Base sizes were 1–4: 3 cases of size 1, 56 of size 2, 96 of size 3, and 4
  of size 4.
- Deterministic generator certificates used 1–4 rows: 6 cases used 1, 57 used
  2, 92 used 3, and 4 used 4.
- The old learner rejected every case as
  `nonfaithful_or_unresolved_translation_action`.

The result therefore supports the predicted mechanism: after generator
completeness is certified, a small group base resolves repeated translations
without querying the full table.

## SCIENCE ledger

- **KNOWN:** the corrected theorem transfers prospectively from exhaustive
  synthetic domains to 159 unseen public nonfaithful quandles.
- **KNOWN:** independent reconstruction and production reconstruction agree on
  all cases.
- **KNOWN:** the old faithfulness gate excluded all 159 recoverable cases.
- **FALSIFIED:** nonfaithful public quandles are necessarily outside useful
  translation-base reconstruction scope.
- **UNTESTED:** automatic generator-completeness certification from partial
  queries, larger orders, non-quandle nonfaithful families, and noisy or
  corrupted oracles.

## CONSEQUENCE ledger

- THEORICA may now advertise exact certified reconstruction for faithful and
  nonfaithful permutation-translation operations.
- The certified path should be exposed separately from automatic discovery;
  a generator certificate is a real capability input, not hidden tuning.
- Future benchmark design should distinguish `certified reconstruction` from
  `unknown-group discovery` rather than using faithfulness as a blanket scope
  boundary.

## Provenance and reproducibility

- Frozen protocol commit: `3053017c90d1a00f0ae15e68aeeb3290a815b021`
- GitHub Actions run: `38389293608`
- Workflow artifact SHA-256:
  `7318c687f917c54cb0e900f4ff79def09b11de2891aa112e0ec8d29d444884d9`
- Canonical payload digest:
  `b4b67b5ad81b6cbbf5601f7a90412434750423f0d1c5752955d77fa3d8355e30`
- Result-file SHA-256:
  `977f7ff6802a5571ca46981ca730ec695d51b652d36c5ae5aa4293fa178ebe8f`
- Corpus SHA-256:
  `40e8e520946e5e657f1b3cf2979ce2b9c1168de270f382ca1b0988c99d221bff`
- Two complete evaluation executions within the workflow were byte-identical
  by the frozen `cmp` gate.

```bash
gap -q scripts/export_gap_nonfaithful_public_holdout.g
python scripts/nonfaithful_public_holdout.py
cp results/nonfaithful_public_holdout.json /tmp/run1.json
python scripts/nonfaithful_public_holdout.py
cmp /tmp/run1.json results/nonfaithful_public_holdout.json
```

## Limitations

This is not automatic discovery: the evaluator derives and supplies a complete
generator certificate from each public table.  The result does not prove
historical novelty, performance on large algebras, robustness to noise, or
superiority to specialized quandle algorithms given family labels.  The
overall field-level breakthrough gate remains **INCONCLUSIVE** pending a
primary-literature priority audit and validation of certificate acquisition
from partial queries.

