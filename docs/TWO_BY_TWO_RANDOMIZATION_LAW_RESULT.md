# Protected-pairing law for exact robust query planning

## Result

Consider two query actions evaluated against two ambiguity vertices, with
payoff matrix

\[
M=\begin{pmatrix}A&B\\ C&D\end{pmatrix}.
\]

There is a randomized policy strictly better than both deterministic actions
if and only if one of the two diagonal pairings strictly dominates the entries
outside it. Equivalently, after permuting rows and columns,

\[
\min(A,D)>\max(B,C).
\]

This **protected-pairing criterion** is invariant under relabeling. In the
displayed orientation, the exact probability on the first action and the
robust value are

\[
\lambda^*=\frac{D-C}{(A-C)+(D-B)},\qquad
v^*=\frac{AD-BC}{(A-C)+(D-B)}.
\]

The deterministic value is `max(B,C)`. Hence the strict gain is explicit: if
`B >= C`, it is

\[
\frac{(A-B)(D-B)}{(A-C)+(D-B)},
\]

and if `C >= B`, it is

\[
\frac{(A-C)(D-C)}{(A-C)+(D-B)}.
\]

## Proof

With probability `lambda` on the first action, the two ambiguity-vertex
payoffs are

\[
f_1(\lambda)=C+\lambda(A-C),\qquad
f_2(\lambda)=D+\lambda(B-D).
\]

The robust objective is the lower envelope `min(f_1,f_2)`. For an interior
point to improve strictly on both endpoints, the line that is lower at zero
must rise and the line that is lower at one must fall. Relabeling the columns
accordingly gives

\[
C<D,\quad C<A,\quad B<A,\quad B<D,
\]

which is exactly `min(A,D) > max(B,C)`. This proves necessity. Conversely,
those four strict inequalities make `f_1` rise from below `f_2` and `f_2` fall
to below `f_1`; their unique crossing is inside `(0,1)` and strictly above
both endpoint lower-envelope values. Solving `f_1=f_2` gives `lambda*`, and
substitution gives `v*`. This proves sufficiency and the formulas.

With one action there is no nontrivial distribution to choose. With one
ambiguity vertex the objective is linear in the action distribution, so a
pure action attains its maximum. Therefore two actions and two vertices are
the smallest possible strict-randomization witness; the identity payoff
matrix is one such witness.

## Exact verification

- 6,561 rational payoff matrices on the grid `{-1,-3/4,...,1}`.
- 1,752 strict-randomization cases: 876 protected-diagonal and 876 protected-
  anti-diagonal cases.
- 4,809 pure-optimal or equality-boundary controls.
- Zero criterion, value, policy, or certificate mismatches.
- An independent `Fraction`-only checker, importing no production planner,
  reproduced all counts and the complete value digest.
- The frozen orbit-quotient witness `((1/2,1/6),(1/8,3/8))` returned probability
  `3/7`, value `2/7`, best pure value `1/6`, and gain `5/42` unchanged.

## System consequence

`solve_two_by_two_robust_game` now returns the exact probabilities, value,
gain, protected pairing, and validity certificate. The orbit-quotient planner
uses it as a direct fast path whenever there are exactly two query orbits and
two ambiguity vertices, avoiding generic support/active-set enumeration while
preserving exact rational output. Equality and dominance boundaries return a
deterministic policy rather than a false strict-mixing claim.

## Priority boundary

Finite minimax and mixed strategies are classical. Von Neumann's 1928 paper
established the bilinear minimax equality; the 1948 RAND synthesis treated
finite zero-sum games and their solution methods. The present algebra is a
closed-form specialization of that classical theory, not a new minimax
theorem.

Primary sources:

- John von Neumann, *Zur Theorie der Gesellschaftsspiele*, 1928,
  https://doi.org/10.1007/BF01448847.
- H. F. Bohnenblust et al., *Mathematical Theory of Zero-Sum Two-Person Games
  with a Finite Number or a Continuum of Strategies*, RAND R-115, 1948,
  https://doi.org/10.7249/R115.

The smallest supported contribution is the permutation-invariant protected-
pairing certificate, its exact integration into THEORICA's algebraic robust
query planner, and exhaustive preservation of its sharp strict/equality
boundary.

## SCIENCE ledger

**True:** protected pairing is necessary and sufficient for strict mixing in a
two-by-two robust query game; the displayed formulas are exact; two-by-two is
minimal; the production fast path matches exhaustive exact enumeration.

**Not claimed:** historical novelty for two-by-two game formulas, minimax,
mixed strategies, or lower-envelope optimization.

## Limitations

- The law is complete only for two actions and two ambiguity vertices; larger
  games still use the general exact enumerator.
- Payoffs are assumed exact rationals.
- Verification is internal and CI-gated, not independent peer review.
- No external holdout or third-party replication was used.
