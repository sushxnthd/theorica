# Representation Closure v2 — Frozen Long-Range Holdout

Date frozen: 24 September 2026

## Scientific change from failed v1

v1 failed its preregistered 60/80 paired-win gate. Its negative result is
preserved in `results/REPRESENTATION_CLOSURE_V1_FAILURE.md`.

v2 changes exactly one decision rule motivated by that failure:

> THEORICA may change representation only if the existing explicit symbolic
> language is itself falsified on held-out edge probes.

The new absolute inadequacy threshold is explicit edge-validation
NRMSE >= 0.01, in addition to the existing requirements that the operator
candidate achieve NRMSE <= 0.08 and <= 0.50 times the explicit error.

Frozen implementation commit:

`00d89b9613ce0e1443226f11217c1274a7664f75`

No scientific method or gate changes are permitted after the v2 holdout is
first executed.

Pre-holdout CI note: the first v2 workflow stopped at the regression-test stage before the holdout runner executed. The old Airy test asserted that operator mode must always be selected; this conflicts with v2's new absolute falsification gate. Commit `1a32b95beb985601c87f2ed92d6810d5cffe1bb4` changes only that test expectation to require accurate prediction, not a forced representation. The v2 algorithm, gates, families, seeds, and benchmark script were unchanged.

## Research question

Can a family-agnostic differential meta-language recover governing structure
that is absent from THEORICA's explicit grammar, using a small set of edge
experiments to falsify the original representation, and then extrapolate much
farther than the measurements used for theory construction?

The meta-language still contains only

[
x^k D^j[y], qquad j\le2,quad k\le2,
]

with at most four active terms. It contains no Gaussian, erf, Dawson, sinc, or
special-function primitive.

## Untouched out-of-language families

These four family types have not been executed against the frozen v2
implementation before this preregistration.

### Gaussian

20 tasks, seeds 20000-20019.

- training x: [-1.5, 1.5], 81 points
- hidden test x: [-3.0, 3.0], 401 points
- y = A exp[-a(x-b)^2]
- a ~ U[0.45,1.10], b ~ U[-0.25,0.25]
- |A| ~ U[0.6,1.4], random sign

### Error function

20 tasks, seeds 20100-20119.

- training x: [-1.5, 1.5]
- hidden test x: [-3.0, 3.0]
- y = A erf(kx+s)
- k ~ U[0.60,1.30], s ~ U[-0.30,0.30]

### Dawson function

20 tasks, seeds 20200-20219.

- training x: [-1.5, 1.5]
- hidden test x: [-3.0, 3.0]
- y = A Dawson(kx+s)
- k ~ U[0.60,1.20], s ~ U[-0.25,0.25]

### Sinc / spherical-j0 form

20 tasks, seeds 20300-20319.

- training x: [0.50, 3.00]
- hidden test x: [0.30, 6.00]
- y = A sin(kx)/(kx)
- k ~ U[0.80,1.40]

All tasks use independent Gaussian measurement noise with standard deviation
0.3% of the clean training-signal standard deviation.

## In-language specificity controls

20 degree-2-to-5 polynomial tasks, seeds 21000-21019:

- training [-1.5,1.5]
- hidden test [-3,3]

20 fixed-frequency trigonometric mixtures, seeds 21100-21119:

- training [-2,2]
- hidden test [-4,4]
- y = A sin(x) + B cos(x) + c x + d

## Comparators

1. current bounded THEORICA symbolic synthesis, trial width 200;
2. polynomial regression with degree 1-12 selected by held-out training-edge
   error;
3. v2 falsification-gated representation closure.

No comparator receives the hidden family label.

## Frozen primary success gates

All must hold:

1. closure beats current THEORICA on at least 60/80 OOD paired tasks;
2. median OOD closure NRMSE <= 0.02;
3. one-sided paired Wilcoxon p < 0.01 and the 95% bootstrap CI for mean
   explicit-minus-closure NRMSE is strictly positive;
4. at least 38/40 in-language controls remain in explicit mode;
5. median in-language closure NRMSE is no worse than 1.10 times the current
   explicit median.

The complete family breakdown is reported whether positive or negative.
