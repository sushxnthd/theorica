# Exact q-ary adaptive lie law

## Theorem

Fix `q >= 2`. Index `q^m` pairwise-incompatible robust decisions by q-ary
words of length `m`. For every prefix, expose three physical copies of the
query that returns the next q-ary symbol inside that prefix subtree and zero
outside it. With at most one adversarial answer substitution, the exact
minimum worst-case adaptive depth is

`D_q(m,1) = 2m + 1`.

Every fixed schedule requires at least

`3 q^(m-1)`

queries. Thus increasing the answer alphabet leaves adaptive depth linear in
word length while the certified fixed lower bound grows exponentially.

## Proof

For the upper bound, query the current prefix twice. If the answers agree,
all other first-symbol subtrees have already spent two discrepancies and are
eliminated; the selected subtree is the same height-`m-1` problem with the lie
still possibly unused. If the answers disagree, use the third copy. Its
majority identifies the first symbol, the single lie is spent, and the
remaining `m-1` symbols need one clean query each. Therefore

`D_q(m,1) <= max(2 + D_q(m-1,1), 3 + m - 1) = 2m + 1`,

with `D_q(1,1)=3`.

For the matching lower bound, use prefix dominance. Before the current symbol
is resolved, a query strictly below one candidate child is identically zero
on every other child. The adversary can choose another child and make that
query convey no information. Exchanging it with a current-prefix query cannot
increase worst-case depth. The adversary then returns the same true symbol on
the first two current-prefix queries. Any one of those answers could still
have been the sole lie, so the selected subtree retains the full one-lie
state. Hence `D_q(m,1) >= 2 + D_q(m-1,1)`, and induction gives `2m+1`.

For a fixed schedule, each sibling group differs only on its leaf-parent
query. One-lie identification needs Hamming distance at least three, so all
three copies of every one of the `q^(m-1)` leaf-parent queries are mandatory.

## Exact evidence

| Arity | Depth | Completions | Adaptive optimum | Fixed lower bound | Saving |
|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 2 | 3 | 3 | 0 |
| 3 | 1 | 3 | 3 | 3 | 0 |
| 4 | 1 | 4 | 3 | 3 | 0 |
| 2 | 2 | 4 | 5 | 6 | 1 |
| 3 | 2 | 9 | 5 | 9 | 4 |
| 3 | 3 | 27 | 7 | 27 | 20 |
| 4 | 2 | 16 | 5 | 12 | 7 |
| 5 | 2 | 25 | 5 | 15 | 10 |

The three prospective cases all matched. The strongest holdout uses 27
incompatible decisions: seven adaptive queries versus a fixed lower bound of
27. Removing one required leaf-parent copy makes exact robust identification
impossible.

An independent standard-library implementation, importing no THEORICA code,
reconstructed all eight exact optima and the missing-copy abstention. The
production constructor `qary_prefix_query_library` turns the theorem into an
executable query design; the generic exact planner returns its minimizing
policy and rational terminal decisions.

## Reproduction

```bash
python scripts/verify_qary_adaptive_lie_law.py
python scripts/audit_qary_adaptive_lie_law.py
pytest -q tests/test_corruption_resilient_features.py
```

Raw deterministic evidence is under `results/qary_adaptive_lie_law/`.

## Limits and novelty boundary

The theorem is for this prefix-query library, one adversarial substitution,
and a finite exact completion list. It is not an unrestricted q-ary liar-game
capacity theorem. Dynamic programming, repetition and feedback coding are
classical; the contribution is the sharp nonbinary boundary, executable
algebraic decision planner, exact holdouts and adaptive/fixed separation.
