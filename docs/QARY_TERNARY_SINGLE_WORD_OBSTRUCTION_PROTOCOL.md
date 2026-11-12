# Frozen protocol: minimal ternary obstruction at `(1,3,1)`

## Question

The embedded binary family predicts cost 17 at ternary level costs `(1,3,1)`,
while the full 27-word ternary family has exact cost 18.  Determine whether a
single genuinely ternary completion already causes this gap or whether the
obstruction requires an interaction among multiple new words.

## Frozen baseline and order

Let `B = {0,1}^3`, embedded in the ternary completion space `{0,1,2}^3`.
The exact binary theorem gives `T(B)=17` under four copies, one substitution,
one recognized erasure, and a middle-level first action.

Enumerate the 19 words in `{0,1,2}^3 \ B` in lexicographic order.  For every
word `w`, solve exact budget-17 feasibility on `B union {w}`.  Do not stop at
the first obstruction; open all 19 singleton augmentations.

If every singleton remains feasible, test unordered pairs in lexicographic
order.  If one or more singletons are infeasible, pairs are out of scope for
this run.

## Acceptance criteria

A singleton obstruction requires all of:

- `B` is feasible at budget 17;
- `B union {w}` is infeasible at budget 17;
- `B union {w}` is feasible at budget 18;
- all 19 singleton outcomes are preserved, including negative results;
- the obstruction is tested under every global ternary-symbol permutation;
- a separate zero-production-import solver reproduces the baseline and all
  singleton feasibility decisions;
- deterministic evidence regenerates byte-for-byte;
- full regression, Ruff, and diff-integrity checks pass.

## Mechanistic consequence

If a singleton suffices, the binary envelope fails because one ternary word
creates a specific new indistinguishability obstruction; no collective
19-word interaction is needed.  The word and its symbol-permutation orbit
become the next lower-bound target.  This does not by itself prove a corrected
global cost formula.

## Scope

The experiment is restricted to the frozen `(1,3,1)` weighted point, arity
three, depth three, four physical copies, one substitution, one recognized
erasure, and a middle-first initial action.  It does not establish minimality
under arbitrary deletion from the full 27-word family, characterize a cost
cone, or prove an unrestricted ternary theorem.
