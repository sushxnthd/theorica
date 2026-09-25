# Translation-Action Challenge v1 — Frozen Public-Corpus Result

**Date:** 25 September 2026  
**Clean workflow:** https://github.com/sushxnthd/theorica/actions/runs/36135938536

## Corpus

The corpus was generated in a clean GitHub Actions runner directly from pinned
public GAP catalogues:

- GAP SmallGrp;
- RightQuasigroups 0.9.12 SmallQuandle.

The frozen corpus contains **246 public algebras**:

- development: 66 SmallGrp groups + 50 sampled SmallQuandles;
- holdout: 80 SmallGrp groups + 50 sampled SmallQuandles.

Holdout orders were distinct from development orders.

Each holdout algebra was evaluated under three fixed acquisition seeds, giving
**390 holdout task/repeat cases**.

SmallQuandle tables were transposed solely to align the package's
right-translation convention with THEORICA's left-translation convention.

## Frozen scoring promise

Full tables were available only to the benchmark scorer.

An algebra counted as eligible when:

1. every learner-side left translation was a permutation;
2. the carrier-to-translation map was faithful;
3. the full translation group had at most 20,000 elements;
4. the action had a greedy base of size at most 12.

The learner did not receive source labels, GAP ids, full-table eligibility, or
the full table.

## Result

| Metric | Frozen holdout result |
|---|---:|
| Holdout task/repeat cases | **390** |
| Eligible cases | **240** |
| Ineligible cases | **150** |
| Adaptive exact reconstructions on eligible cases | **240/240** |
| False acceptances on ineligible cases | **0/150** |
| Median queried table fraction, adaptive | **10.981%** |
| Median queried table fraction, random-row baseline | 13.021% |

The same-representation random-row baseline also reconstructed all 240 eligible
cases exactly.

Paired query-count outcomes among those 240 exact/exact comparisons:

- adaptive lower cost: **98**
- tie: **123**
- adaptive higher cost: **19**

Thus unresolved-signature targeting is beneficial on many cases, but the public
challenge does **not** support a claim of universal query reduction over random
row acquisition. The median paired call ratio is exactly 1.0 because most cases
tie.

## Important limitation exposed by v1

The **80 unique eligible holdout algebras are exactly the 80 SmallGrp groups**.

The 50 sampled SmallQuandles are all outside the frozen faithful compact-action
promise and were correctly rejected on all three repeats. This is a useful
abstention result but it means v1 does **not** establish positive reconstruction
transfer to a quandle family.

That limitation is retained publicly rather than obscured by reporting only the
aggregate 240/240 number.

## Next frozen extension

Challenge v1.1 therefore keeps the original nonfaithful/ineligible quandle
samples as negative controls and adds:

- public **faithful connected quandles** selected using the package's
  `IsFaithfulRightQuasigroup` property;
- public nonassociative small loops.

The THEORICA reconstruction algorithm and its thresholds are not changed for
this extension.

## Reproducibility

The workflow installs:

- Ubuntu GAP;
- SmallGrp;
- pinned RightQuasigroups 0.9.12;

then regenerates the public corpus and evaluates both acquisition policies from
scratch.

Artifact:
https://github.com/sushxnthd/theorica/actions/runs/36135938536/artifacts/10864950508
