# Frozen protocol: ternary middle-first universality test

Status: frozen before ternary policy synthesis and prospective execution.

## Hypothesis

The binary all-positive-cost law may be arity-invariant at arity three.  For
positive level costs `(a,b,c)`, the ternary, four-copy, one-substitution,
one-erasure problem conditioned on a middle-level first query is predicted to
have exact value

```text
max(
  a + 5b + c,
  2a + 3b + 4c,
  2a + 4b + 3c,
  3a + 3b + 3c,
  3a + 4b + c,
  4a + 2b + c,
).
```

Scalar agreement is insufficient.  The decisive experiment must synthesize
policies whose transcript-exposure vectors certify the complete positive cost
cone, including any refinement required on the exceptional `(3,4,1)` face.

## Frozen tests

- Recompute the exact ternary optimum on asymmetric prospective cost triples,
  not only equal-cost examples.
- Synthesize every ordinary face policy on its extreme rays.
- Test the binary six-cell exceptional-face fan unchanged; if it fails, retain
  the counterexample and derive the smallest exact ternary refinement.
- Verify every terminal transcript against all defining rays.
- Independently replay scalar optima, exposure inequalities, and fan coverage
  without importing THEORICA.
- Require deterministic byte-for-byte artifacts and a clean full regression.

## Decision rule

Promote an arity-three theorem only if every face/fan cell is certified and all
prospective scalar holdouts are exact.  If any cell or holdout fails, preserve
the failure as an arity boundary and reformulate rather than broadening the
claim.

## Claim boundary

Success would cover arity three, depth three, four physical copies per prefix,
one substitution, one recognized erasure, and a middle-level first action.
It would not by itself prove all arities, higher depth, fewer copies, larger
fault budgets, unrestricted first actions, or optimality among arbitrary query
families.
