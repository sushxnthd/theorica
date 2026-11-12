# Frozen protocol: exact all-positive-cost policy fan

Status: frozen before final synthesis, prospective evaluation, and independent
audit.

## Question

Can the universal six-face lower boundary be matched for every positive root,
middle, and leaf cost by replacing the falsified one-policy-per-face proof with
a finite polyhedral policy fan?

## Predicted theorem

For every positive integer cost triple `(a,b,c)`, the exact worst-case cost in
the binary, four-copy, one-substitution, one-erasure class conditioned on a
middle-level first query is

```text
max(
  a + 5b + c,
  2a + 3b + 4c,
  2a + 4b + 3c,
  3a + 3b + 3c,
  3a + 4b + c,
  4a + 2b + c
).
```

The prior affine adversary recursion supplies the universal lower bound. Five
face-active cones have one matching policy each. The exceptional `(3,4,1)`
cone is covered by six simplicial cells. Two cover its outer wings. Four share
the interior ray `(2,2,1)` and partition its zero-leaf edge at ancestor ratios
`1/2, 2/3, 1, 3/2, 2`.

## Frozen proof obligations

- Synthesize one exact policy for every cell using simultaneous remaining
  budgets at the cell's three generating rays.
- Replay every terminal transcript and retain its three-level exposure vector.
- Prove each exposure lies below `(3,4,1)` on all three cell rays.
- Verify exactly that the six cell cones cover the full five-ray exceptional
  cone, with no positive-cost gap.
- Combine these six policies with the five previously successful single-face
  policies to cover the positive cost orthant.
- Test the 18 frozen, untouched positive integer triples in the config against
  the exact scalar planner.
- Independently reproduce ray budgets, terminal exposure inequalities, fan
  coverage, and prospective costs using the Python standard library only.
- Reproduce all evidence byte-for-byte.

## Preserved falsification

The preceding result remains part of the proof history: no single policy
covers all five rays of `(3,4,1)`, and only 2/10 triples of its original
extreme rays are feasible. The new internal boundary rays are required, not a
cosmetic re-expression of that failed triangulation.

## Claim boundary

The theorem remains conditioned on binary arity, depth three, four copies per
query, one substitution, one erasure, and a middle-level first action. It does
not cover unrestricted first actions, higher arity, deeper trees, other fault
budgets, or establish novelty relative to an external literature review.

Kill or reformulate on any infeasible cell, exact coverage gap, prospective
mismatch, transcript-budget violation, or independent-audit disagreement.
