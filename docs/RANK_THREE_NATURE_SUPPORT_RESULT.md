# Tight four-scenario nature certificates at affine rank three

## Smallest supported claim

For a certified additive robust game whose rational scenario payoff columns have
affine dimension exactly three, every valid nature certificate can be replaced
by an exact certificate on at most four original scenarios without changing any
component-local action's expected payoff. Consequently every additive joint
action has the same expected payoff, so the replacement preserves dual
optimality and the minimax value. Four is necessary in the worst case.

THEORICA now performs this compression using exact rational arithmetic after
rank-three hull reduction, lifts the compressed weights to the original
scenario indices, and rejects the certificate if mass, nonnegativity,
barycenter, per-action expectations, or support fail exact replay.

## Proof

Let the exact projected coordinates be $z_s\in\mathbb{Q}^3$ and let $q$ be a
valid nature distribution. Its barycenter is

\[
\bar z=\sum_s q_s z_s.
\]

Caratheodory's theorem gives a distribution $q'$ supported on at most four of
the original points with the same barycenter. Every local payoff is affine in
$z_s$, say $u_{t,a}(s)=\alpha_{t,a}+\langle\beta_{t,a},z_s\rangle$. Therefore

\[
\sum_s q_su_{t,a}(s)=
\alpha_{t,a}+\langle\beta_{t,a},\bar z\rangle=
\sum_s q'_su_{t,a}(s).
\]

Additivity extends this equality to every joint action. Thus a dual-optimal
$q$ remains dual-optimal after compression. For tightness, the $4\times4$
identity payoff game has affine scenario rank three, value $1/4$, and its only
dual-optimal distribution is uniform on all four scenarios.

## Frozen evidence

| Gate | Result |
|---|---:|
| Opened exact games | 80/80 |
| Prospective holdouts | 30/30 |
| Dense 5--8 vertex interventions | 40/40 |
| Maximum compressed support | 4 |
| Tight identity witness | value $1/4$, support 4 |
| Rank-four attacks | 40/40 rejected |
| Independent Fraction-only dense checks | 40/40 |
| Independent Fraction-only holdouts | 30/30 |
| Full repository regression | 153/153 |

The prospective holdout digest is
`38913570f7d7b60a54acd06e822daa392bdb15ff6e52892c95803bb5ad145f47`.
The dense-intervention digest is
`dc93dde2bbf23cfe3bdd5bc3ae7d77c0520811a97536ef5a11294dee2b2dc558`.
The independent audit digest is
`8bdd3adc315605922e66eb9f28af959c5205a607b5f353c5ae68efc0247eb65e`.

## Alternative explanation falsified

The downstream LP solver often emits a sparse basic solution, so merely
observing small nature support would not test the mechanism. Forty interventions
instead supplied dense positive distributions on every one of 5--8 rank-three
vertices. Exact compression preserved each barycenter and reduced every case to
at most four scenarios. The four-scenario identity control then showed that the
bound cannot be improved to three.

## Novelty audit

The $d+1$ convex-combination bound is the classical Caratheodory theorem, and
computational and approximate variants are established; see Mulzer and Stein,
*Computational Aspects of the Colorful Caratheodory Theorem* (SoCG 2015),
<https://doi.org/10.4230/LIPIcs.SOCG.2015.44>, and Mirrokni et al., *Tight Bounds
for Approximate Caratheodory and Beyond* (ICML 2017),
<https://proceedings.mlr.press/v70/mirrokni17a.html>.

Sparse strategies in general games are also an established and potentially
hard optimization problem; see Afiouni et al., *Commitment to Sparse Strategies
in Two-Player Games* (AAAI 2025),
<https://ojs.aaai.org/index.php/AAAI/article/view/33474>.

The defensible contribution is narrower: a tight support law specialized to
THEORICA's exact affine-rank router, an executable rational compressor, direct
per-action replay, dense-certificate interventions, a tight lower-bound witness,
and a fail-closed rank-four boundary.

## Product consequence

Rank-three plans previously exposed an adversarial certificate on as many as
eight hull vertices. They now return a provably sufficient and worst-case-tight
four-scenario certificate. This halves the maximum counterexample explanation
without changing the policy, value, or any action expectation.

## Limits

- The result requires an exact affine-rank-three certificate and exact
  additivity. It is not a claim about arbitrary matrix games.
- Rank four may require five scenarios and is rejected by this route.
- The current hull router still caps the number of surviving vertices at eight.
- Floating geometry may propose hull candidates, but it is not trusted for
  either hull acceptance or nature compression.
- The prospective games are exact synthetic families; they do not establish
  downstream scientific usefulness on every real discovery task.

## Reproduction

```bash
python scripts/verify_rank_three_nature_support.py
python scripts/audit_rank_three_nature_support.py
pytest -q
```
