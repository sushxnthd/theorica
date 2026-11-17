# Exact q-ary mixed-fault law

## Theorem

Fix `q >= 2`, word depth `m >= 1`, substitution budget `t >= 0`, and
recognized-erasure budget `s >= 0`. Index `q^m` pairwise-incompatible robust
decisions by q-ary words. For every prefix, expose `2t+s+1` physical copies of
the query returning the next symbol inside that prefix subtree and zero outside
it. The exact minimum worst-case adaptive depth is

`D_q(m;t,s) = (t+1)m + t + s`.

Every fixed schedule requires at least `(2t+s+1)q^(m-1)` queries.

## Proof

For the upper bound, at the current prefix query until one non-erased answer
has appeared `t+1` times, then descend into that child. No false answer can
reach this threshold with at most `t` substitutions. If level `j` receives
`e_j` substitutions and `r_j` erasures, it costs at most
`t+1+e_j+r_j` queries. The budgets are global, so summing gives
`(t+1)m + sum(e_j) + sum(r_j) <= (t+1)m+t+s`.

For the lower bound, prefix dominance lets a strict-descendant query made
before the current symbol is resolved be exchanged for the current-prefix
query without increasing worst-case depth: it is identically zero outside one
candidate child, so an adversary retaining another child makes it
uninformative. At each of the first `m-1` levels, the adversary returns `t+1`
identical truthful non-erased answers. With only `t` such answers, all could be
substitutions, while no substitution or erasure budget has yet been spent.
The last q-way symbol is a repetition code and needs `2t+s+1` physical
answers: two distinct symbols have distance equal to the number of copies,
and unique separation under `t` substitutions plus `s` erasures requires
distance at least `2t+s+1`. Therefore

`(t+1)(m-1) + (2t+s+1) = (t+1)m+t+s`.

For a fixed schedule, any two leaves with the same length-`m-1` prefix differ
only on their leaf-parent query. The same error-erasure separation condition
requires all `2t+s+1` copies of each of the `q^(m-1)` leaf-parent queries.

## Exact evidence

Eight exact families cover arities two through four, depths one through three,
pure substitutions, pure erasures, and mixed budgets up to two substitutions
and two erasures. All matched the theorem. The four frozen prospective
holdouts `(3,2,1,1)`, `(2,3,1,2)`, `(4,2,2,1)`, and `(3,3,1,1)` had exact
adaptive depths 6, 9, 9, and 8.

The strongest holdout has 27 incompatible decisions: 8 adaptive queries
versus a fixed-schedule lower bound of 36, saving 28 worst-case queries. Its
exact solver explored 78,555 states. Removing one required leaf-parent copy
at `(3,2,1,1)` made robust identification impossible; the planner abstained
after exploring 14,631 states.

An independent standard-library implementation reconstructed all eight
optima and the abstention, reproduced the case digest, and imported zero
THEORICA modules.

## Reproduction

```bash
python scripts/verify_qary_mixed_fault_law.py
python scripts/audit_qary_mixed_fault_law.py
pytest -q tests/test_corruption_resilient_features.py
```

Raw deterministic evidence is under `results/qary_mixed_fault_law/`.

## Limits and novelty boundary

The theorem concerns this prefix-query construction, global bounded faults,
recognized erasures, and a finite exact completion set. It is not a general
q-ary liar-game or feedback-channel capacity theorem. Error-erasure coding,
repetition, and liar games are classical. The bounded contribution is the
sharp mixed-fault law for THEORICA's algebraic decision family, its executable
exact minimax planner, prospective nonbinary holdouts, and its certified
adaptive-versus-fixed separation.
