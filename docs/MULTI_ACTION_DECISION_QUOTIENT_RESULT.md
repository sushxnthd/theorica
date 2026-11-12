# Multi-action decision quotient

## Exact theorem

For every feasible payoff completion `theta`, let `v_theta` be its exact robust
value and define its optimal-policy polytope

\[
P_\theta=\{w\in\Delta_{a-1}:G_\theta^T w\ge v_\theta\mathbf 1\}.
\]

One exact robust policy is valid for every completion if and only if

1. every `v_theta` is equal, and
2. the intersection of all `P_theta` is nonempty.

If values differ, two transcript-indistinguishable completions certify that no
exact value-and-policy result is identifiable. If values agree but the policy
intersection is empty, Helly's theorem in the affine `(a-1)`-simplex guarantees
an empty-intersection witness containing at most `a` completions.

The witness bound is sharp. For `a` actions, completion `i` with one payoff
scenario equal to zero on every action except payoff `-1` on action `i` has
optimal set `P_i={w:w_i=0}`. Every proper subfamily intersects, while all `a`
faces have empty intersection.

## Executable certificate

THEORICA now:

- enumerates finite feature-span completions under one shared row-corruption
  budget across every action;
- computes robust values and policies by exact rational vertex enumeration;
- intersects the resulting optimal-policy polytopes exactly;
- returns a common policy or a concrete completion-index witness of size at
  most the action count; and
- replays every returned policy against every scenario of every completion.

The pre-existing finite-list distance gate still runs before completion
enumeration, so positive-dimensional version spaces fail closed.

## Evidence

| Gate | Result |
|---|---:|
| Opened three/four-action positive transcripts | 40/40 |
| Prospective reciprocal-feature positives | 20/20 |
| Non-identifiable positive models | 60/60 |
| Unequal-value attacks rejected | 20/20 |
| Equal-value/disjoint-policy attacks rejected | 20/20 |
| Sharp three-completion Helly witnesses | 10/10 |
| Sharp four-completion Helly witnesses | 10/10 |
| Independent Fraction-only positives | 60/60 |
| Independent production imports | 0 |
| Primary digest | `8e52a09caf60ede6ae0f649fce604635eec008d92730ef7941cf375ff4c81fd6` |
| Independent digest | `0884958ea57fd6782012bb8f7ac6ef3096bcc73a2eadd10f5c9d8f84e888cf86` |

Pairwise agreement is not sufficient once there are three actions: every pair
in the sharp face construction shares a policy, but the triple does not. The
returned Helly witness therefore carries strictly more information than a
pairwise disagreement search.

## Novelty and limitations

Optimal-policy sets are convex and Helly's theorem is classical. No novelty is
claimed for either fact or for finite zero-sum linear programming. The bounded
contribution is the exact corrupted-query decision quotient for arbitrary
finite action counts, its executable rational certificate, and its bounded,
sharp abstention witness integrated into THEORICA.

The implementation is combinatorial and intended for small exact version
spaces. It does not establish polynomial complexity, efficient high-action list
decoding, or approximate/noisy guarantees. It assumes exact rational payoffs,
externally certified feature-span structure and budgets, a finite completion
list, and trusted erasure labels.
