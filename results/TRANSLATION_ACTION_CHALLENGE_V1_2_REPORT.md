# Translation-Action Challenge v1.2 — Public Cross-Family Result

**Date:** 25 September 2026  
**Clean workflow:** https://github.com/sushxnthd/theorica/actions/runs/36138175775  
**Artifact:** https://github.com/sushxnthd/theorica/actions/runs/36138175775/artifacts/10865079703

## Why v1.2 exists

Challenge v1.1 was intentionally frozen before the cross-family evaluation and
**failed**: THEORICA reconstructed only 297/345 eligible holdout cases. All 48
failures were public nonassociative loops.

The failure showed that a partial generated translation group can imitate the
true translations on its current permutation base even when some true
translations are still missing. Fresh validation queries found those errors,
but the old learner immediately abstained.

v1.2 changes exactly one scientific behavior:

> A validation counterexample `F(x,y) != h_x(y)` now causes THEORICA to query
> the complete falsifying translation `L_x`, enlarge the action group, and
> retry.

The public corpus, split, query budgets, eligibility scorer, random-row
baseline, and frozen success gates are unchanged from v1.1.

The mathematical justification is Proposition 3 in
`docs/TRANSLATION_BASE_RECONSTRUCTION.md`.

## Public corpus

The clean workflow regenerates all data directly from public GAP catalogues.

Total corpus: **293 public algebras**

| Source | Count |
|---|---:|
| GAP SmallGrp | 146 |
| sampled SmallQuandle controls | 100 |
| faithful connected quandles | 17 |
| nonassociative SmallLoop | 30 |

Holdout families use orders excluded from their corresponding development
portion.

The holdout contains **165 unique public algebras**. Each is evaluated under
three frozen acquisition seeds, giving **495 task/repeat cases**.

### Scoring-only compact-action promise

The learner is not told whether an algebra is a group, loop, quandle, or
whether it satisfies the reconstruction theorem.

Using the hidden full table only after evaluation, the scorer calls a case
eligible when:

1. every learner-side left translation is a permutation;
2. the carrier-to-translation map is faithful;
3. the full translation group contains at most 20,000 elements;
4. the full action has a greedy permutation base of size at most 12.

This yields:

- **115 unique eligible holdout algebras**;
- **35 unique eligible non-group holdout algebras**;
- **50 unique out-of-promise holdout controls**.

## Frozen v1.2 result

| Metric | Result |
|---|---:|
| Holdout task/repeat cases | **495** |
| Eligible cases | **345** |
| Adaptive exact reconstructions | **345/345** |
| Random-row exact reconstructions | 342/345 |
| Ineligible cases | **150** |
| Adaptive false acceptances | **0/150** |
| Median table fraction, adaptive | **13.021%** |
| Median table fraction, random-row | 15.061% |
| Mean calls on paired-exact cases, adaptive | **174.20** |
| Mean calls on paired-exact cases, random-row | 193.80 |
| Adaptive call wins / ties / losses | **98 / 225 / 19** |
| One-sided paired Wilcoxon | **p = 3.31e-14** |

The Wilcoxon comparison includes only cases in which both acquisition policies
reconstructed the hidden table exactly. This is conservative with respect to
correctness because the adaptive learner additionally succeeds on three public
group cases where the random-row baseline does not.

## Cross-family correctness

### GAP SmallGrp

- eligible cases: **240**
- adaptive exact: **240/240**
- random exact: 237/240
- adaptive median table fraction: **10.981%**
- random median table fraction: 13.021%
- mean calls on paired-exact cases: **230.16 vs 258.45**
- one-sided paired Wilcoxon: **p = 3.31e-14**

### Public faithful connected quandles

- eligible cases: **30**
- adaptive exact: **30/30**
- random exact: 30/30
- false acceptances: 0

These 30 runs correspond to **10 unique holdout quandles** of orders 8 and 9.
Their full translation groups range across sizes including 18, 36, 54, 56, and
72, and every hidden action has base size 2 under the frozen scorer.

### Public nonassociative loops

- eligible cases: **75**
- adaptive exact: **75/75**
- random exact: 75/75
- false acceptances: 0

These are **25 unique order-6 nonassociative loops**. Their translation groups
include sizes 36, 48, 360, and 720, with hidden base sizes 3–5.

This is the family that broke v1.1 and motivated counterexample-driven action
expansion.

### Sampled SmallQuandle controls

- ineligible cases: **150**
- adaptive false acceptances: **0/150**

The controls are retained from v1. They are not removed merely because they lie
outside the faithful compact-action promise.

## Query-fraction caveat on tiny non-group algebras

The faithful-quandle and loop instances are orders 8–9 and 6 respectively.
The frozen validation budget is 64 fresh queries. On such small tables this
usually exhausts every remaining unqueried entry, so the reported total query
fraction is 100% for these tiny cross-family cases.

Therefore v1.2 supports **cross-family exactness and safe abstention**, not a
subquadratic efficiency claim for the small quandle/loop instances.

The efficiency evidence remains strongest on the larger SmallGrp holdout,
where the same algorithm operates at a median **10.981%** of the table and
beats the same-representation random acquisition control.

A future larger-order quandle/loop challenge should preserve the algorithm but
use a preregistered validation fraction rather than a fixed 64-query budget if
the purpose is to measure scaling rather than exhaustive validation.

## What v1.2 establishes beyond the original BOC result

The earlier 11-operation BOC study could be criticized as a narrow collection
of hand-readable operations.

v1.2 instead evaluates a catalogue-generated public holdout:

- dozens of unseen finite groups;
- independently curated faithful connected quandles;
- independently curated nonassociative loops;
- retained out-of-promise quandle controls.

The algorithm receives none of those family labels.

The public result supports the claim that translation-base reconstruction is a
representation principle rather than a lookup rule for the five original BOC
operations.

## What it does not establish

v1.2 does not establish:

- universal finite-algebra reconstruction;
- query efficiency on tiny quandles/loops, because validation becomes
  effectively exhaustive;
- robustness to noisy or adversarially corrupted operation answers;
- superiority to specialized group/quandle/loop algorithms that are given the
  correct family in advance;
- historical first-publication priority.

## Reproducibility

The v1.2 workflow installs from scratch:

- GAP;
- SmallGrp;
- pinned RightQuasigroups v0.9.12;
- THEORICA.

It regenerates the unchanged v1.1 public corpus, runs the corrected learner and
same-representation random-row baseline, enforces the frozen gates, and uploads
the exact TSV and JSON outputs.

The failed v1.1 result is separately preserved in:

`results/TRANSLATION_ACTION_CHALLENGE_V1_1_FAILURE.md`
