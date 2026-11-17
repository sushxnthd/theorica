# Exact clean-separator boundary at the ternary witness state

## Theorem (fixed state and cost ray)

Consider the post-erasure witness state with level costs `(a,b,c)=(3,10,3)`,
eight binary-cube completions at lie count one, two added completions at lie
count zero, and the frozen remaining-query multiplicities.  Then:

1. for P2, a middle query cleanly separates the two zero-lie completions from
   each other and from every one-lie completion, and the exact residual value
   is `3*b = 30`;
2. for P0, no remaining middle query has this clean-separator property, and
   the exact residual value is `a + 3*b = 33`;
3. the exact P0/P2 residual gap is `a = 3`.

This is an executable state predicate: enumerate middle response cells and
test whether each zero-lie completion occupies its own cell without any
one-lie completion.  The predicate selects the correct sharp residual branch
on both preregistered families at the unseen cost ray.

## Exact evidence

The P0 holdout was frozen before execution.  All three remaining middle
partitions fail clean separation.  Query groups 1 and 2 keep both zero-lie
completions together; query group 3 separates them, but one shares a cell with
all eight one-lie completions.

Exhaustive Bellman search proves matching lower and constructive upper bounds
of 33.  It evaluates 4,571 actions over 5,392 value states and 135
compatibility states.  Two first actions attain the optimum:

- root query group 0, cost 3, child values `[16,16,30]`;
- middle query group 3, cost 10, child values `[23,20]`.

The previously frozen P2 calculation gives matching bounds of 30, so the gap
is exactly 3.  A separate zero-production-import audit reconstructed every
middle partition from the evidence, recomputed the formula, and checked the
reserved-case accounting.

## Scope and limitations

The theorem is exact only for the frozen post-erasure state, these two
families, and the cost ray `(3,10,3)`.  It does not prove that clean separation
is necessary or sufficient for arbitrary states, cost ratios, or completion
families.  It also does not establish the complementary P1 orbit separately.
Exactly two reserved family/cost cases have now been opened; 16 remain sealed.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_ternary_no_clean_separator.py
PYTHONPATH=src python scripts/audit_qary_ternary_no_clean_separator.py
```

The deterministic artifacts are in
`results/qary_ternary_no_clean_separator/`.
