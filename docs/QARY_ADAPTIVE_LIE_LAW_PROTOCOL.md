# Frozen protocol: q-ary adaptive lie law

Status: frozen before implementation.

## Claim under test

Let `q >= 2` and index `q^m` pairwise-incompatible exact robust decisions by
length-`m` words over `{0,...,q-1}`.  At every prefix, a query returns the next
symbol inside that prefix subtree and `0` outside it.  Supply three physical
copies of every prefix query and allow one adversarial answer substitution.

The predicted exact adaptive depth is

`D_q(m, 1) = 2m + 1`.

The predicted fixed-schedule lower bound is `3 q^(m-1)`: every sibling group
can differ only on its parent query, whose three copies are therefore all
mandatory under one lie.

The proof target is a prefix-dominance exchange lemma plus induction. Before
the next symbol is resolved, a descendant query is null outside one candidate
subtree and cannot improve the worst case over a parent query. Two agreeing
parent answers leave the full lie budget for the selected height-`m-1`
subtree; a disagreement needs the third copy and consumes the lie. Thus the
worst branch is `2 + D_q(m-1,1)`, with base `D_q(1,1)=3`.

## Frozen experiments

- Opened controls: arities 2, 3, 4 at depth one and arities 2, 3 at depth two.
- Prospective holdouts: `(q,m)=(3,3),(4,2),(5,2)`.
- Delete one copy of a leaf-parent query and require fail-closed behavior.
- Compare exact adaptive depth with `3 q^(m-1)` and the repeated-path upper
  bound `3m`.
- Independently replay the recurrence and every returned tree using only the
  Python standard library and no THEORICA imports.

## Success and kill criteria

Success requires every exact optimum to equal `2m+1`, every returned tree to
replay, every missing-copy attack to abstain, and every prospective case to
beat its fixed lower bound. Any counterexample kills the closed-form law and
is preserved. If only the finite cases survive but the prefix-dominance lemma
cannot be proved, the result is reported as an exact enumerated boundary, not
an unrestricted theorem.

## Novelty boundary

Liar games, repetition, feedback coding and dynamic programming are classical.
The bounded contribution sought is the sharp q-ary law for this algebraically
generated decision-query family, its exact executable planner, and the
adaptive-versus-fixed separation for nonbinary scientific answers.
