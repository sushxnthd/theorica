# Robust provenance-weighted query frontier: frozen protocol

## Active kernel

THEORICA hidden-generator reasoning only. The prior-weighted planner currently
assumes an exact trusted prior. This run asks what survives when provenance
certifies only a total-variation ball around a nominal prior.

## Precise question

For `k=q+1` labels covered by a `q`-query hidden-generator strategy, what is the
exact worst-case success probability over `TV(pi,p)<=delta`? Does the current
deterministic top-mass strategy remain minimax when randomized query sets are
allowed?

## Frozen claims to test

1. The optimal deterministic robust value is
   `D*(p,delta,k)=max(0,sum(top_k(p))-delta)`.
2. The randomized minimax value is
   `R*(p,delta,k)=min_{pi:TV(pi,p)<=delta} sum(top_k(pi))`, by minimax duality
   between distributions over `k`-subsets and adversarial priors.
3. Deterministic top-mass querying is not generally minimax: for uniform `p`
   and any `delta>0`, `R*=k/n` but `D*=max(0,k/n-delta)`.

## Best-known frontier and novelty boundary

Version spaces, robust Bayes decision theory, total-variation distributional
robustness, and finite zero-sum minimax duality are established. Historical
novelty is not presumed. The candidate contribution is the exact reduction for
THEORICA's certified hidden-generator family and an auditable planner contract.

## Exact objective

- Prove both displayed laws and the uniform-prior separation.
- Exhaust deterministic strategies and rational adversarial priors on finite
  cases, and independently solve the randomized value as a linear program.
- Add a runtime frontier function that reports deterministic and randomized
  robust values and refuses deterministic execution whenever a certified gap is
  present.

## Strongest alternative explanation

Because the nominal top-mass strategy is Bayes-optimal, randomization may add no
robust value after the adversary is constrained to a small TV ball.

## Cheapest decisive falsification

One finite `(p,delta,q)` instance where exhaustive deterministic enumeration
disagrees with claim 1, linear programming disagrees with claim 2, or uniform
randomization fails to separate the values.

## Success and kill conditions

- **Success:** exact laws, exhaustive/independent agreement, and a runtime
  receipt changing THEORICA's query-planning behavior.
- **Project relevance:** uncertain provenance produces an explicit robust floor
  and prevents use of a dominated deterministic plan.
- **Kill:** any law fails, numerical duality is uncertified, or the result does
  not alter the planner contract.

No unopened algebraic holdout is used.
