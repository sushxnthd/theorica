# Decision-identifiable list decoding

## Theorem

Fix a certified rational feature span, a two-action payoff game, a query
transcript, and row-error/erasure budgets. Let \(\Theta\) be the finite set of
all feature-span payoff completions consistent with that transcript and budget.
For each \(\theta\in\Theta\), let \(v_\theta\) be its exact robust value and
\(P_\theta\subseteq[0,1]\) its set of optimal probabilities on action zero.

An exact transcript-only robust value and executable policy exist if and only if

1. every \(v_\theta\) is the same value \(v\); and
2. \(\bigcap_{\theta\in\Theta}P_\theta\ne\varnothing\).

For two actions, every \(P_\theta\) is an exact closed interval. If scenario
\(j\) has action payoffs \((a_j,b_j)\), the constraints

\[
b_j+p(a_j-b_j)\ge v
\]

give its lower and upper endpoints directly. The common-policy test is therefore
the closed-form boundary

\[
\max_\theta L_\theta\le \min_\theta U_\theta.
\]

## Proof

If the values agree and the intervals intersect, choose any probability in the
intersection. It attains \(v\) in every feasible completion, so both the value
and policy are certified without identifying the model.

Conversely, unequal values give two feasible worlds in which the same transcript
requires different exact answers. Equal values with disjoint optimal-policy
sets give feasible worlds with no policy optimal in both. A transcript-only
exact procedure must therefore abstain in either case. This proves necessity and
sufficiency.

## Executable result

THEORICA now enumerates the bounded exact algebraic version space using shared
row-corruption locations, solves every completion with its rational robust-game
solver, derives each complete optimal interval, and either returns a common exact
policy or a machine-readable abstention reason.

| Gate | Result |
|---|---:|
| Opened affine positive cases | 40/40 |
| Prospective quadratic-family holdouts | 20/20 |
| Non-identifiable payoff models in positive cases | 60/60 |
| Unique-model decoder abstentions | 60/60 |
| Unequal-value attacks rejected | 20/20 |
| Equal-value/disjoint-policy attacks rejected | 20/20 |
| Independent Fraction-only audit | 60/60 positives, 40/40 attacks |
| Independent production imports | 0 |
| Primary evidence digest | `647d2f5b8a0b65a3249eee5a5229a3b5af173d6d2c7cf58aea4fdc5fa75eeaa7` |
| Independent audit digest | `e667d8acfd0d049edfbe88af9d7549d7fbfa3d69cdbffbff33cb1bf2bdf6fb6b` |

The quadratic holdouts use rank-three feature rows and only four observations
under one possible corruption. Unique model correction would require five MDS
queries, yet the robust decision and value are exact after four because all four
feasible polynomial completions share the same optimal policy and value.

## Direct consequence

Corruption no longer forces THEORICA to equate model uncertainty with decision
uncertainty. The planner can act one query before worst-case unique decoding in
the certified holdout family, while failing closed on indistinguishable worlds
whose values differ or whose optimal policies do not overlap.

## Limits and novelty boundary

Version-space reasoning and list decoding are established ideas. Guruswami's
folded Reed--Solomon work explicitly formalizes returning all codewords with
sufficient agreement rather than forcing a unique decode
(`arXiv:cs/0511072`). Decision-focused learning likewise distinguishes
prediction fidelity from downstream decision quality. Most directly,
*Geometric Identification in Predict-Then-Optimize Learning*
(`arXiv:2609.33472`) studies how multiple reports can induce the same optimal
decision and characterizes quotient-report identification for the SPO+ population
risk. That work is about learning-risk geometry, not adversarial feature-code
transcripts or exact robust-plan certification.

Accordingly, we do **not** claim novelty for list decoding, decision equivalence,
or optimal-face geometry. The bounded contribution is the exact corrupted-query
robust-decision quotient, its necessary-and-sufficient two-action interval
criterion, algebraic completion enumerator with shared row faults, matched
indistinguishable-world witnesses, and fail-closed execution path. A broader
priority search is still required before any publication-level novelty claim.

The implementation is limited to one two-action
component, exact rational features, certified span membership, explicit
error/erasure budgets, and at most 10,000 candidate pairs. It does not cover
approximate rank, noisy real arithmetic, unknown feature maps, probabilistic
corruption, or general multi-action policy-polytope intersection.
