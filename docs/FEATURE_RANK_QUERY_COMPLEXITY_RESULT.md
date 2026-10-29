# Optimal feature-rank query complexity for robust planning

## Smallest supported claim

Let `Phi` be a known rational scenario-feature matrix with `m` rows, arbitrary
width `p`, and exact row rank `r`.  Assume an external certificate establishes
that every component-local action payoff lies in the column space of `Phi`, and
that total payoff is additive across components.  THEORICA can reconstruct the
entire local payoff table using exactly `r` scenario-oracle calls, independent
of `m` and `p`.  In the worst case, no deterministic exact algorithm using
fewer than `r` calls can guarantee even the robust value.

This strictly subsumes the preceding affine law.  For affine descriptors
`z_s in Q^d`, `Phi_s=(1,z_s)` and `r=d+1`.  The feature-rank form additionally
covers certified polynomial and mechanistic feature maps and does not pay for
linearly redundant feature columns.

## Proof

Choose `r` linearly independent rows of `Phi`.  Every scenario row is an exact
rational linear combination of those basis rows.  A local payoff vector has
the form `Phi c`; therefore applying the same row combination to the `r`
queried payoff values reconstructs its value at every unqueried scenario.  The
argument holds simultaneously for every local action, so the reconstructed
robust game is identical to the full-table game.

For necessity, expose any deterministic algorithm to an all-zero transcript
for fewer than `r` queries.  Its queried feature rows span a proper subspace of
the row space.  Linear algebra supplies a nonzero payoff functional that
vanishes on all queried rows but not on at least one unqueried row.  Choose its
sign to make an unqueried payoff negative.  The zero one-action game and this
nonzero game have identical transcripts but distinct robust values.  Hence
fewer than `r` queries cannot solve the certified class in the worst case.

## Frozen evidence

- 160/160 opened exact families passed at ranks 2--4 and 9--48 scenarios.
- 40/40 prospective holdouts passed at 53, 79, 113, 167, and 257 scenarios.
- Full-table and reconstructed-table robust plans agreed exactly in value,
  policy, randomization classification, and certificate state.
- 66 evaluated cases required strict randomization.
- 90/90 lower-bound witnesses gave identical `(r-1)`-query transcripts but
  unequal exact robust values.
- 8/8 quadratic and cubic one-dimensional witnesses reconstructed exactly;
  every witness violated the earlier affine-coordinate certificate.
- Redundant maps reached feature width seven while requiring at most four
  queries.  Query count tracked exact row rank rather than raw width.
- The independent standard-library checker reproduced all 200 main/holdout
  reconstructions, eight polynomial witnesses, 90 lower bounds, and the full
  evidence digest without importing production code.
- Full repository regression passed 159/159 tests; touched files are
  Ruff-clean.
- Primary evidence digest:
  `aca231815c4c04530f8fa5334a5f7f4b782bff9e26307dc068a9115d48b838d2`.

## Strongest alternatives and falsification

**Raw width controls cost.** False on the redundant-column families: adding
three feature columns did not change rank or query count.

**Nonlinear scenario dependence defeats the mechanism.** False under a known
feature map: all quadratic and cubic witnesses reconstructed exactly, while a
linear fit in the raw scalar descriptor failed.

**Robust value needs fewer observations than full reconstruction.** The 90
indistinguishability witnesses refute this in the worst case even for a
one-action game.

**Agreement is a pure-policy coincidence.** The 66 strict-randomization cases
rule this out.

## Executable consequence

`reconstruct_feature_span_scenario_payoffs` computes exact row rank, selects
the lexicographically first independent scenario rows and pivot columns,
queries only those scenarios, reconstructs every remaining payoff with
`Fraction` arithmetic, and returns an auditable query certificate.  Missing
feature-span certification, malformed feature rows, zero rank, inconsistent
oracle shapes, or a failed exact span check aborts before planning.

For the largest holdout, a rank-four map reconstructs 257 scenario columns
from four oracle calls.  THEORICA can then invoke its existing rank-aware
scenario quotient and product-free additive planner.  Acquisition cost now
depends on certified feature rank; planning cost depends on retained scenario
geometry and the tie arrangement, not the Cartesian joint-action count.

## Priority audit

Unisolvent interpolation and rank tests are classical.  Neidinger's exact
multivariate interpolation algorithms explicitly use Gaussian elimination and
identify a polynomial vanishing on the nodes when unique interpolation is
impossible: <https://doi.org/10.1137/17M1124188>.  Classical multivariate
interpolation likewise characterizes unisolvent node sets through nonsingular
Vandermonde matrices; see Cools and Poppe, *Computing Almost Minimal Formulas
on the Square* (2013): <https://doi.org/10.1016/j.cam.2012.05.021>.

The rank lower bound is elementary finite-dimensional indistinguishability,
not a newly claimed linear-algebra theorem.  The defensible contribution is
the sharp feature-rank law for robust scenario acquisition, its executable
exact certificate, matching robust-value lower bound, nonlinear and redundant
feature validation, prospective policy replay, and fail-closed THEORICA
integration.

## Limitations

- The feature map and payoff-in-span property are externally certified.
  Queried observations alone cannot validate the property on hidden scenarios.
- All evidence uses exact rational arithmetic.  Noisy or approximate feature
  structure requires statistical estimation and different guarantees.
- Reconstruction does not guarantee that the resulting game satisfies the
  current downstream affine-rank or hull-size caps; unsupported games still
  abstain after reconstruction.
- The lower bound is deterministic, exact, and worst-case.  It does not cover
  approximation, randomized error, or distributional priors.
- The result does not discover features or prove additivity.

## Reproduction

```bash
python scripts/verify_feature_rank_query_complexity.py
python scripts/audit_feature_rank_query_complexity.py
pytest -q
```
