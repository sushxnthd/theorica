# Frozen protocol: finite policy fan for the minimal ternary obstruction

Status: frozen before any unopened holdout is solved.

## Question

The single added face `(2,5,1)` fits the complete primitive discovery grid but
overpredicts the exact value at `(2,9,3)`.  Test the more faithful mechanism
that a fixed adaptive policy has a max-linear terminal-exposure cost, while the
optimal planner selects the minimum over a finite set of such policies.

## Frozen construction

Use the same depth-three ternary prefixes, four copies, one substitution, one
recognized erasure, middle-first initial action, eight binary words, and three
minimal two-word root-fibre augmentations as the preceding cost-cone study.

For each obstruction pair separately:

1. Re-synthesize an exact optimal policy at each of the 55 primitive positive
   cost triples with `max(a,b,c) <= 4` already opened in discovery.
2. Walk every terminal transcript.  Replace its exposure set by the
   componentwise Pareto-maximal antichain of `(root,middle,leaf)` query counts.
3. Deduplicate policies solely by that antichain.  Retain every distinct
   antichain; do not hand-select faces or refit coefficients.
4. For cost vector `x`, define a stored policy envelope
   `U_P(x) = max_{e in E(P)} e dot x`, and the finite-fan prediction
   `F(x) = min_P U_P(x)`.

The construction is accepted for prospective testing only if it exactly
replays all 165 discovery cases and every previously opened holdout case for
that pair.  The stored source cost and exposure antichain must identify an
executable policy witness for every prediction.

## Prospective evaluation

Only after calibration passes, evaluate the still-unopened suffix of the
original holdout order.  At `(2,9,3)`, the first pair is calibration data from
the prior falsification; the other two pairs remain prospective.  For all
three pairs, `(3,10,3)`, `(4,11,2)`, `(5,13,4)`, `(7,19,5)`, `(11,29,7)`, and
`(13,34,9)` remain prospective.

For each case, record the fan prediction before exact solution, then require:

- production exact optimum equals the frozen prediction;
- the selected stored policy envelope equals that prediction;
- an independent standard-library dynamic program reconstructing the problem
  with zero THEORICA imports agrees on feasibility at the prediction and
  infeasibility one unit below.

Stop at the first prospective mismatch and preserve it.  Do not add discovery
policies after a mismatch.

## Interpretation boundary

Success establishes a finite executable policy fan on these three ten-word
families and the frozen holdouts.  It does not by itself prove completeness of
the fan over every positive cost vector, a symbolic lower-bound theorem, or a
law for arbitrary ternary completion families.  Failure falsifies this
discovery-generated fan and forces the next experiment to change mechanism.
