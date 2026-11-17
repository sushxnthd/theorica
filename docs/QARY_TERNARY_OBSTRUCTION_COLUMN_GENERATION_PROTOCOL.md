# Frozen protocol: counterexample-guided exposure-antichain columns

Status: frozen before any remaining holdout-family case is opened.

## Mechanism

Replace post-hoc face fitting with counterexample-guided policy column
generation.  A column is the componentwise Pareto-maximal antichain of terminal
`(root,middle,leaf)` exposures of one executable adaptive policy.  Its cost is
the max-linear envelope of that antichain; the planner's finite-fan bound is the
minimum across retained columns.

Initialize each of the three obstruction-family fans with the discovery-policy
columns serialized by the preceding experiment.  Replay the 181 already-opened
cases in their frozen order.  At the first mismatch:

1. synthesize an exact policy at that already-opened cost;
2. extract its Pareto exposure antichain without fitting coefficients;
3. require the antichain to be new and add it only to that obstruction family;
4. restart the ordered calibration replay.

Iterate until every opened case matches or until a mismatch yields no new
column, which falsifies the algorithm.  No unopened case may supply a column.

## Prospective gate

Only after 181/181 calibration closure, serialize predictions for the 20
still-unopened pair/cost cases: the two unopened pairs at `(2,9,3)` and all
three pairs at `(3,10,3)`, `(4,11,2)`, `(5,13,4)`, `(7,19,5)`, `(11,29,7)`,
and `(13,34,9)`.

Then execute in that order, stopping at the first mismatch.  Each opened
prospective case must satisfy all of the following:

- the selected stored policy envelope equals the frozen prediction;
- the production exact optimum equals the prediction;
- an independent standard-library solver with zero THEORICA imports proves
  feasibility at the prediction and infeasibility one unit below.

## Success and failure

Success means the calibration-closed finite column set makes exact executable
predictions on all 20 remaining cases.  It does not prove completeness over all
positive costs.  Failure preserves the first counterexample and forbids adding
its policy: prospective data may falsify this fan but may not train it.

This is a genuine mechanism change from the two retired hypotheses.  The first
used one fitted face; the second sampled only policies scalar-optimal on the
small discovery grid.  This protocol uses an ordered separation oracle over
already-opened evidence and propagates complete policy exposure antichains.
