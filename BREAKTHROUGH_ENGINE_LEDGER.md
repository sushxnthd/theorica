# Breakthrough Engine Research Ledger: Identifiability / Abstention

Date: 2026-09-25
Status: exploratory development only. No confirmatory holdout opened.
Isolation: this branch is independent of THEORICA main and all active/frozen experiments.

## Motivation

A development-only attempt to generalize THEORICA's successful spectral closure into generic missing-operator-family induction failed asymmetrically: periodic structure was much easier to identify than exponential, rational, and logarithmic families. This suggests an identifiability problem rather than merely a classifier problem.

## Mechanistic hypothesis

On a bounded interval around zero, common smooth operator families become locally confounded after a low-order polynomial scaffold is fit. For example,

log(1+a x^2) = a x^2 - (a^2/2) x^4 + O(x^6)

and

1/(1+a x^2) = 1 - a x^2 + a^2 x^4 + O(x^6).

If the discovery grammar already contains constant and x^2 terms, the leading family-specific signal begins at order x^4. Under Gaussian measurement noise, squared discrimination signal therefore scales as O(R^8) with experimental radius R in this local regime. A system should not confidently expand its grammar when this signal is below its noise/evidence floor.

This is a mathematical mechanism to test, not yet a novelty claim.

## Development simulation

A fresh local simulation compared four nonlinear families (exponential, rational, logarithmic, sinusoidal) on noisy observations with an affine/quadratic scaffold. After three additional measurements:

- random extrapolation: exp 88/100, rational 66/100, log 61/100, sinusoidal 100/100
- disagreement-maximizing active points: exp 99/100, rational 75/100, log 60/100, sinusoidal 100/100

This is development evidence only. It indicates that naive active disagreement can nearly resolve exponential and periodic cases while leaving rational/logarithmic ambiguity largely intact.

## Prior-art audit

The active-model-discrimination direction is not cleanly novel. A 2026 Biotechnology and Bioengineering paper on automated data-efficient symbolic regression explicitly evaluates model-based design of experiments for discrimination between SR models and reports that experiments chosen to distinguish early imperfect models may fail to guide recovery of the true structure. LLM-ACES (2026) also frames symbolic equation discovery as an identifiability problem and uses closed-loop adaptive search. Recent equation-discovery work further discusses provable identifiability under structural families.

Therefore the project must NOT claim novelty for "active symbolic regression", "model discrimination for symbolic regression", or "identifiability-aware equation discovery" in general.

## Surviving research question

A potentially narrower contribution remains open:

Can an autonomous equation-discovery system estimate an evidence-based *identifiability certificate* for a proposed grammar expansion, abstain when operator families are locally observationally equivalent, and request an intervention only when a predeclared information-gain threshold predicts that the ambiguity is resolvable?

The target contribution would be a calibrated abstention/certificate protocol, not another active-learning heuristic.

## Next falsification step

Before opening any holdout:
1. derive an explicit finite-noise distinguishability bound for matched Taylor families;
2. test whether the bound predicts empirical family confusion across interval radius and noise level;
3. compare against bootstrap model-selection confidence and raw predictive disagreement;
4. measure calibration: among cases declared identifiable at confidence q, does the selected family achieve approximately q correctness?;
5. include null tasks where the base grammar is already sufficient, to measure false grammar expansion.

Only if the certificate is calibrated on development tasks should a preregistered unopened confirmation panel be frozen.

## Claim boundary

There is no breakthrough claim at this stage. The active-discrimination idea overlaps prior art. The local Taylor-confounding mechanism and a calibrated abstention certificate are hypotheses requiring formalization, prior-art review, and prospective validation.
