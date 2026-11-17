# Minimal ternary obstruction at `(1,3,1)`

## Result

The one-unit gap between the embedded binary cost 17 and the full ternary cost
18 is not caused by any single new ternary completion.  All **19/19** singleton
augmentations of the binary family remain feasible at budget 17.

The obstruction first appears at cardinality two.  Among all **171** unordered
pairs of genuinely ternary words, exactly three are infeasible at budget 17
and feasible at budget 18:

```text
{(2,0,0), (2,1,0)}
{(2,0,0), (2,2,0)}
{(2,1,0), (2,2,0)}
```

Thus every two-element subset of

```text
{(2,0,0), (2,1,0), (2,2,0)}
```

is a minimal obstruction relative to the embedded binary baseline.  Deleting
either added word returns to a certified cost-17 singleton instance.

## Mechanism

The hard interaction fixes the new root symbol `2` and the distinguished leaf
outcome `0`, while varying the middle symbol.  A single such word can be
absorbed by a cost-17 adaptive policy; any two force exact cost 18.

This localizes the missing ternary mechanism far more sharply than the full
27-word counterexample: the gap needs only the eight binary completions plus
two aligned ternary completions.

## Relabeling falsification

The frozen global-symbol-permutation test does **not** exhibit full ternary
alphabet symmetry:

- all **6/6** checks whose permutation fixes symbol `0` preserve exact cost 18;
- all **12/12** checks moving symbol `0` become feasible at budget 17.

This is structural, not a solver discrepancy.  The prefix-query library uses
`0` as the response outside the queried subtree, so global permutations that
move zero do not preserve the experiment.  Any future theorem must state this
distinguished-zero convention explicitly rather than claiming full alphabet
symmetry.

## Independent audit

A separate stdlib-only solver imports zero THEORICA modules and independently
replays:

- the binary baseline;
- all 19 singleton augmentations;
- all 171 pair augmentations;
- all 18 relabeling checks.

It visits **248,786** cached states and reproduces exactly the same three
obstructing pairs and the same 6/12 relabeling split.

## Consequence

The next lower-bound experiment should operate on the ten-word minimal hard
family, not the full 27-word space.  Its target is an adversary or transcript
support certificate explaining why two root-`2`, leaf-`0` words with distinct
middle symbols force one additional unit of weighted query cost.  The present
result does not yet prove a corrected global face or cost cone.

## Scope

The result is exact only at level costs `(1,3,1)`, arity three, depth three,
four copies, one substitution, one recognized erasure, the implemented
distinguished-zero prefix-query semantics, and a middle-first initial action.
Minimality is relative to adding words to `{0,1}^3`; it is not a classification
of every subset of the full ternary family.
