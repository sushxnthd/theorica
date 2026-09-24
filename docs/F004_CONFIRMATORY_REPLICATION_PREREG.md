# THEORICA Campaign F004 — Exact-Method Confirmatory Replication

Frozen: 24 September 2026

F004 is a confirmatory replication of F003. It does **not** claim new family
zero-shot transfer. It asks whether the F003 result survives an entirely fresh
parameter/measurement-noise draw with the scientific method unchanged.

## Frozen method

Exact F003 method commit:

`4a25a15868a3b78f4f0fe5312ca2aaa9b4d04bf4`

No algorithm, operator grammar, e-process, tolerance, alpha, query policy, or
experiment budget is changed.

## Fresh seeds

The same four OOD family generators are used with disjoint seeds:

- arctan: 50000-50019
- asinh: 50100-50119
- noninteger power: 50200-50219
- Lorentzian: 50300-50319

Fresh controls:

- polynomial: 51000-51019
- sin/cos: 51100-51119

Domains, parameter distributions, 0.3% Gaussian noise, challenge pools, hidden
test domains, and six-measurement maximum budget are identical to F003.

## Confirmatory gates

F004 is positive only if all hold:

1. F004 beats frozen explicit THEORICA on at least 65/80 OOD tasks.
2. Median OOD F004 NRMSE <= 0.03.
3. Median explicit/F004 error ratio >= 7.
4. At least 55/80 OOD explicit theories are rejected within six probes.
5. At most 3/40 in-language controls switch representation.
6. Bootstrap 95% CI for mean paired improvement is strictly positive and
   one-sided Wilcoxon p < 1e-8.

The complete result is retained regardless of outcome.
