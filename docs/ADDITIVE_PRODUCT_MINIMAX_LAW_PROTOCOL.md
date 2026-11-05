# Frozen protocol: additive-product minimax law

Status: frozen before exhaustive enumeration.

## Active kernel

- **Precise question.** For robust query games whose action space and ambiguity vertices are Cartesian products and whose payoff is the sum of component payoffs, can THEORICA solve components independently and synthesize a sparse joint randomized plan without losing minimax value?
- **Best-known frontier.** THEORICA has exact fast paths for two actions, two ambiguity vertices, and symmetry quotients. General product games still expand every joint action and joint ambiguity vertex.
- **Exact objective.** Prove that the product-game value is the sum of component values; derive an executable coupling with joint support at most `1 + sum_t(s_t - 1)` from component supports `s_t`; characterize strict randomized advantage; and prove a failure boundary when rectangular ambiguity or payoff additivity is removed.
- **Strongest alternative explanation.** Independent component optimization may fail because correlations between joint actions or coupled adversary states change the worst case. The sparse-support bound may be a loose Caratheodory restatement with no executable construction.
- **Cheapest decisive falsification.** Any exact product/direct value mismatch, any coupled plan with incorrect marginals, any support above the bound, any strictness-criterion mismatch, or any claimed decomposition surviving a frozen nonrectangular/cross-term counterexample.
- **Mechanism-derived unseen prediction.** If component values are `v_t` and best pure values are `p_t`, the joint value is `sum(v_t)`, the best pure joint value is `sum(p_t)`, and strict randomization occurs exactly when at least one `v_t > p_t`. A greedy common-mass coupling preserves every component marginal using at most `1 + sum_t(s_t - 1)` joint actions.
- **Publishable threshold.** Exact proof, exhaustive rational product/direct agreement, independent checker, frozen unseen three-factor cases, sharp assumption counterexamples, deterministic artifacts, primary-literature audit, and integration as a fail-closed planner.
- **Project-consequence threshold.** Replace expanded exact enumeration for certified additive rectangular products with component fast paths plus sparse coupling, while returning a checkable marginal/value certificate and refusing uncertified structure.
- **Kill condition.** Any theorem/checker mismatch, non-sharp assumption boundary, failure to reduce represented joint support on a nontrivial family, or inability to validate the synthesized plan independently.

## Frozen theorem candidate

For component payoff matrices `M_t` on `A_t x B_t`, define

`M((a_1,...,a_d),(b_1,...,b_d)) = sum_t M_t(a_t,b_t)`.

Nature may choose any vertex in the full Cartesian product `prod_t B_t`.
For any joint query distribution, expected payoff depends only on its component
marginals, and minimization over the Cartesian ambiguity set separates. Hence
the robust objective is the sum of component objectives.

The coupling algorithm repeatedly emits the tuple of the current positive-mass
component atoms with weight equal to their smallest remaining mass, subtracts
that weight, and advances every exhausted component atom. Every iteration after
the first exhausts at least one of `sum_t(s_t-1)` nonfinal atoms, giving support
at most `1 + sum_t(s_t-1)`.

## Frozen enumeration and holdouts

- Exhaust every pair of `2 x 2` component games over payoffs `{0,1,2}`.
- Exhaust selected `2 x 3`, `3 x 2`, and mixed-dimension pairs over `{0,1,2}` where direct exact enumeration remains tractable.
- Freeze 24 three-factor games from seed `20261025` before solving them.
- Check value, pure baseline, randomized gain, strictness, all coupling marginals, realized joint value, support bound, and canonical certificate.
- Counterexamples: one nonrectangular ambiguity subset and one bilinear cross-term perturbation, each required to break the naive additive prediction.

## Reporting boundary

Finite minimax, separable optimization, marginal coupling, transportation
polytopes, and Caratheodory-type support bounds are classical. Even a pass
supports an exact THEORICA decomposition/certificate law and implementation,
not a new general zero-sum-game theorem.
