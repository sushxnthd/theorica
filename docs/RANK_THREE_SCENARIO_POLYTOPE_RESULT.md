# Exact affine-rank-three scenario polytope quotient

## Smallest supported claim

For a certified additive robust game whose rational scenario payoff columns have affine dimension exactly three, every non-vertex scenario is minimax-redundant. THEORICA now detects the rank, constructs a three-dimensional coordinate quotient, deletes only points covered by exact convex-combination certificates, solves the remaining vertices product-free when at most eight survive, lifts nature's certificate, and replays the executable policy against every original scenario.

This is not a new convex-hull, Carathéodory, minimax, or robust-optimization theorem. The contribution is an exact fail-closed router and certificate chain that makes those classical facts executable inside THEORICA.

## Law

Let each joint-action payoff be additive across components and affine in a shared scenario coordinate $z_s\in\mathbb{Q}^3$:

\[
u(a,s)=\alpha_a+\langle\beta_a,z_s\rangle.
\]

For every mixed policy, expected payoff is affine in $z_s$. Its minimum over the finite scenario set is therefore unchanged after replacing that set by the vertices of its convex hull. In three dimensions, Carathéodory membership requires supports of at most four points, permitting an exact rational deletion certificate.

Production may use floating convex-hull geometry only to propose candidates. Every proposed vertex is checked against exact rational membership, and every discarded or unproposed point must have an exact convex-combination certificate over the final vertices. A bad floating proposal therefore causes abstention rather than an incorrect reduction.

## Exact evidence

| Gate | Result |
|---|---:|
| Opened families | 80/80 exact |
| Prospective holdouts | 25/25 exact |
| Holdout ambient scenarios | 9, 12, 16, 20, 24 |
| Holdout surviving vertices | 4, 5, 6, 7, 8 |
| Strict-randomization holdouts | 20/25 |
| Rank-four attacks | 50/50 rejected before planning |
| Nine-vertex attacks | 20/20 rejected before planning |
| Independent Fraction-only audit | 8/8 |
| Independent audit digest | `0f9fa128d7ff03534005fdbaada88c30583a073bf0f70ae9a867206b5c2a75b0` |
| Full repository regression suite | 151/151 passed |

There were zero value, randomization-classification, hull, lifted-payoff, or nature-support mismatches. Observed executable-policy support was at most three; the certified general bound remains the number of surviving vertices, at most eight in this implementation.

The prospective holdout digest is `a34e3b69739649d44225a88914e6275bbd5cacb9ac6b4dc97f81434c48d39379`.

## Strongest simple baseline falsified

A coordinate-extrema heuristic retains only scenarios that minimize or maximize individual coordinates. On the frozen cubic witness it discards genuine non-axis-extreme vertices and returns value $67/38$. The exact polytope quotient returns $29/37$. Both solutions require randomization, so the discrepancy is not a classification artifact.

## Scaling consequence

For 20 binary components and 24 scenarios, THEORICA reduced the ambiguity set to eight exact vertices and certified value zero without enumerating the $2^{20}=1,048,576$ implicit joint actions. Policy recovery remained over component marginals and returned support one for this witness.

## Failed experiment preserved

The first implementation exhaustively tested every point against every four-point subset of the full ambient scenario set. It remained exact but exceeded two minutes at the frozen evaluation scale and was killed under the protocol's practicality condition.

The replacement uses numerical geometry only as an untrusted proposal generator, followed by exact rational vertex and coverage certificates. The full 105-case primary evaluation then completed in under one minute locally. This changes runtime, not the mathematical acceptance rule.

## Novelty audit

Extreme-point reduction for affine objectives and convex uncertainty sets is standard robust optimization; see Bertsimas, Brown and Caramanis, *Theory and Applications of Robust Optimization*, SIAM Review (2011), <https://epubs.siam.org/doi/10.1137/080734510>.

Carathéodory membership and its computational variants are also established; see Mulzer and Stein, *Computational Aspects of the Colorful Carathéodory Theorem* (SoCG 2015), <https://doi.org/10.4230/LIPIcs.SOCG.2015.44>, and Kalantari, *A Characterization Theorem and An Algorithm for A Convex Hull Problem* (2012), <https://arxiv.org/abs/1204.1873>.

Accordingly, the defensible contribution is narrow: exact rank detection, untrusted-proposal/exact-certificate geometry, product-free downstream integration, prospective validation, and sharp abstention boundaries.

## Limits

- Additivity must be certified; cross-component payoffs invalidate the planner.
- Affine rank below or above three is routed elsewhere or rejected.
- More than eight surviving vertices currently abstain before planning.
- Exact certificate search is fixed-dimension and is not claimed efficient for growing affine rank.
- The floating proposal layer is not trusted for correctness, but pathological numerical proposals may cause safe abstention.
- The tested families are synthetic exact rational games, not evidence for every scientific-discovery workload.

## Reproduction

```bash
python scripts/verify_rank_three_scenario_polytope.py
python scripts/audit_rank_three_scenario_polytope.py
pytest -q tests/test_robust_provenance.py
```
