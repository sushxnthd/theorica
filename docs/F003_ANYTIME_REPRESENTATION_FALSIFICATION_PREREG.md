# THEORICA Campaign F003 — Anytime-Valid Representation Falsification

Frozen: 24 September 2026

## Method freeze

The scientific method is frozen at:

`4a25a15868a3b78f4f0fe5312ca2aaa9b4d04bf4`

File:
`src/theorica/agents/anytime_falsification.py`

Subsequent commits on this branch before F003 only added development/diagnostic
scripts or fixed their packaging. No F003 family-specific rule is permitted.

## Question

Can THEORICA begin with its ordinary explicit symbolic grammar, construct a
family-agnostic weak differential alternative, and use a statistically valid
sequence of challenge experiments to decide when the frozen explicit theory
has been falsified?

The alternative representation contains no named arctan, asinh, power-law, or
Lorentzian primitive. Its atoms remain only

    x^k D^j[y],  j <= 2, k <= 2,

with sparse support inherited from the representation-closure implementation.

## Statistical rule

After the initial measurements, both the explicit theory f and operator theory g
are frozen before challenge measurements.

For known Gaussian sensor noise sigma, THEORICA tests the composite adequacy
null

    |E[Y|x] - f(x)| <= epsilon

using the one-step e-value

    N(y ; g(x), sigma^2)
    ---------------------
    sup_{|mu-f(x)|<=epsilon} N(y ; mu, sigma^2).

The product is an e-process for predictable/adaptive experiment choices. The
campaign uses alpha = 0.01, so the explicit theory is rejected only when
log(E_t) >= log(100). Adequacy tolerance is

    epsilon = max(3 sigma, 0.003 * initial-signal-scale).

Challenge x is chosen from a public candidate pool by maximum frozen
prediction disagreement |f(x)-g(x)|. Maximum budget: 6 challenge measurements.

The synthetic benchmark supplies the exact measurement-noise standard
deviation, corresponding to a calibrated instrument-noise specification. This
assumption is part of the claim boundary.

## Completely untouched F003 family types

No execution against these family types is permitted before the official run.

### 1. Arctangent
20 tasks, seeds 40000-40019.

    y = A arctan(k x)

A has random sign and |A| in [0.6,1.4], k in [0.7,1.4].
Initial measurements: 41 points on [-1.2,1.2].
Challenge pool: [-2.5,-1.3] U [1.3,2.5].
Hidden test: 401 points on [-4,4].

### 2. Inverse hyperbolic sine
20 tasks, seeds 40100-40119.

    y = A asinh(k x)

Same A/k ranges and domains as arctangent.

### 3. Noninteger power
20 tasks, seeds 40200-40219.

    y = A x^p

x is positive. p is drawn from [0.7,3.4] subject to distance >= 0.18 from every
integer and from 0.5. Initial measurements: 41 points on [0.7,2.0].
Challenge pool: [2.1,3.3].
Hidden test: 401 points on [0.55,4.5].

### 4. Lorentzian
20 tasks, seeds 40300-40319.

    y = A / (1 + (k x)^2)

Same A/k ranges as arctangent.
Initial measurements: 41 points on [-1.2,1.2].
Challenge pool: [-2.5,-1.3] U [1.3,2.5].
Hidden test: 401 points on [-4,4].

All initial and challenge observations have independent Gaussian noise with
standard deviation 0.003 times the clean initial-signal standard deviation.

## In-language controls

20 degree-2-to-4 polynomials, seeds 41000-41019.
20 mixtures A sin(x) + B cos(x), seeds 41100-41119.

Controls use comparable initial/challenge/test geometry and the same relative
noise rule. The current explicit grammar already contains the required
structures.

## Baselines

1. Frozen explicit THEORICA theory fitted to the initial measurements only.
2. Degree-selected polynomial regression (degree 1-12), selected only using
   an internal initial-data edge split.
3. F003 anytime-valid representation falsifier.

No baseline receives the hidden family label.

## Primary success gates

F003 is positive only if every gate holds:

1. F003 beats the frozen explicit theory on at least 60/80 OOD paired tasks.
2. F003 median OOD hidden-test NRMSE <= 0.03.
3. Median OOD explicit/F003 NRMSE ratio >= 5.
4. The e-process rejects the explicit theory on at least 60/80 OOD tasks
   within the six-measurement challenge budget.
5. At most 4/40 in-language controls switch to the operator representation.
6. The paired explicit-minus-F003 improvement has a strictly positive
   bootstrap 95% CI and one-sided Wilcoxon p < 1e-6.

All family-level failures are published. Failure of any primary gate means the
campaign is reported as failed; thresholds will not be rewritten.
