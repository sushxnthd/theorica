# Frozen protocol: coupled-additive minimax correction

Status: frozen before coupled-family enumeration or prospective holdout generation.

## Active kernel

- **Question:** With additive component payoffs but coupled rather than rectangular ambiguity, what exact decomposition survives?
- **Objective:** derive an exact optimal policy without enumerating joint actions and a necessary-and-sufficient boundary for when the rectangular sum value survives.
- **Alternative:** nonrectangular coupling may destroy all useful action-side decomposition.
- **Decisive falsification:** any rational mismatch against the expanded game, zero-bonus criterion mismatch, or sparse-coupling payoff error.
- **Prediction:** for coupled vertex set C, optimize only component action marginals. The value equals the rectangular baseline iff a distribution on C has every component marginal on its nature-optimal face; otherwise the coupling bonus is strictly positive.
- **Project consequence:** replace Cartesian action enumeration with an exact reduced solver using 1 + sum_t(|A_t|-1) variables, expose the coupling bonus, and return a sparse executable policy.
- **Kill condition:** any exact disagreement, vacuous equality boundary, or support-bound violation.

## Frozen theorem candidate

For nonempty C contained in the product of component ambiguity vertices and additive payoff

M(a,b) = sum_t M_t(a_t,b_t),

expected payoff against b depends only on component action marginals mu_t. Every tuple of marginals has a joint coupling, hence

V_C = max_(mu_t) min_(b in C) sum_t <mu_t, M_t(:,b_t)>.

This is a linear program with 1 + sum_t(|A_t|-1) variables and |C| payoff constraints.

Let v_t be the rectangular component values and D_t their nature-optimal faces. Finite minimax duality gives V_C >= sum_t v_t, with equality iff some lambda supported on C satisfies, for every t and action a_t,

E_lambda[M_t(a_t,b_t)] <= v_t.

Greedy common-mass coupling realizes optimal action marginals with at most
1 + sum_t(s_t-1) joint actions.

## Frozen validation

- Exhaust all pairs of 2x2 component games over {0,1,2} and all 15 nonempty subsets of four joint ambiguity vertices: 98,415 cases.
- Compare to a separately implemented exact expanded joint-game solver.
- Check equality feasibility, bonus sign, marginals, every coupled-vertex payoff, and support.
- Only after that gate, open 32 three-factor cases from seed 20261026.
- Require both equality and strict-bonus proper nonrectangular families.

## Claim boundary

Finite minimax, LP duality, rectangularity, and marginal coupling are classical. The candidate contribution is the sharp correction/equality certificate and its executable THEORICA integration.
