# Moving symbol zero breaks policy transport but preserves two scalar endpoints

## Structural falsification

The completed symbol-orbit results required alphabet maps that fixed symbol 0.
The stronger conjecture that every coordinatewise alphabet permutation
conjugates the prefix-query game is false.

Applying `0 <-> 1` to P0 produces the unseen family

`111, 110, 101, 100, 011, 010, 001, 000, 211, 201`.

The prefix-query library returns 0 both for an observed zero and outside the
active prefix.  Moving zero therefore changes which completions are merged in
query cells.  Five rounds of level-coloured refinement separate the source and
target incidence graphs by color-class multiplicity.  No level-preserving
query-cell isomorphism exists, so exact policies cannot be transported by the
previous orbit certificate.

## Preserved negative result

Despite the structural failure, the two preregistered scalar endpoints and
root signatures coincide exactly:

| `c` | source/target value | unique root group | source/target children |
| ---: | ---: | ---: | --- |
| 18 | 37 | 0 | `[33,33,33]` |
| 19 | 38 | 0 | `[34,34,33]` |

This negative result is important: agreement of values, optimal root actions,
and one-step child values does not certify mechanism-level equivalence.  A
consumer may cache the scalar endpoint here, but it may not transport the
policy or its proof through the zero-moving relabelling.

## Concrete planning consequence

The exact solver explored a substantially larger target game at both costs:

| quantity | source | zero-moving target | ratio |
| --- | ---: | ---: | ---: |
| Bellman states | 5,392 | 24,497 | 4.543x |
| evaluated actions | 4,571 | 24,241 | 5.303x |

These counts are implementation-level search evidence, not an intrinsic lower
bound on all algorithms.  They nevertheless provide a concrete consequence
of losing the certified quotient: the existing exact planner cannot reuse the
source orbit and must solve a much larger labelled state space.

## Independent audit and limits

The zero-production-import audit reconstructs all four endpoint minima from
the emitted root actions, verifies ordered child vectors and unique optimal
groups, checks the frozen color-multiplicity separation, and confirms that the
completed 18-case panel was not reopened.

The result proves an impossibility boundary for the current prefix-query
encoding.  It does not prove that every zero-moving family changes policy
structure, nor that the observed search ratios are universal.  It also leaves
open whether a different query encoding with an explicit outside-prefix token
restores full alphabet covariance.
