# Translation-Action Challenge v1.1 — Frozen Failure Report

**Frozen run:** https://github.com/sushxnthd/theorica/actions/runs/36137216490  
**Artifact:** https://github.com/sushxnthd/theorica/actions/runs/36137216490/artifacts/10864982891

## Why this run is retained

Challenge v1.1 extended the public GAP benchmark beyond groups by adding:

- public faithful connected quandles;
- public nonassociative small loops;
- the original sampled SmallQuandles as out-of-promise abstention controls.

The THEORICA learner and its v1 thresholds were initially left unchanged.

The frozen gate required exact reconstruction on every eligible holdout case and
zero false acceptances on ineligible cases.

**v1.1 failed that gate.**

## Frozen result before the algorithm correction

Across **495 holdout task/repeat cases**:

| Metric | v1.1 result |
|---|---:|
| Eligible cases | 345 |
| Adaptive exact reconstructions | **297/345** |
| Random-row exact reconstructions | 296/345 |
| Ineligible cases | 150 |
| Adaptive false acceptances | **0/150** |
| Unique eligible holdout algebras | 115 |
| Unique eligible non-group holdout algebras | 35 |

Per source:

| Public source | Eligible cases | Adaptive exact |
|---|---:|---:|
| SmallGrp | 240 | **240/240** |
| Faithful connected quandles | 30 | **30/30** |
| Nonassociative SmallLoop | 75 | **27/75** |
| Sampled SmallQuandle negatives | 0 | 0 |

All **48 reconstruction failures** were public order-6 nonassociative loops.

## Failure mechanism

The full-table scorer verified that these loops satisfied the frozen compact
translation-action promise:

- all left translations were permutations;
- the carrier-to-translation map was faithful;
- the full translation group was below the 20,000-element cap;
- the full action had a small permutation base.

The failure therefore exposed a gap between the **existence theorem** and the
adaptive acquisition algorithm.

With only a partial set of acquired translations, THEORICA generated a subgroup
`H` of the true translation group. In several loops, every carrier element
could temporarily be assigned a unique element of `H` from the current base
signature even though some true translations were not in `H`.

Fresh validation correctly found a pair

```
F(x,y) != h_x(y),
```

but the original code treated that counterexample only as a reason to abstain.

## Scientific correction

For a base `B` of the current subgroup `H`, if `L_x` and candidate
`h_x in H` agree on `B` but disagree at a fresh point, then
`L_x notin H`. Otherwise the base would have forced `L_x=h_x`.

The corrected algorithm therefore uses the falsifying carrier element `x` as
the next acquisition target:

1. query the full translation `L_x`;
2. add it to the generator set;
3. regenerate the action group and base;
4. retry representation and validation.

This converts held-out falsification into active representation expansion.

The correction is formalized as Proposition 3 in
`docs/TRANSLATION_BASE_RECONSTRUCTION.md`.

## Versioning boundary

This failed run remains **Challenge v1.1**.

The corrected learner is evaluated separately as **Challenge v1.2** using the
same public corpus, split, budgets, eligibility scorer, and frozen gates.

No v1.1 result should be retroactively reported as a pass.
