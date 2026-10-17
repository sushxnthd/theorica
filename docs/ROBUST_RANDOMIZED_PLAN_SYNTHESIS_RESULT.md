# Constructive robust randomized query planning

## Result

THEORICA now converts the total-variation robust frontier into an executable
distribution over hidden-generator query plans.

Let `k=q+1`, and let the adversarial frontier LP minimize an epigraph variable
`v` subject to `pi(S)<=v` for every `k`-subset `S`. At optimum, the negatives of
the HiGHS inequality marginals on these subset constraints are nonnegative and
sum to one. They therefore define a distribution `lambda` over `k`-sets. Its
label-inclusion vector is

`a_i = sum_{S contains i} lambda_S`.

LP duality gives

`min_{TV(pi,p)<=delta} pi dot a = R*(p,delta,q)`.

THEORICA independently resolves the left-hand minimization before accepting the
mixture. A certificate records the mixture, inclusion probabilities, frontier,
independently computed payoff, residual, and solver status. Execution is
deterministically bound to an explicit seed digest: the sampled `k`-set becomes
`q` queried labels plus one all-negative terminal guess.

## Boundary correction found by the frozen gate

The run falsified the previous deterministic formula at full coverage. The
correct law is

`D*(p,delta,q)=max(0,sum_top_k(p)-delta)` for `k<n`,

but

`D*(p,delta,n-1)=1`.

When all labels are covered, no probability mass can move outside the success
set. The old formula incorrectly subtracted `delta`. The exact counterexample
and explanation are preserved in `ROBUST_FULL_COVERAGE_CORRECTION.md` and
`results/robust_full_coverage_failure.json`. All previously reported strict
separations used `k<n` and survived the corrected exhaustive verifier.

## Prospective evaluation

| Gate | Result |
|---|---:|
| Frozen synthesis cases, orders 3 through 8 | 528 |
| Mixture components certified | 1,405 |
| Seed reproducibility/executability checks | 1,056 |
| Strict randomized gains after correction | 242 |
| Full-coverage cases corrected | 72 |
| Persisted mixtures independently audited | 72 |
| Maximum internal payoff residual | `8.89e-16` |
| Maximum independent persisted-mixture residual | `2.00e-12` |
| Scientific failures | 0 |

The primary artifact reran byte-identically. Runtime and localization tests
cover strict uniform separation, asymmetric priors, full coverage, seed-bound
execution, and fail-closed handling of uncertified provenance.

## SCIENCE ledger

- The minimax value theorem is now constructive: optimal subset-mixture weights
  are recovered from the frontier LP dual and independently payoff-certified.
- The deterministic law has a necessary full-coverage exception; this removes
  72 false penalties in the frozen panel.
- After correction, 242 proper-subset cases still exhibit a strict randomized
  minimax advantage.

## CONSEQUENCE ledger

- `robust_provenance_frontier` now returns
  `use_certified_randomized_plan`, rather than refusing, when deterministic
  top-mass planning is dominated and the mixture certificate passes.
- `locate_hidden_generator_with_robust_provenance` executes the certified
  mixture with a reproducible seed, emits the robust success floor and residual,
  and makes zero oracle calls when family or provenance certification is absent.
- Full-coverage requests correctly use the deterministic plan with success one.

## Smallest supported claim

For the certified hidden-generator equality-query reduction, orders 3 through
8 in the frozen prior/radius panel, THEORICA synthesized and independently
verified executable subset mixtures whose worst-case TV-robust payoff matched
the minimax frontier within `2.00e-12`. This is a constructive deployed
reduction, not a historical novelty claim for minimax duality, LP sensitivity,
or hypersimplex representations.

## Limitations

- Guarantees depend on the hidden-family and provenance/TV-radius certificates.
- The numerical certificate is tolerance-bound (`1e-8`), not rational exact
  arithmetic; failure to close the residual is fail-closed.
- Enumerating all `k`-subsets is exponential and is currently suitable only for
  small certified families. Column generation is future work.
- No unopened external challenge or third-party replication was used.
