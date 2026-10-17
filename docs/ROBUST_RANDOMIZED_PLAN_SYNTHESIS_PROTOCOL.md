# Robust randomized plan synthesis: frozen protocol

**Frozen:** 2026-10-17 UTC  
**Parent:** `6c0fc90b22af5ead1247ce92382c881b5f3120e6`

## Active kernel

### Precise question

Can THEORICA turn the exact total-variation robust value

`R*(p,delta,q)=min_{TV(pi,p)<=delta} sum_top_(q+1)(pi)`

into an explicit executable distribution over `q`-query plans, with a
checkable certificate that its worst-case success matches the frontier?

### Best-known frontier

The current runtime computes the robust value and correctly refuses a
dominated deterministic top-mass plan. The minimax proof identifies feasible
inclusion vectors with the hypersimplex, but the runtime does not recover a
mixture over its `k=q+1` subset vertices and therefore cannot execute the
superior randomized strategy.

### Exact objective

Recover the dual weights on all `k`-subset epigraph constraints from the
frontier LP; interpret them as a distribution over covered-label sets; and
independently solve

`min_{TV(pi,p)<=delta} E_S[pi(S)]`.

The implementation must return the mixture, label-inclusion probabilities,
certified lower payoff, frontier value, residual, solver status, and a
deterministic seed-bound sample consisting of `q` queried labels plus one
all-negative terminal guess.

### Strongest alternative explanation

The LP reports the correct game value, but its constraint marginals may have
the wrong sign/normalization, may be numerically degenerate, or may not map to
an executable subset mixture. In that case the earlier value theorem is not an
operational planner.

### Cheapest decisive falsification

For any frozen prior/radius/budget case, independently minimize the synthesized
mixture's payoff over the TV ball. Kill the synthesis claim if mixture weights
are negative or fail to sum to one, any support set has the wrong cardinality,
the independent payoff is below the frontier by more than `1e-8`, a sampled
plan leaves its mixture support, or repeated identical seeds differ.

### Publishable success condition

Pass all budgets for uniform and asymmetric controls at orders 3 through 8,
including every strict deterministic/randomized separation, plus a separately
implemented independent payoff audit and byte-identical rerun. This is a
constructive system theorem for the certified hidden-generator reduction, not
a historical-first claim for LP duality or hypersimplex decomposition.

### Project-relevance threshold

THEORICA must replace `refuse_dominated_deterministic_plan` with an executable
`use_certified_randomized_plan` action only when the synthesized mixture passes
its payoff certificate. Missing certificates, solver failure, or residual
above tolerance must remain fail-closed.

### Kill condition

One reproducible dual/frontier mismatch, independent-payoff failure, seed
nondeterminism, or execution outside the certified family kills this kernel.

## Frozen evaluation

- Orders `n=3..8`.
- Priors per order: uniform; one-heavy `(3,1,...)`; descending bounded weights;
  and a deterministic pseudorandom panel.
- TV radii: `0`, `1/20`, `1/10`, `1/4`.
- Every query budget `q=0..n-1`.
- Independent audit reconstructs payoffs from the persisted mixture rather
  than trusting the synthesis function.
- A fixed seed panel checks support membership and reproducibility.

No unopened challenge or holdout is used.

## Ledgers

### SCIENCE

Test the constructive implication of the minimax theorem: the frontier LP's
dual epigraph multipliers are an optimal distribution over covered-label
sets, and their independently computed worst-case payoff equals `R*`.

### CONSEQUENCE

If supported, uncertain certified provenance no longer forces THEORICA to
refuse whenever deterministic planning is dominated. It can execute a
reproducible randomized query plan with an auditable robust-success floor.
