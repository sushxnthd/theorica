# Rank-one scenario quotient: exact result

## Smallest supported claim

For a finite robust game with a certified component-additive payoff, suppose
every component-local action payoff profile across scenarios is affine in one
shared scalar scenario coordinate. Then the full game is exactly equivalent to
the game containing only the minimum- and maximum-coordinate scenarios. An
optimal executable agent policy has support at most two. The implementation
checks the affine certificate with exact rational arithmetic, replays the
returned policy on every original scenario, and rejects higher-rank inputs
before endpoint planning.

This removes the previous ambient `m <= 8` boundary for this class. It does not
solve rank-two scenario geometry, nonadditive payoffs, or uncertified endpoint
selection.

## Theorem

Let components be `t = 1,...,T`, local actions be `a_t`, and scenarios be
`j = 1,...,m`. Assume the joint payoff is

`U(a,j) = sum_t U_t(a_t,j)`.

If there are rationals `z_j`, `b_{t,a_t}`, and `d_{t,a_t}` such that

`U_t(a_t,j) = b_{t,a_t} + d_{t,a_t} z_j`,

then for every randomized joint policy `p`, its payoff against a nature mixture
`q` is `B(p) + D(p) E_q[z]`. The set of possible expectations is exactly the
interval `[min_j z_j, max_j z_j]`. A linear function on that interval is
minimized at an endpoint, so

`max_p min_q E[U] = max_p min(U_p(j_min), U_p(j_max))`.

The reduced game has two nature columns. Linear-program basic-feasible-solution
geometry gives an optimal agent mixture supported on at most two joint actions.
Because additivity is preserved at the endpoints, the existing product-free
two-vertex planner constructs this mixture without Cartesian action expansion.

The converse used by the router is deliberately only operational: if the exact
affine-rank certificate fails, this quotient is not authorized. Rank above one
does not imply that endpoint deletion always fails; it means this theorem no
longer justifies it.

## Frozen evaluation result

| Gate | Result |
|---|---:|
| Opened rational families | 304/304 exact |
| Opened strict-mixing cases | 123 |
| Prospective holdouts | 50/50 exact |
| Unseen holdout scenario counts | 9, 13, 21, 34, 64 |
| Holdout strict-mixing cases | 20 |
| Maximum returned support | 2 |
| Rank-two mutation attacks | 100 |
| Rank-two false accepts | 0 |
| Independent audit | passed |

The strongest simple alternative—delete all but two scenarios without a rank
certificate—is decisively false. For actions `(1,0,1)` and `(1,1,0)`, deleting
the middle scenario claims value `1`; the exact three-scenario value is `1/2`.
The production router rejects this input.

The scaling witness has 20 components, four actions per component, and 64
scenarios. Cartesian expansion would contain `4^20 = 1,099,511,627,776` joint
actions. The certified quotient retains two scenarios and returns an exact
one-action policy in this witness.

Reproduce with:

```bash
python scripts/verify_rank_one_scenario_quotient.py
python scripts/audit_rank_one_scenario_quotient.py
pytest -q tests/test_robust_provenance.py
```

## Novelty and priority audit

The ingredients are classical: finite minimax duality, extrema of affine
functions on an interval, and sparse basic feasible solutions. Robust
optimization broadly exploits extreme points of uncertainty sets; see
[Bertsimas, Brown, and Caramanis (2011)](https://doi.org/10.1137/080734510).
Sparse game strategies are also an established topic, with general sparse
commitment potentially computationally difficult; see
[Afiouni et al. (2024)](https://arxiv.org/abs/2412.14337).

Accordingly, this result is not claimed as a new minimax or convexity theorem.
The defensible contribution is the sharp, executable routing criterion for the
THEORICA additive planner: exact detection of a shared affine scenario quotient,
product-free recovery, full original-scenario replay, a prospective validation
beyond the old scenario cap, and fail-closed rejection demonstrated against an
endpoint-deletion attack. A broader literature search did not establish
priority for this particular software theorem, so any publication claim must
remain at that bounded level pending expert review.

## Limitations

- Exact rational inputs are required by this certificate.
- Approximate low rank receives no tolerance-based guarantee and is rejected.
- The quotient depends on certified payoff additivity.
- Rank two or higher requires the general arrangement planner or a future
  higher-dimensional structural theorem.
- The prospective tests are generated algebraic families, not external domain
  data.

## Direct product consequence

THEORICA can now route arbitrary-scenario additive games through
`synthesize_rank_one_scenario_quotient_plan`. Success removes the ambient
scenario-count cap and produces a replayable support-two policy. Any affine
certificate failure raises before planning, so the product must abstain from
this fast path and preserve the existing general boundary.
