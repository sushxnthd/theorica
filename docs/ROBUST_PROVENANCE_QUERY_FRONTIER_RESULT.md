# Robust provenance-weighted query frontier

## Exact result

Let `p` be a nominal prior on `n` certified hidden-generator labels, let the true
prior lie in `TV(pi,p)<=delta`, and let `k=q+1` be the number of labels on which a
`q`-query strategy can succeed (the queried labels plus its all-negative guess).

For deterministic strategies,

`D*(p,delta,q) = max(0, sum_top_k(p) - delta)`.

For randomized strategies,

`R*(p,delta,q) = min_{TV(pi,p)<=delta} sum_top_k(pi)`.

The second expression is an exact finite linear program.

## Proof

A deterministic plan succeeds on a fixed `k`-set `S`. Total variation permits
the adversary to move up to `delta` probability mass out of `S`, so its worst
case is `max(0,p(S)-delta)`. Choosing the largest nominal masses proves the first
law.

A randomized plan is a distribution over `k`-sets. Its inclusion-probability
vector lies in the hypersimplex `A={a in [0,1]^n: sum a_i=k}`, and payoff against
prior `pi` is `pi dot a`. Finite-dimensional minimax duality gives

`max_{a in A} min_{pi in B} pi dot a = min_{pi in B} max_{a in A} pi dot a`.

For fixed `pi`, the maximizing inclusion vector selects its `k` largest masses,
yielding the second law.

## Decisive separation

For uniform nominal `p`, every prior has top-`k` mass at least `k/n`, while the
uniform prior itself remains in every TV ball. Hence `R*=k/n`. But for any
positive radius before truncation, `D*=k/n-delta`. Therefore the current
deterministic top-mass planner is strictly dominated under uncertain provenance.

## Exact and independent checks

| Check | Count |
|---|---:|
| Positive integer prior vectors, orders 3 through 7 | 3,267 |
| Deterministic frontier cases | 85,212 |
| Exhaustive deterministic subset checks | 332,613 |
| Independent randomized LP controls | 100 |
| Uniform-prior strict separations | 20 |
| Scientific failures | 0 |

The primary result and independent audit reran byte-identically.

## Runtime consequence

`theorica.agents.robust_provenance` now returns both robust values and an
auditable action. It permits the existing deterministic top-mass execution only
when its value matches the randomized minimax frontier within certified solver
tolerance. Otherwise it returns `refuse_dominated_deterministic_plan`.

This prevents an exact nominal prior planner from silently masquerading as a
robust planner when provenance provides only an ambiguity radius.

## Prior art and novelty boundary

Distributionally robust optimization, total-variation ambiguity, randomized
decision rules, and minimax duality are established. For examples of the broader
frontier, see total-variation DRO for discrete uncertainties
(https://arxiv.org/abs/2302.07454) and minimax control under TV ambiguity
(https://epubs.siam.org/doi/10.1137/140955707).

Historical novelty of the abstract minimax machinery is not claimed. The
defensible result is the exact hidden-generator reduction, deterministic versus
randomized separation, exhaustive certificate, and deployed refusal contract.

## Ledgers

### SCIENCE

- The exact deterministic and randomized robust frontiers are established.
- Nominally optimal deterministic top-mass querying is not robustly minimax in
  general.
- Uniform randomized coverage exactly removes the deterministic TV penalty for
  uniform nominal provenance.

### CONSEQUENCE

- THEORICA must record a provenance uncertainty radius, not only point weights.
- A dominated deterministic plan is now rejected rather than reported as
  confidence-optimal.
- The next implementation step is to recover an explicit optimal subset mixture
  from the LP dual and execute it with a reproducible seed.

## Smallest claim and limitations

The result applies to the certified hidden-generator equality-query reduction
and TV ambiguity sets. The current runtime certifies the minimax value and
refuses dominated deterministic execution; it does not yet synthesize the full
optimal randomized mixture for every nonuniform prior. No unopened external
challenge was used.

