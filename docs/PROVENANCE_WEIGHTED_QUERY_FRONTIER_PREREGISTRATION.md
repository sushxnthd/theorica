# Frozen protocol: provenance-weighted hidden-generator query frontier

Frozen before implementation or outcome enumeration.

## Active THEORICA breakthrough kernel

- **Precise question.** For the certified hidden-cycle rack family, if a trusted provenance source supplies a nonuniform prior `pi` over the hidden generator label, what is the exact maximum Bayes success probability achievable with at most `q` cell queries, and can THEORICA expose the optimizer with an exact receipt?
- **Best-known frontier.** The current uniform-prior/worst-case symmetric law is `(q+1)/n`; zero error costs `n-1`. The deployed engine does not use nonuniform certified provenance and has no exact budget inversion for it.
- **Measurable exact objective.** Prove or refute `P*(pi,q)=sum_{i=1}^{q+1} pi_(i)`, where `pi_(i)` are the descending masses, for `0<=q<=n-1`. Implement a deterministic optimal planner for integer-weight priors, exhaust finite rational priors and all deterministic negative-path policies, independently audit the frontier, and emit exact success fractions.
- **Strongest alternative explanation.** Adaptive row selection could exploit the pattern of negative observations and beat a fixed top-mass plan. The decisive issue is whether a depth-`q` decision tree can be correct on more than `q` positively identified labels plus one all-negative guess.
- **Cheapest decisive falsification.** Find any certified family instance, integer prior, and budget for which exhaustive policy enumeration exceeds the top-`q+1` mass or the production planner attains less.
- **Publishable success condition.** A sharp upper/lower theorem, exhaustive finite certificate, independent implementation, fail-closed interface contract, and a documented capability change. Historical novelty is not inferred from failure to find a predecessor; the abstract weighted search theorem may be standard.
- **Project-relevance threshold.** THEORICA must replace uniform random querying, when and only when a trusted provenance distribution is supplied, with an exact Bayes-optimal planner and receipt. Without trusted provenance it must retain the symmetric or zero-error path.
- **Kill condition.** Any adaptive counterexample, planner/certificate disagreement, or inability to separate trusted provenance from oracle-derived evidence kills the kernel.

## Frozen theorem candidate

For a certified hidden-cycle family with hidden label `Z~pi`, each off-diagonal row probe is an equality test for one candidate label. Any deterministic depth-`q` policy has at most `q` positive leaves and one all-negative terminal guess, so it is correct on at most `q+1` labels. Hence its Bayes success is at most the sum of the largest `q+1` prior masses. Querying any `q` of those labels and guessing the remaining one after all negative answers attains the bound. Randomization cannot improve a Bayes objective because it is a convex combination of deterministic policies.

The exact confidence budget candidate is the smallest `q` such that the cumulative mass of the largest `q+1` labels is at least the authorized target confidence.
