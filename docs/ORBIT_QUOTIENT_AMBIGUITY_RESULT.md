# Orbit-quotient ambiguity law and exact robust planner

## Result

Let a finite group (G) act on a finite label set (X), with point-orbits
(O_1,\ldots,O_r). Let the admissible (k)-query family be (G)-closed, and
let the convex ambiguity set of label priors be (G)-invariant. For a query
orbit (GS), define

\[
c(S)_j=\frac{|S\cap O_j|}{|O_j|},
\]

and for a prior (p), define its orbit-mass vector

\[
m(p)_j=\sum_{x\in O_j}p_x.
\]

Then robust query planning loses no value by restricting to (G)-invariant
randomized plans, and the resulting game factors exactly as

\[
\max_{q\in\operatorname{conv} C}\min_{m\in M} m\cdot q,
\]

where (C) is the set of accessible query-orbit composition vectors and (M)
is the projection of the ambiguity set to point-orbit masses. Thus the
(n)-label robust game is exactly replaced by an (r)-coordinate game. If
(M) is a polytope, only its vertices are required, and an optimal plan exists
with at most (r) query-orbit components.

### Proof

For any randomized plan μ, average all its group translates to obtain
μ̄. Because the ambiguity set is invariant,

\[
\min_{p\in P} U(\bar\mu,p)
=\min_{p\in P}\frac1{|G|}\sum_{g\in G}U(\mu,g^{-1}p)
\geq\frac1{|G|}\sum_{g\in G}\min_{p\in P}U(\mu,p).
\]

Hence an invariant plan is maximin-complete. Uniform sampling within a query
orbit includes every point of (O_j) with probability (c(S)_j), by incidence
double-counting. Its payoff against (p) is therefore exactly
(∑_j m(p)_jc(S)_j), proving the quotient factorization. Minimization of a
linear payoff over a polytope occurs at a vertex. Finally, all composition
vectors lie in the affine hyperplane
(∑_j |O_j|c_j=k), so Carathéodory gives support at most (r).

## Sharp two-by-two boundary

For two query-orbit compositions and two ambiguity vertices, let
(a_{ij}=m_j\cdot c_i). With λ the weight on (c_1), the robust value is the
maximum on ([0,1]) of the lower envelope of

\[
\ell_j(\lambda)=a_{0j}+\lambda(a_{1j}-a_{0j}).
\]

Randomization is strictly better than both pure query orbits exactly when the
two lines have opposing nonzero slopes and their crossing lies strictly inside
((0,1)). The optimal weight is the crossing

\[
\lambda^*=\frac{a_{01}-a_{00}}
{(a_{10}-a_{00})-(a_{11}-a_{01})}.
\]

This is an executable criterion: it predicts both when mixing helps and the
exact rational mixture before any query outcome is observed.

## Frozen prediction

For point-orbit sizes `(3,4)`, `k=2`, query compositions `(2/3,0)` and
`(0,1/2)`, and ambiguity vertices `(3/4,1/4)` and `(1/4,3/4)`, the protocol
predicted weights `3/7` and `4/7`. Exact execution returned value `2/7`; the
best pure value is `1/6`, for a strict gain of `5/42`. The prediction passed
unchanged.

## Exact verification

- 2,280 two-orbit rational games.
- 408 strict randomization wins and 1,872 pure-optimal controls.
- 4,560 quotient-versus-expanded-label payoff equalities, with zero mismatch.
- 2,280 support-bound checks, with zero mismatch.
- 100 three-orbit stress games; 98 required strict randomization.
- An independent standard-library checker reproduced all two-orbit values,
  strict-gain classifications, and the complete value digest.
- Duplicate primary executions were byte-identical.
- The focused production suite passed 22/22 tests; the full repository suite
  passed 114/114 tests.

The assumption boundary was also falsified deliberately. For the transposition
action on two labels and the non-invariant singleton prior `(1,0)`, an
unrestricted pure query has value `1`, while forced invariant mixing has value
`1/2`. The API therefore refuses when the invariance certificate is absent.

## Priority boundary

The broad ingredients are established: von Neumann's finite minimax theorem,
randomized decision rules, group averaging in invariant decision problems,
optimal-design symmetrization, and mixed strategies in robust optimization.
Relevant primary sources include:

- John von Neumann, *Zur Theorie der Gesellschaftsspiele*, 1928,
  https://doi.org/10.1007/BF01448847.
- Abraham Wald, *Generalization of a Theorem by von Neumann Concerning Zero
  Sum Two Person Games*, 1945, https://doi.org/10.2307/1969027.
- Jack Kiefer, *Optimum Experimental Designs*, 1959,
  https://doi.org/10.1111/j.2517-6161.1959.tb00338.x.
- Pier Giuseppe Sessa et al., *Mixed Strategies for Robust Optimization of
  Unknown Objectives*, 2020, https://arxiv.org/abs/2002.12613.
- Hiroshi Nozaki and Masanori Sawa, *Cubature formulae and designs obtained
  from group orbits*, 2011, https://arxiv.org/abs/1102.4891.

No historical novelty is claimed for those ingredients or for solving a matrix
game by linear programming. The smallest externally defensible contribution is
the exact orbit-composition specialization, its sharp certificate boundary,
and the integrated rational THEORICA planner that compresses and executes this
class of algebraically structured robust discovery problems.

## SCIENCE ledger

**True:** action invariance is sufficient for a lossless quotient from label
priors to point-orbit masses; query-orbit composition is a complete payoff
statistic; support (r) suffices; and the two-by-two strict-mixing boundary is
the interior opposing-slope crossing criterion.

**Not claimed:** a new minimax theorem, a new generic robust-optimization
principle, or a new group-averaging method.

## CONSEQUENCE ledger

THEORICA now has an exact rational planner that takes a certified finite action,
admissible query-orbit representatives, and ambiguity orbit-mass vertices. It
returns a sparse seed-executable maximin plan, its exact value, the strongest
pure-orbit baseline, and the exact randomized gain. It fails closed if the
action, priors, query family, or invariance premise is uncertified. This extends
the prior uniform-containing-ambiguity planner to general invariant polytopes.

## Limitations

- The finite group and ambiguity invariance certificate are trusted inputs.
- The ambiguity set must be supplied through exact rational orbit-mass
  vertices; continuous non-polytopal sets require a separate extreme-point
  oracle.
- Exact support enumeration is combinatorial and currently intended for
  theorem certificates and small discovery problems.
- No unopened external challenge or third-party replication was used.
- The result is internally verified and CI-gated, not peer reviewed.
