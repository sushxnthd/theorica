# Frozen protocol: q-ary multiple-lie law

Status: frozen before implementation and before prospective holdouts.

## Claim under test

Let `q >= 2`, `m >= 1`, and `t >= 0`. Index `q^m` pairwise-incompatible
exact robust decisions by length-`m` words over `{0,...,q-1}`. At every
prefix, expose `2t+1` physical copies of the query returning the next symbol
inside that prefix subtree and zero outside it. Allow at most `t` adversarial
answer substitutions.

The predicted exact adaptive depth is

`D_q(m,t) = (t+1)m + t`.

The predicted fixed-schedule lower bound is

`(2t+1) q^(m-1)`.

The proof target is a prefix-dominance exchange lemma plus induction. Query
the current prefix until one answer has appeared `t+1` times. A false symbol
cannot reach that count, and if `e` lies are spent at the level the cost is
`t+1+e`; summed over all levels this is at most `(t+1)m+t`. For the lower
bound, prefix dominance lets an adversary postpone all corruptions until the
last unresolved symbol: each earlier level costs `t+1` identical truthful
answers while preserving the full budget, and the final `q`-way choice costs
`2t+1`.

## Opened controls

- `t=2`: `(q,m)=(2,1),(3,1),(2,2),(3,2),(4,2),(5,2),(2,3)`.
- `t=3`: `(q,m)=(2,2),(3,2)`.
- The preceding one-lie result remains an opened consistency control.

## Prospective holdouts

- `(q,m,t)=(3,3,2)`.
- `(q,m,t)=(4,2,3)`.
- `(q,m,t)=(2,3,3)`.
- Delete one copy of a leaf-parent query at `(q,m,t)=(3,2,2)` and require
  fail-closed behavior.
- Independently replay all returned depths using only the Python standard
  library and no THEORICA imports.

## Success and kill criteria

Success requires every exact optimum to equal `(t+1)m+t`, every returned tree
to replay, every prospective case to beat the fixed lower bound when that
bound is strictly larger, and the missing-copy attack to abstain. Any depth
counterexample kills the closed-form law and is preserved. If the finite cases
survive but prefix dominance cannot be proved, the result is reported only as
an enumerated conjecture.

## Novelty boundary

Liar games, repetition, feedback coding, and minimax dynamic programming are
classical. The bounded contribution sought is the sharp all-budget law for
this algebraically generated q-ary decision-query family, an executable
optimal policy, and an exact adaptive-versus-fixed separation.
