# Representation Closure v1 — Frozen Holdout Failure

Date: 24 September 2026

Official run: GitHub Actions run 36036055450.

The campaign was preregistered before execution and **failed** its primary
success gate. The failure is retained.

## Aggregate result

| Metric | Value |
|---|---:|
| OOD tasks | 80 |
| Current symbolic median NRMSE | 0.0039741 |
| Closure median NRMSE | 0.0027072 |
| Degree-12 polynomial median NRMSE | 0.0042699 |
| Closure wins vs current symbolic | **36/80** |
| Closure wins vs polynomial | 49/80 |
| Operator selected | 56/80 |
| Mean paired improvement vs symbolic | +0.0034022 |
| Bootstrap 95% CI | [0.0015333, 0.0057112] |
| One-sided paired Wilcoxon | p = 0.0005359 |
| In-language controls retained explicit | 33/40 |

The preregistered gate required at least **60/80** OOD paired wins, so the
campaign is a negative result despite the positive aggregate error shift.

## Family results

- Hermite: median 0.00851 → 0.00313; 10/20 paired wins.
- Laguerre: median 0.01167 → 0.00380; 13/20 paired wins.
- 1F1: median 0.00133 → 0.00095; 9/20 paired wins.
- Modified Bessel: median 0.00338 → 0.00355; 4/20 paired wins.
- Polynomial controls: 0 unnecessary operator selections.
- Trigonometric controls: 7 unnecessary operator selections; all seven hurt
  held-out performance.

## Diagnosis fixed before v2

The failure showed that a relative improvement gate alone is not a valid test
that the current representation is inadequate. On some already-expressible
tasks, noise made the operator representation look better on the small edge
validation split even though the explicit theory extrapolated better.

v2 therefore adds one scientifically motivated condition before any
representation change:

> the existing symbolic language must itself fail an absolute held-out
> adequacy threshold.

This is not a post-hoc rewrite of v1. v1 remains failed. v2 uses new family
types and new seeds in a separately preregistered campaign.
