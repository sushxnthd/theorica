# Exact q-ary multiple-lie law

## Theorem

Fix `q >= 2`, word depth `m >= 1`, and corruption budget `t >= 0`. Index
`q^m` pairwise-incompatible robust decisions by q-ary words. For every prefix,
expose `2t+1` physical copies of the query returning the next symbol inside
that prefix subtree and zero outside it. The exact minimum worst-case adaptive
depth under at most `t` adversarial answer substitutions is

`D_q(m,t) = (t+1)m + t`.

Every fixed schedule requires at least `(2t+1)q^(m-1)` queries.

## Proof

For the upper bound, at the current prefix query until an answer has appeared
`t+1` times, then descend into that child. No false answer can reach `t+1`
occurrences using at most `t` substitutions. If `e_j` substitutions occur
while resolving level `j`, that level costs `t+1+e_j` queries. Since
`sum(e_j) <= t`, the total is at most `(t+1)m+t`.

For the lower bound, prefix dominance allows any strict descendant query made
before the current symbol is resolved to be exchanged for the current-prefix
query without increasing worst-case depth: a descendant is identically zero
outside one candidate child, so the adversary can retain another child while
making it uninformative. At each of the first `m-1` levels, the adversary gives
`t+1` identical truthful answers. Fewer answers cannot exclude a competing
child because all could be substitutions, and the full corruption budget is
still available after descent. The final q-way symbol requires `2t+1`
queries. Hence the lower bound is `(t+1)(m-1)+(2t+1)=(t+1)m+t`.

For a fixed schedule, any two leaves with the same length-`m-1` prefix differ
only on their leaf-parent query. Correcting `t` substitutions requires Hamming
distance at least `2t+1`, so every physical copy of all `q^(m-1)` leaf-parent
queries is mandatory.

## Exact evidence

Twelve exact families cover arities two through five, depths one through
three, and budgets two and three. All matched the theorem. The three frozen
holdouts were `(3,3,2)`, `(4,2,3)`, and `(2,3,3)`; their exact adaptive depths
were 11, 11, and 15. The strongest holdout has 27 incompatible decisions:
11 adaptive queries versus a fixed lower bound of 45, saving 34 queries.

Deleting one required leaf-parent copy at `(3,2,2)` made robust identification
impossible, and the planner abstained. An independent standard-library solver
reconstructed every optimum and the abstention without importing THEORICA.

## Reproduction

```bash
python scripts/verify_qary_multi_lie_law.py
python scripts/audit_qary_multi_lie_law.py
pytest -q tests/test_corruption_resilient_features.py
```

Raw deterministic evidence is under `results/qary_multi_lie_law/`.

## Limits and novelty boundary

The theorem concerns this prefix-query library, a finite exact completion
list, and substitution faults with a declared finite answer alphabet. It is
not a general q-ary liar-game capacity theorem. Liar games, repetition, and
feedback coding are classical; the bounded contribution is the sharp
all-budget law for THEORICA's algebraic decision family, its executable exact
planner, prospective nonbinary holdouts, and fixed/adaptive separation.
