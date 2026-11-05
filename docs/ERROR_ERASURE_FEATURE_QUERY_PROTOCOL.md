# Frozen protocol: exact feature queries with errors and erasures

## Kernel

For a known rational scenario-feature matrix of row rank `r`, determine the
smallest outcome-independent query set that reconstructs every certified
feature-span payoff when up to `t` returned scenario vectors are adversarially
wrong and up to `s` queried scenarios are explicitly unavailable.  Turn the
criterion into an executable fail-closed selector/decoder and replay its output
through exact robust planning.

## Prediction frozen before evaluation

A query set `Q` is sufficient exactly when its evaluation code has minimum
distance at least `2t+s+1`, equivalently when deleting any `2t+s` selected rows
preserves rank `r`.  Hence distinct-point Vandermonde/MDS geometry should attain
the tight query count `r+2t+s`; arbitrary geometry may require more or make the
budget impossible.  Decoding must ignore the known erasures and uniquely
correct the remaining errors.

## Evidence plan

- Open 120 seeded Vandermonde families spanning ranks 2--4, error budgets 0--2,
  erasure budgets 1--2, and 11--30 scenarios.
- Keep 30 fixed seeds untouched until the implementation and opened sweep pass;
  use 17, 29, 47, 71, and 97 scenarios and include rational quadratic/cubic
  feature maps not separately named by the production API.
- Construct 60 exact indistinguishable-transcript lower bounds at one query
  below `r+2t+s`, splitting a minimum-weight codeword between two error sets
  after erasing `s` known support positions.
- Independently reimplement rational rank, distance, decoding, and robust value
  without importing production code.
- Preserve a repeated-row geometry where the Singleton count is unattainable
  and require abstention before the oracle when the cap is insufficient.

## Strongest alternatives and decisive falsification

- **Error-only distance (`2t+1`).**  The cheapest falsification is an MDS query
  set of size `r+2t` followed by one known erasure and `t` errors; two payoff
  tables must produce the same surviving transcript.
- **Treat erasures as errors (`2(t+s)+1`).**  This is safe but predicts
  `r+2t+2s` MDS queries; the prospective sweep must show exact recovery with
  `r+2t+s` and no loss in robust value or policy.
- **Repeated-basis voting.**  Compare against `r(2t+s+1)` calls while noting its
  stronger repeated-call corruption semantics.

## Gates

Publishable threshold: exact theorem and proof, 120/120 opened cases, 30/30
untouched holdouts, 60/60 constructive lower bounds, independent agreement,
zero oracle calls on rejected geometry, full regression, deterministic evidence
digests, and explicit priority/limits.  Project consequence threshold: the same
decoded table must reproduce the exact robust value and policy.

Kill or reformulate if any MDS case needs more than `r+2t+s`, any valid
weight-bounded transcript has multiple decodings under the predicted distance,
the lower bound cannot change robust value, or the independent checker
disagrees.  This protocol does not claim novelty for the classical
error-and-erasure coding inequality.
