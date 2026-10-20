# Frozen protocol: two-by-two randomization law

## Active kernel

- **Precise question.** In the smallest orbit-quotient robust query game with
  two query orbits and two ambiguity vertices, what entrywise condition is
  necessary and sufficient for randomization to beat every deterministic
  query, and can THEORICA emit the exact optimal policy directly from it?
- **Best-known frontier.** Finite zero-sum minimax and closed-form solutions of
  two-by-two matrix games are classical. The preceding orbit-quotient result
  gives an opposing-slope/interior-crossing test, but not a permutation-
  invariant entrywise certificate or a dedicated exact fast path.
- **Exact objective.** Prove an if-and-only-if protected-diagonal criterion,
  prove minimality in action/vertex count, derive exact mixture/value/gain
  formulas, integrate a rational solver into the orbit planner, and obtain zero
  mismatch against exhaustive exact enumeration and an independent checker.
- **Strongest alternative explanation.** The proposed condition is only
  sufficient, misses equality/dominance boundaries, or does not change the
  executable planner beyond restating generic matrix-game algebra.
- **Cheapest decisive falsification.** Find one exact two-by-two payoff matrix
  for which the criterion disagrees with direct maximization of the lower
  envelope, or for which the formula's returned policy fails its payoff
  certificate.
- **Mechanism-derived unseen prediction.** For the already frozen orbit game,
  the payoff matrix is `((1/2,1/6),(1/8,3/8))`. Its diagonal minimum `3/8`
  exceeds its off-diagonal maximum `1/6`; the new formula must return first-row
  probability `3/7`, value `2/7`, best pure value `1/6`, and gain `5/42`.
- **Publishable threshold.** Exact iff proof and minimality boundary, exhaustive
  rational verification including equality cases, independent non-production
  checker, explicit classical-priority boundary, and reproducible CI.
- **Project-consequence threshold.** A callable exact solver must return a
  structural certificate and the orbit planner must use it as its two-by-two
  fast path while preserving every existing result.
- **Kill condition.** Any exact counterexample, any failure of the frozen
  prediction, any regression in the full test suite, or priority evidence that
  supports claiming more than a classical two-by-two specialization.

## Frozen claim

For a payoff matrix

\[
M=\begin{pmatrix}A&B\\ C&D\end{pmatrix},
\]

strict randomization advantage holds exactly when, after permuting rows and
columns if needed, both diagonal entries strictly exceed both off-diagonal
entries:

\[
\min(A,D)>\max(B,C).
\]

In that orientation the probability on the first row is

\[
\lambda^*=\frac{D-C}{(A-C)+(D-B)},
\]

and the robust value is

\[
v^*=\frac{AD-BC}{(A-C)+(D-B)}.
\]

One action or one ambiguity vertex cannot exhibit strict randomization
advantage, making two-by-two the minimal dimension.

## Frozen gates

1. The claim and frozen witness above are not changed after implementation.
2. The primary verifier uses exact `Fraction` arithmetic throughout.
3. The independent checker imports no production planner code.
4. Exhaustion includes strict, equality, dominance, diagonal, and
   anti-diagonal orientations.
5. Historical novelty is not claimed for minimax, two-by-two matrix games, or
   mixed strategies; the contribution sought is a sharp executable certificate
   inside the algebraic query-planning system.

## Holdout integrity

No external holdout is opened. The frozen orbit witness is a prospective check
of the new structural formula; exhaustive payoff panels test the theorem rather
than estimate a fitted effect.
