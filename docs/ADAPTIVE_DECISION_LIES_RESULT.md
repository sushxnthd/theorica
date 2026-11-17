# Exact adaptive decision queries with adversarial lies

## Central result

For each feasible completion `theta`, retain the least number `ell_theta` of
answer substitutions needed to explain the transcript. At budget `t`, the
feasible set is exactly

`S(ell) = {theta : ell_theta <= t}`.

For remaining physical query instances `Q`, the exact optimal worst-case
depth is

`D(ell, Q) = 0`

when `S(ell)` has one common exact robust policy and value, and otherwise

`D(ell, Q) = 1 + min_q max_y D(ell + 1[c_theta(q) != y], Q - {q})`.

An infeasible answer branch is omitted; a state with no finite query choice
fails closed. The implementation returns the minimizing tree, every clipped
lie-count state, and exact rational policy/value certificates at its leaves.

## Proof

The vector `ell` is a sufficient statistic: a completion can still be true
exactly when its minimum transcript disagreement count is at most `t`. After
query `q` returns `y`, each count therefore changes by precisely
`1[c_theta(q) != y]`. The verifier must withstand every feasible answer, so
the adversary chooses the maximum child; the verifier chooses the minimum
query. Backward induction over the strictly shrinking query set proves both
optimality and completeness of the returned tree.

The terminal test uses the exact intersection of robust-policy polytopes. An
incompatible pair is an immediate negative certificate, but absence of such a
pair is never treated as sufficient: genuinely higher-order conflicts still
invoke the full common-policy test.

For binary pairwise-incompatible states, the search also uses the classical
lie-sphere weight as a proof-preserving lower bound. Iterative deepening rejects
every smaller depth before accepting the returned policy.

## Sharp adaptive/nonadaptive separation

The prospective family indexes 16 distinct robust decisions by leaves of a
depth-four prefix tree and supplies three physical copies of every internal
query. One answer may be adversarially substituted.

The exact adaptive optimum is **9** queries. The preregistered repeated-path
construction required at most 12.

For every sibling leaf pair, only the three copies of its parent query differ.
One-lie fixed identification requires Hamming distance at least three, so all
three copies are mandatory for each of the eight disjoint sibling pairs. Every
fixed schedule therefore needs at least **24** queries. The executable adaptive
policy saves at least **15** worst-case queries against this certified fixed
lower bound.

Opened depth-two and depth-three families give exact adaptive depths 5 and 7,
against fixed lower bounds 6 and 12.

## Falsification and independent checks

| Gate | Result |
|---|---:|
| Two-class exact repetition controls (`t=0,1,2`) | 3/3 |
| Missing-copy attacks that must abstain | 2/2 |
| Opened prefix-tree families | 2/2 |
| Prospective 16-completion family | 1/1 |
| Higher-order 3--6 action families | 4/4 |
| Independent stdlib-only replays | 12/12 |
| Production imports in independent replay | 0 |

Every higher-order family has zero pairwise conflict edges, yet the complete
family is incompatible and is correctly resolved at depth three under one
lie. This directly falsifies a pairwise-conflict implementation.

The raw result contains the complete 16-completion depth-nine tree. The
independent checker reconstructs the recurrence without importing THEORICA,
replays every node transition, verifies every terminal predicate appropriate
to the frozen families, reproduces the exact depths, and independently checks
the disjoint sibling-pair lower bound.

## Reproduction

```bash
python scripts/verify_adaptive_decision_lies.py
python scripts/audit_adaptive_decision_lies.py
pytest -q tests/test_corruption_resilient_features.py
```

Evidence is stored in `results/adaptive_decision_lies/` and is deterministic.

## Novelty boundary and limitations

Liar games, minimax dynamic programming, Hamming distance, sphere bounds, and
repetition codes are classical. The bounded contribution is their exact
integration with THEORICA's algebraic completion list and non-transitive
common-policy predicate, together with an executable adaptive-versus-fixed
scientific-query separation.

The current implementation is finite and exact, so its state space can grow
exponentially. Query outcomes must have declared finite alphabets; malformed
out-of-alphabet responses require a separate transport policy. The result does
not claim asymptotic optimality for unrestricted query design or noisy
stochastic channels.
