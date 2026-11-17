# Frozen protocol: minimal ternary obstruction cost cone

## Question

For each of the three inclusion-minimal ten-word ternary families found at
costs `(1, 3, 1)`, determine whether the isolated budget gap extends to an
exact all-positive-cost law.

The experiment is restricted to depth-three ternary prefixes, four copies of
each physical prefix query, one substitution, one recognized erasure, and a
middle-level first action.  The candidate set is the eight binary words plus
one of the three unordered pairs from
`{(2,0,0), (2,1,0), (2,2,0)}`.

## Preregistered candidate

Let `(a,b,c)` be the positive integer root, middle, and leaf query costs.  Let

```text
B(a,b,c) = max(
  a + 5b + c,
  2a + 3b + 4c,
  2a + 4b + 3c,
  3a + 3b + 3c,
  3a + 4b + c,
  4a + 2b + c,
)
```

be the established binary middle-first law.  The preregistered ternary
candidate is

```text
M(a,b,c) = max(B(a,b,c), 2a + 5b + c).
```

The proposed mechanism is an additional root exposure forced by the minimal
ternary root fiber.  The new face is active exactly where
`2a + 5b + c > B(a,b,c)`.

## Discovery set

Run exact synthesis for every primitive positive triple with
`max(a,b,c) <= 4` on all three obstruction pairs.  A triple is primitive when
`gcd(a,b,c) = 1`.  The candidate is falsified immediately if the exact optimum
differs from `M(a,b,c)` for any pair.

## Prospective holdouts

Only if the discovery set passes, open these fixed triples on all three pairs:

```text
(1,5,1), (2,5,2), (1,4,2), (2,7,1),
(3,8,2), (2,9,3), (3,10,3), (4,11,2),
(5,13,4), (7,19,5), (11,29,7), (13,34,9)
```

The list deliberately includes predicted new-face points, binary-face points,
and boundary/tie cases at ratios outside the discovery grid.

## Exactness and independent check

The production solver must synthesize a feasible policy at the predicted
budget and prove infeasibility below it by its monotone integer search.  A
separate zero-import checker will reconstruct the ten-word query system and
verify, for every recorded case, infeasibility at `M-1` and feasibility at
`M` using an independent dynamic program.  It must also check the binary face
arithmetic, primitive enumeration, fixed holdout list, all three pairs, and
the active-face classification.

## Acceptance and claim boundary

Promote the candidate only if all discovery cases and all prospective
holdouts match for all three families, the independent checker agrees, the
artifacts reproduce byte-for-byte, and the full regression suite passes.
Otherwise preserve the first counterexample and retire the candidate.

Even on success, the result is not a law for all 27 ternary completions or for
arbitrary ternary augmentations.  It is an exact cost-cone claim only for the
three specified ten-word minimal-obstruction families and the fault/query
model above.
