# Multiset quotient is exact but insufficient

## Result

The frozen hypothesis that identical-copy quotienting alone would open a
previously timed-out unrestricted depth-four case is falsified.

The implementation groups physical queries only when both their complete
outcome row and integer cost are identical. A remaining state stores one count
per group, while each returned tree node receives the next unused original
physical index. This is an exact orbit quotient under permutations of
identical copies; it does not remove an adaptive action.

For the binary depth-four library there are 15 distinct prefix rows and four
copies of each. The raw remaining-query representation falls from `2^60`
indexed subsets to `5^15` count vectors, a factor of approximately 37.78
million. An independent standard-library audit reconstructed this count with
zero THEORICA imports.

## Exact evidence

- The opened uniform calibration reproduced unrestricted cost 10 and depth 10.
- It solved 969,398 cost-bounded states and 1,528 compatibility states in
  51.49 seconds.
- All 51 focused corruption-resilient-feature tests passed, including a new
  root-to-leaf check that no physical query index is reused.
- The solver now accepts an independently certified feasible upper bound; for
  q-ary prefix instances the root-respecting theorem supplies that bound.
- Full scanner semantics and missing-copy abstention remain unchanged.

## Preserved negative result

The formerly timed-out `(20,1,1,1)` case still exceeded 240 seconds even with:

1. exact copy-permutation quotienting;
2. the sharp root-respecting feasible upper bound 83 instead of the sum of all
   query costs; and
3. cost- and balance-aware query ordering.

An exploratory run of the frozen interior case `(2,7,1,3)` also produced no
result within 90 seconds and was interrupted rather than reported as an
optimum. The remaining prospective values were not opened after the primary
acceptance criterion failed.

## Consequence and kernel decision

Copy labels were a real 37.78-million-fold representational redundancy, but
they were not the dominant source of exact-search complexity. The hard states
come from partially compatible fault transcripts and ancestor-bypass choices,
not from physical-copy permutations.

Under the kill rule, the “larger brute force after symmetry quotient” kernel is
retired after this decisive falsification. The replacement kernel is an
**ancestor-bypass dominance certificate**: derive statewise lower bounds that
prove when querying descendants before an unresolved ancestor can or cannot
improve the root-respecting recurrence.

## Scope

The quotient implementation is exact and useful as an executable reduction,
but this result is not a depth-four closed form and establishes no new
unrestricted optimum beyond the opened uniform calibration. The timed-out
cases remain unresolved, explicitly and durably.
