# Cross-fitted spectral closure: frozen holdout

Date: 24 September 2026

## Question

Can THEORICA detect that its current symbolic language is missing a continuous
frequency scale, estimate that scale from held-out evidence, add the missing
operator to its own grammar, and recover an out-of-language periodic law?

This is a deliberately narrow test of **data-driven hypothesis-language
expansion**. It is not a claim of universal operator invention.

## Frozen design

- 100 unseen tasks, seeds 1000-1099.
- 40 noisy training measurements on x in [-2, 2].
- Fresh noiseless validation on 401 points spanning [-2.5, 2.5].
- Hidden laws: A sin(omega x + phase) + b x + c.
- omega sampled continuously from [1.35, 5.65].
- Measurement noise: Gaussian, sigma = 1% of the clean training-output standard deviation.
- Expansion gate fixed at cross-fitted augmented/base MSE ratio < 0.20.
- No target equation or target frequency is stored in the grammar.

Two baselines were used:

1. **Current THEORICA grammar**, with trial width increased from 30 to 200 to
   make the baseline stronger.
2. **Fixed integer Fourier bank**, which additionally preloads sin(kx), cos(kx)
   for k = 2,...,6, also with trial width 200.

The adaptive method uses a cubic two-fold diagnostic scaffold only to test for
persistent periodic structure. It searches omega continuously, then injects the
data-estimated sin(omega x), cos(omega x) pair into the full THEORICA grammar
and re-runs sparse theory synthesis.

## Result

| Metric | Current grammar | Fixed integer bank | Spectral closure |
|---|---:|---:|---:|
| Median validation NRMSE | 0.22759 | 0.09739 | **0.002293** |
| Mean validation NRMSE | 0.25184 | 0.11720 | **0.003748** |
| Runs below 0.01 NRMSE | 1/100 | 6/100 | **97/100** |
| Paired wins by closure | - | - | **100/100 vs both** |

Frequency recovery:

- Median absolute |omega_hat - omega|: **0.00268**
- 90th percentile absolute error: **0.02494**

Against the current grammar, mean paired NRMSE improvement was **0.24810**,
with bootstrap 95% CI **[0.21461, 0.28395]**. One-sided paired Wilcoxon
p = **1.95e-18**.

Against the stronger fixed integer-frequency bank, the closure method also won
100/100 paired tasks; one-sided paired Wilcoxon p = **1.95e-18**.

## What changed scientifically

The earlier THEORICA result showed that a fixed hypothesis language creates a
hard ceiling: experiment selection cannot recover a law the language cannot
express.

This experiment supplies the next missing link. On this controlled failure
mode, THEORICA no longer merely searches a fixed grammar. It can use held-out
prediction failure as evidence about the grammar itself, estimate a missing
continuous operator parameter, change the language, and then recover a law that
the original language extrapolates poorly.

That is a project-level breakthrough because it changes the object being
optimized from **"which theory inside H?"** to **"is H itself wrong, and how
should it change?"**

## Claim boundaries

Supported:

- Cross-fitted evidence can trigger a narrow periodic grammar expansion.
- Continuous frequency induction strongly improves this frozen synthetic
  misspecification panel.
- The effect survives a substantially stronger fixed-language baseline.

Not supported:

- universal operator invention;
- state-of-the-art symbolic regression;
- a claim that this mechanism is field-first;
- generalization from periodic structure to arbitrary missing mathematical
  operators;
- physical sim-to-real transfer.

The next valid extension is a leave-one-operator-family-out panel covering
periodic, exponential, rational, and fractional-power misspecification, frozen
before evaluation. Physical Rig 001 remains a separate preregistered test.
