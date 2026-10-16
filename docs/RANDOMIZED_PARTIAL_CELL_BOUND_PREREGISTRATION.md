# Randomized partial-cell hidden-generator boundary

**Frozen:** 16 October 2026  
**Classification:** exact theorem extension and runtime-contract test  
**Parent result:** deterministic zero-error complexity `n - 1`

## Precise question

For the externally certified rack family `R(n,z,sigma)`, what is the exact
worst-case number of adaptive randomized cell queries needed to locate the
hidden generator `z` with success probability at least `alpha`?

The candidate law is

```text
R_alpha(n) = max(0, ceil(n * alpha - 1)).
```

The theorem is about classical randomized queries. It does not cover noisy
answers, uncertified family membership, quantum queries, or arbitrary racks.

## Mechanism

An off-diagonal query in row `x` is exactly the equality test `x == z`.
A `q`-query randomized algorithm samples `q` distinct rows uniformly, probes
them in random order, and, after an all-identity transcript, guesses uniformly
among the `n-q` unqueried rows. Its success probability is `(q+1)/n` for every
hidden label.

The proposed lower bound is distributional: under a uniform hidden label, any
deterministic depth-`q` decision tree can be correct on at most its `q`
positive branches plus one label on the all-identity branch. Yao's principle
then bounds every randomized algorithm's worst-case success by `(q+1)/n`.

## Exact objectives and gates

All gates must pass:

1. prove the upper and lower bounds symbolically;
2. exhaust every `3 <= n <= 128` and `0 <= q <= n-1` with exact rational
   arithmetic;
3. verify the symmetric algorithm has identical success `(q+1)/n` for every
   hidden label;
4. verify the minimum query budget for every grid confidence
   `alpha in {0,1/n,...,1}` equals `max(0,ceil(n*alpha-1))`;
5. verify exact expected calls
   `q - q(q-1)/(2n)` for the stop-on-hit implementation;
6. independently reproduce all formulas and boundary cases without importing
   the primary verifier;
7. add a fail-closed runtime primitive that requires both the family
   certificate and an explicit bounded-error authorization;
8. preserve the deterministic zero-error path as the default at `alpha=1`.

## Strongest alternative explanation

Adaptive choice of cells or nonuniform randomization might outperform sampling
distinct rows. The distributional bound is decisive: every query can test at
most one previously unresolved candidate, and the all-identity leaf can name
at most one additional candidate.

## Publishable success and consequence

The generic marked-item lower bound is standard, so historical novelty is not
claimed for that core. Success is the exact rack-family reduction, matching
finite certificate, and a deployed THEORICA planner that exposes the precise
confidence/query frontier instead of treating randomization as an informal
heuristic.

## Kill condition

Any exact counterexample to the law, nonuniform hidden-label success, runtime
contract violation, or independent-audit mismatch kills the extension. No
confidence grid or family definition may be changed after this commit.

## Ledgers

### SCIENCE

- **KNOWN:** deterministic zero-error complexity is exactly `n-1`.
- **HYPOTHESIS:** bounded error buys exactly one additional candidate per query,
  giving success `(q+1)/n` and no more.
- **ALTERNATIVE:** adaptivity or asymmetric randomization beats the symmetric
  search frontier.

### CONSEQUENCE

- **PASS:** expose an explicit confidence-budgeted cell planner for certified
  instances, with zero-error remaining the default.
- **FAIL:** retain only deterministic localization; do not expose probabilistic
  seed claims.

