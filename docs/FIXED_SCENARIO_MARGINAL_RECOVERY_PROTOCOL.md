# Frozen protocol: product-free marginal recovery

Frozen before implementation and outcome inspection on 2026-10-23 UTC.

## Question

Can the fixed-scenario additive planner recover an exact executable policy without enumerating the Cartesian product of actions tied at the minimizing nature distribution?

The value path is already product-free. The remaining limitation is policy recovery: if component `t` has tied set `T_t`, the current implementation enumerates `prod_t |T_t|` joint actions and fails closed above 500,000.

## Mechanism and theorem target

For additive scenario payoffs, a joint policy affects every scenario only through its component marginals. At the exact dual minimizer `q*`, restrict component `t` to `T_t` and solve the marginal feasibility system

```
sum_a p[t,a] = 1                                      for every component t
p[t,a] >= 0
sum_t sum_a p[t,a] u[t,a,s] >= V                       for every scenario s
```

where `V` is the certified dual value. Any feasible marginals have a joint coupling. Greedy common-mass coupling preserves every marginal and has support at most

```
1 + sum_t (support(p[t]) - 1).
```

At a basic feasible marginal solution, the component simplex equations contribute `T` independent constraints and the active scenario constraints contribute at most `m - 1`: their `q*`-weighted combination is constant on all tied actions. Hence the coupling support is at most `m`, independent of `prod_t |T_t|`.

Floating point may propose a basis, but it may not certify one. The implementation must reconstruct all accepted probabilities from exact `Fraction` linear systems and reject a candidate unless exact replay proves nonnegativity, unit marginals, payoff at least `V` in every scenario, recovered marginals, and support at most `m`. Failure to reconstruct is abstention, not an approximate plan.

## Frozen decisive experiment

1. Preserve all existing exact fixed-scenario tests and exhaustive five-scenario results.
2. Compare new recovery with the former enumerative recovery on a frozen tractable corpus; require identical value and valid exact payoff certificates, not identical policies.
3. Use the adversarial tie-explosion family of 15 components, five scenario-basis actions per component, and payoff 5 on the selected scenario and 0 otherwise. At uniform `q*`, all five actions tie in every component, so the former recovery sees `5^15 = 30,517,578,125` active joint actions and must abstain under its frozen 500,000 cap. The new method must return an exact certificate without forming that product.
4. Add an independent checker that imports no THEORICA planner code and verifies the serialized witness with `Fraction` arithmetic.
5. Run the full test suite and the dedicated hosted workflow.

## Strong alternatives and falsifiers

- **Correlation is required.** Falsified only if exact replay confirms that a coupling of recovered marginals reaches `V` in every scenario.
- **The numerical basis hides approximation.** Falsified only by independent rational replay; any reconstruction failure kills the candidate.
- **The support bound is false under degeneracy.** One valid witness with support above `m`, or any corpus mismatch in certified value, kills the claim.
- **The improvement is merely a looser cap.** The implementation must never iterate the tied Cartesian product on the new path; instrumentation and the 30.5-billion witness must make this auditable.

## Smallest publishable and product claims

This is not claimed as a new LP or coupling theorem. The bounded claim is an end-to-end compositional certificate: fixed scenario dimension makes both exact value computation and exact policy recovery independent of the Cartesian joint-action count, with an executable support-`m` policy and fail-closed rational verification. The direct product consequence is removal of tied-response explosion as an abstention cause in THEORICA's certified additive planner.

The claim excludes nonadditive interactions, approximate payoff tables, unbounded scenario dimension, and instances exceeding the arrangement or marginal-variable safety caps.
