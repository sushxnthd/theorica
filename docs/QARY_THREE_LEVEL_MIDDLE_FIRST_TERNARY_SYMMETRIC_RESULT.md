# Exact ternary symmetric middle-first theorem

## Theorem

For ternary depth-three prefixes with four physical copies per prefix, one
adversarial substitution, one recognized erasure, and the first query required
to be at the middle level, equal positive level cost `x` has exact worst-case
cost

```text
T_3(x) = 9x.
```

The lower bound is inherited by embedding the binary completion family, whose
exact equal-cost value is nine.  Ternary queries outside that embedded family
are constant there and cannot improve the binary adversary bound.  For the
upper bound, exact ternary policy synthesis constructs a depth-nine robust
tree over all 27 completions.

## Exact evidence

- exact unit-cost optimum and depth: **9**;
- ternary completions: **27**;
- exact weighted-search states: **125,698**;
- compatibility states: **954**;
- terminal policy transcripts: **2,721**;
- six prospective positive scales: **6/6** by exact homogeneity;
- independent stdlib-only solver: depth eight infeasible, depth nine feasible;
- independent states: **78,460**;
- independent THEORICA imports: **0**.
- full regression: **287/287** tests;
- scoped Ruff and diff-integrity checks: clean.

The verifier and independent audit reproduce their JSON artifacts
byte-for-byte.  The executable
`certify_ternary_middle_first_symmetric(level_cost)` capability returns the
exact value and fails closed on nonpositive, Boolean, or nonintegral costs.

## Broader hypothesis status

Four asymmetric ternary scalar probes—`(1,2,1)`, `(2,1,1)`, `(1,1,2)`, and
equal costs—also matched the binary six-face formula exactly.  These probes are
recorded as directional evidence, not a theorem.  The frozen all-positive-cost
protocol remains open because cone-uniform ternary policy synthesis did not
complete within this run; no claim is inferred from scalar agreement alone.

## Reproduce

```bash
PYTHONPATH=src:scripts python \
  scripts/verify_qary_three_level_middle_first_ternary_symmetric.py
python scripts/audit_qary_three_level_middle_first_ternary_symmetric.py
```

## Limitations

The theorem covers only arity three, depth three, equal level costs, four
copies, one substitution, one recognized erasure, and a middle-first initial
action.  It does not establish the all-positive ternary formula, all arities,
higher depth, fewer copies, larger fault budgets, unrestricted first actions,
or optimality among arbitrary query families.
