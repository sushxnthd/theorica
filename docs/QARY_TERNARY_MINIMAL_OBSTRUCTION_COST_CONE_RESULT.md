# Minimal ternary obstruction cost cone: falsified single-face law

## Result

The preregistered replacement law

```text
M(a,b,c) = max(B(a,b,c), 2a + 5b + c)
```

is false.  Here `B` is the established binary six-face middle-first law.
The candidate survived the complete primitive discovery grid and then failed
on a prospective holdout exactly as required by the frozen protocol.

For the family consisting of the eight binary words plus
`{(2,0,0), (2,1,0)}`, at costs `(2,9,3)`:

```text
binary six-face value:       50
exact ternary family value:  51
proposed new face:           52
```

Thus the minimal obstruction really does add one unit beyond the binary law,
but its unequal-cost boundary is not the maximum of the binary fan and the
single linear exposure `(2,5,1)`.  The isolated `(1,3,1)` equality was
insufficient to identify a global face.

## Preregistered evaluation

- 55 primitive positive triples with `max(a,b,c) <= 4`
- 3 minimal obstruction pairs per triple
- all 165 discovery cases matched
- 12 holdout-list triples frozen before execution; one, `(1,4,2)`, was
  inadvertently duplicated from the discovery grid, leaving 11 genuinely
  unseen triples
- the first five opened holdout-family cases matched
- the sixth opened holdout-family case, `(2,9,3)` on the first pair, falsified
  the candidate; remaining holdouts were not opened
- 181 total exact cases, 180 candidate matches
- 4,830,453 production search states

The fail-fast rule matters: no replacement coefficients were fitted after the
holdout was observed.

## Independent verification

A separate standard-library checker imports zero THEORICA modules.  It
reconstructs the ternary prefix-query system, four-copy multiplicities,
middle-first restriction, substitution transitions, and recognized erasure.
For every opened case it checks feasibility at the recorded exact cost and
infeasibility one unit below.

- 181/181 feasible at the recorded optimum
- 181/181 infeasible one unit below
- 1/1 candidate mismatch, at the final fail-fast case
- exact preregistered case-order prefix recovered
- 1,557,114 independent dynamic-program states

In particular, the independent calculation certifies infeasibility at 50 and
feasibility at 51 for the `(2,9,3)` counterexample, while direct arithmetic
gives 52 for the retired face.

## Consequence

The next model must permit policy switching or another set-valued mechanism;
a single additional adversarial exposure vector cannot explain the observed
cost cone.  A useful next experiment is to synthesize a finite policy fan from
exact terminal exposures and preregister its lower envelope on the unopened
holdouts.  Those holdouts remain untouched by this run.

## Scope and limitations

This is falsification evidence, not a replacement theorem.  It is restricted
to depth-three prefixes, arity three, four query copies, one substitution, one
recognized erasure, middle-first initial queries, and the specified ten-word
family.  It does not establish the exact global cone for that family, transfer
the mismatch to the other two obstruction pairs, or make a claim about all 27
ternary completions.

The duplicated `(1,4,2)` entry is a preregistration-design defect and is
reported rather than silently removed.  It does not affect the decisive
counterexample: `(2,9,3)` lies outside the discovery grid and was unopened
before the holdout stage.
