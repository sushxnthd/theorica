# Multi-action decision quotient protocol

Status: frozen before implementation and adversarial execution.

## Question

For a finite algebraic completion list with more than two actions, when can
THEORICA certify one exact robust policy even though the payoff model is not
identifiable, and how small can a necessary-abstention witness be?

## Proposed theorem

For each feasible completion `theta`, let `v_theta` be its exact robust value
and let

\[
P_\theta=\{w\in\Delta_{a-1}:G_\theta^T w\ge v_\theta\mathbf 1\}
\]

be its exact optimal-policy polytope for `a` actions. A common exact robust
decision exists if and only if all values are equal and

\[
\bigcap_\theta P_\theta\ne\varnothing.
\]

If values differ, two completions are a complete impossibility witness. If
values agree but the policy intersection is empty, Helly's theorem in the
`(a-1)`-dimensional simplex guarantees an empty-intersection witness containing
at most `a` completions. This bound should be sharp: with three actions there
must be a family of three optimal-policy faces whose pairwise intersections are
nonempty but whose triple intersection is empty.

## Frozen gates

- Implement exact rational robust-value and common-policy certificates for
  finite games with at least three actions.
- Integrate the certificate with finite-list corrupted feature transcripts,
  preserving the shared row-corruption budget across every action.
- At least 60 non-identifiable positive cases across three and four actions.
- At least 20 prospective cases using a previously unopened feature family.
- At least 20 unequal-value attacks and 20 equal-value/disjoint-policy attacks.
- Include a sharp three-completion Helly attack where every pair intersects but
  the triple does not; the returned witness must contain exactly three games.
- Independent Fraction-only checker with zero production imports.
- Preserve the two-action implementation and all existing tests.
- Require full regression, deterministic evidence, Ruff, diff check, and
  hosted workflows.

## Scope

The convex intersection and Helly ingredients are classical. The candidate
claim is limited to an exact executable decision quotient and bounded
impossibility witness for THEORICA's finite corrupted-query completion lists.
It does not cover infinite version spaces, approximate arithmetic, polynomial
list-size bounds, or scalable high-action enumeration.
