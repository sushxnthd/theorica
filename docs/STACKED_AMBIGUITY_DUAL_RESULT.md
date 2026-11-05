# Sparse dual certificates for stacked ambiguity

## Result

Let `U` be the exact rational payoff matrix obtained by stacking every labelled
scenario column from every completion that survives corrupted algebraic
observations. Assume each completion has the same individual robust value `v`.
If the stacked game has value `v_stack` and ambiguity gap
`Delta = v - v_stack`, then there is a probability distribution `q` over the
labelled scenarios such that

`max_i sum_j q_j U[i,j] = v_stack = v - Delta`.

Moreover, an optimal `q` can be chosen with support at most the number `a` of
actions. The implementation returns this weighted dual witness together with
the stacked primal policy and exact expected payoff of every action.

This is strictly more informative than the earlier unweighted incompatibility
witness: it gives an independently replayable upper bound on every randomized
policy and quantifies the unavoidable loss caused by ambiguity.

## Proof

The stacked problem is a finite zero-sum game. Finite minimax duality gives

`max_p min_j sum_i p_i U[i,j] = min_q max_i sum_j q_j U[i,j]`.

The left side is `v_stack`; hence any optimal column strategy `q` establishes
the stated equality. Since every pure action has expectation at most
`v_stack` under `q`, every convex combination of actions does too.

For sparsity, write the column player's equilibrium as its linear program.
At an optimal basic feasible solution, at most `a` probability variables need
be positive (equivalently, one may use the standard sparse-equilibrium support
argument). Thus a certificate with support no greater than the number of
actions always exists.

The sharp `a`-action face family has one critical column per action, each
penalizing its corresponding action. Its unique optimal dual is uniform on all
`a` critical columns, yielding `v_stack = -1/a` and `Delta = 1/a`; deleting any
column lets its action escape. Therefore the support bound is sharp.

## Frozen prospective and falsification results

| Family | Exact result |
|---|---:|
| Opened zero-gap duals | 40/40 |
| Held-out zero-gap duals | 20/20 |
| Known sharp duals (3–5 actions) | 20/20 |
| Prospective six-action sharp duals | 10/10 |
| Asymmetric games with extra scenarios | 20/20 |
| Unequal-value abstentions | 20/20 |
| Independent exact primal-dual replays | 50/50 |

All sharp six-action cases returned uniform weight `1/6`, value `-1/6`, gap
`1/6`, and support exactly six. Every other returned support was at most the
action count. The independent checker imports no production code and
reproduced the primary case digest:
`723f8081fc7633a706afbc1953b5c9577947759c357fa3196da386b46acc8d8c`.

## Executable consequence

THEORICA can now distinguish three outcomes:

1. unequal individual completion values: abstain before composing;
2. equal values and zero gap: emit a common robust plan plus matching exact
   primal and dual certificates;
3. positive gap: abstain with a sparse weighted mixture of labelled completion
   scenarios proving that no randomized plan can recover more than
   `v - Delta`.

An auditor can verify the third outcome by summing rational payoffs only; it
does not need to trust the solver transcript or rerun vertex enumeration.

## Reproduction

```bash
uv run python scripts/verify_stacked_ambiguity_dual.py
uv run python scripts/audit_stacked_ambiguity_dual.py
uv run --with pytest pytest -q tests/test_corruption_resilient_features.py
```

The primary and independent evidence is stored in
`results/stacked_ambiguity_dual/` and is deterministic across reruns.

## Novelty boundary and limitations

Finite minimax duality, linear-program basic solutions, and sparse equilibrium
support are classical. The contribution claimed here is their exact
composition with THEORICA's corrupted algebraic version space, labelled
scenario provenance, fail-closed abstention rule, and independently replayable
certificate—not a new minimax theorem.

The result currently covers finite games with exact rational payoffs. Exact
vertex enumeration scales combinatorially: the frozen asymmetric regression
uses three- and four-action games with dominated extra scenarios, while the
structured prospective sharp sweep reaches six actions. Five-action
asymmetric-extra instances were profiled but excluded from the hourly
regression because they take roughly 24 seconds per case with the current
enumerator. Approximate, continuous, and floating-point games require separate
error bounds and are not covered.
