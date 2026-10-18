# Divergence-agnostic symmetry law: frozen protocol

**Frozen:** 2026-10-18 before verifier outcomes  
**Parent:** `1082439b9dfa55d95f492edee6b46a6671bfcc39`

## Active kernel

- **Question:** For the certified hidden-generator equality-query reduction, when does randomized (k=q+1)-label coverage strictly dominate every deterministic plan beyond total-variation ambiguity, and can the optimal randomized policy be synthesized without an exponential subset LP?
- **Frontier:** the current implementation solves a TV-specific LP over all (k)-subsets and recovers a certified mixture from dual weights. It is exponential and the strict-gain condition is numerical.
- **Exact objective:** derive a closed-form minimax value, strict-dominance criterion, and (O(n))-space executable policy for a stated class of ambiguity sets; verify exact finite cases independently.
- **Strongest alternative explanation:** the TV result is an artefact of that divergence geometry; without the TV polytope the optimal mixture or value may depend on the ambiguity radius and require the full LP.
- **Cheapest decisive falsification:** find any probability vector (pi), carrier size (n), and proper coverage (0<k<n) for which the proposed uniform-subset policy's payoff differs from the claimed value, or any certified ambiguity family containing the uniform prior for which another policy guarantees more.
- **Mechanism-derived unseen prediction:** if the ambiguity set contains the uniform prior, uniform label-inclusion probability (k/n) will equalize payoff for every adversarial prior, making the minimax value exactly (k/n) regardless of divergence, radius, or other members of the set.
- **Publishable threshold:** exact upper/lower-bound proof; exact iff criterion for deterministic strict domination; constructive strictness for at least TV, forward/reverse KL, chi-square, squared Hellinger, and Jensen-Shannon neighborhoods centered at uniform; exhaustive rational enumeration with an independent checker; production implementation and tests.
- **Project consequence threshold:** replace exponential LP synthesis by a direct uniform-(k)-subset sampler whenever certified ambiguity contains uniform; emit a theorem-bound value and strict-dominance receipt, while preserving the TV-specific asymmetric-prior path otherwise.
- **Kill condition:** any counterexample to the value law or failure of exact sampler marginals kills the kernel. If the theorem survives but is only a restatement with no runtime simplification, it does not count as project progress.

## Theorem candidate

Let (mathcal UsubseteqDelta_n) contain the uniform prior (u). A randomized (k)-coverage plan induces inclusion probabilities (ain[0,1]^n) with (sum_i a_i=k), and its success against (pi) is (picdot a). Then

[
max_amin_{piinmathcal U}picdot a = k/n.
]

Upper bound: evaluate any (a) at (u). Lower bound: choose (a_i=k/n), realized by the uniform distribution over (k)-subsets.

A deterministic plan is strictly dominated iff
[
max_{|S|=k}min_{piinmathcal U}pi(S)<k/n.
]

For any nontrivial permutation-invariant neighborhood of (u) containing sufficiently small mass-transfer perturbations and (0<k<n), strict domination follows.

## Verification plan

1. Primary verifier enumerates rational probability vectors and all (k)-subsets through (n=7), checking exact payoff invariance and strict mass-transfer witnesses.
2. Independent standard-library checker rederives counts and equalities without importing production or primary-verifier code.
3. Production uses a seed-bound partial Fisher-Yates sampler for an exact uniform (k)-subset, avoiding subset enumeration.
4. Tests cover exact value, reproducibility, marginal balance by exhaustive seed-space construction where appropriate, full coverage, zero query budget, and fail-closed certification.

No historical novelty claim is permitted until a primary-literature audit is completed. The likely novelty boundary is the certified-family reduction and scalable runtime contract, not minimax symmetry itself.
