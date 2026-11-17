# Frozen protocol: cost-weighted q-ary mixed-fault law

Status: frozen before implementation and before weighted holdouts.

## Claim under test

Extend the q-ary prefix-query family to positive integer level costs
`c_0,...,c_(m-1)`. Every physical query resolving level `j` costs `c_j`.
With global budgets of `t` adversarial substitutions and `s` recognized
erasures, expose `2t+s+1` physical copies of every prefix query.

The predicted exact adaptive worst-case cost is

`C_q(m;t,s;c) = (t+1) sum_j c_j + (t+s) max_j c_j`.

The predicted policy queries the current prefix until one non-erased symbol
appears `t+1` times. Faults add their query cost, and the adversary concentrates
all `t+s` faults at a maximum-cost level.

Every fixed schedule is predicted to have the certified lower bound

`(2t+s+1) q^(m-1) c_(m-1)`

from the leaf-parent queries alone.

## Opened controls

- Unit costs reproduce `D_q(m;t,s)=(t+1)m+t+s`.
- One-level families reproduce the classical repetition cost
  `(2t+s+1)c_0`.

## Prospective holdouts

- `(q,m,t,s,c)=(3,2,1,1,(1,5))`.
- `(q,m,t,s,c)=(2,3,1,2,(7,1,3))`.
- `(q,m,t,s,c)=(4,2,2,1,(2,9))`.
- `(q,m,t,s,c)=(3,3,1,1,(1,2,5))`.
- Repeat the same multiset of costs in different level orders to test the
  predicted dependence on only `sum(c)` and `max(c)`.
- Delete one required leaf-parent copy and require fail-closed behavior.
- Independently replay every optimum using a standard-library-only solver with
  no THEORICA imports.

## Success and kill criteria

Success requires every exact minimax cost to equal the formula, all cost-order
permutations to agree, unit-cost controls to reproduce the previous theorem,
the missing-copy attack to abstain, and the independent solver to match. Any
counterexample kills the law and is preserved. If exact cases survive but the
matching adversarial lower bound cannot be proved, report only an enumerated
conjecture.

## Novelty boundary

Weighted decision trees, repetition codes, feedback strategies, and liar games
are classical. The bounded contribution sought is the sharp weighted law for
this algebraically generated prefix-decision family, its executable exact
cost-minimax planner, and a prospective cost-sensitive adaptive separation.
