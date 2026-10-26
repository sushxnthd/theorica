# Frozen protocol: q-ary mixed substitution-erasure law

Status: frozen before implementation and before mixed-fault holdouts.

## Claim under test

Let `q >= 2`, word depth `m >= 1`, substitution budget `t >= 0`, and
recognized-erasure budget `s >= 0`. Index `q^m` pairwise-incompatible exact
robust decisions by q-ary words. At every prefix expose `2t+s+1` physical
copies of the next-symbol query. Each physical answer can be substituted at
most `t` times globally or returned as a recognized erasure at most `s` times.

The predicted exact adaptive depth is

`D_q(m;t,s) = (t+1)m + t + s`.

The predicted fixed-schedule lower bound is

`(2t+s+1) q^(m-1)`.

The proof target queries a current prefix until one non-erased symbol appears
`t+1` times. A false symbol cannot reach that count. A level using `e`
substitutions and `r` erasures costs `t+1+e+r`; summing the global budgets gives
the upper bound. Prefix dominance should give the matching lower bound by
preserving both budgets through the first `m-1` levels and spending them on
the final symbol.

## Opened controls

- Every `s=0` case from the all-budget substitution theorem.
- Base cases `m=1`, where classical error-erasure separation requires
  `2t+s+1` copies.

## Prospective holdouts

- `(q,m,t,s)=(3,2,1,1)`.
- `(q,m,t,s)=(2,3,1,2)`.
- `(q,m,t,s)=(4,2,2,1)`.
- `(q,m,t,s)=(3,3,1,1)`.
- Delete one leaf-parent copy at `(3,2,1,1)` and require fail-closed behavior.
- Independently replay every optimum using only the Python standard library
  and no THEORICA imports.

## Success and kill criteria

Success requires every optimum to equal `(t+1)m+t+s`, every returned policy
to replay, the missing-copy attack to abstain, and every strict holdout
separation to beat the fixed lower bound. Any counterexample kills the law and
is preserved. If exact cases survive but prefix dominance cannot be proved,
the result is reported only as an enumerated conjecture.

## Novelty boundary

Error-erasure coding, repetition, liar games, and feedback strategies are
classical. The bounded contribution sought is the sharp mixed-fault law for
this algebraically generated decision-query family, its executable exact
planner, and the resulting adaptive-versus-fixed separation.
