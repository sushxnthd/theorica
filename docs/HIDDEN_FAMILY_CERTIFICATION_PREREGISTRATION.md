# Hidden-family certificate verification boundary

**Frozen:** 17 October 2026  
**Program:** THEORICA  
**Branch:** `breakthrough-engine/nonfaithful-reconstruction-boundary-20261013`

## Exactly one active breakthrough kernel

- **Precise question.** Can THEORICA establish the `R(n,z,sigma)` family promise from cell access alone while retaining the `n-1` hidden-generator localization advantage, or is an external certificate an unavoidable trust boundary?
- **Best-known frontier.** The current exact planner localizes the hidden generator in `n-1` deterministic queries and attains randomized success `(q+1)/n`, but both results accept an unaudited Boolean `family_certified` input. Generic property testing treats one-sided verification and Hamming-distance testing, but the deployed rack interface has not stated or enforced the exact certificate-verification cost.
- **One exact objective.** Determine the zero-error query complexity and the complete one-sided randomized rejection frontier for verifying an explicit hidden-cycle-family witness against an arbitrary cell oracle.
- **Strongest alternative explanation.** Rack structure or adaptivity may allow the witness to be certified with substantially fewer than `n^2` cell queries, so the external trust boundary may be an implementation artifact rather than information-theoretic.
- **Cheapest decisive falsification.** Exhibit any sound zero-error verifier that omits one cell, or any `q`-query one-sided randomized verifier whose worst-case rejection probability against a one-cell corruption exceeds `q/n^2`.
- **Publishable success condition.** A matching exact law with proof, exhaustive finite checks, an independently written audit, and a runtime contract that distinguishes externally attested, fully verified, and probabilistically spot-checked certificates.
- **Project-relevance threshold.** The result must remove the bare Boolean certificate from the safe runtime path or prove why it cannot be removed without forfeiting the query advantage.
- **Kill condition.** Any counterexample to the claimed lower bound, disagreement between the primary and independent checkers, or no enforceable runtime consequence kills this extension.

No backup kernel is active in this run.

## Frozen theorem candidate

An explicit witness `C=(z,sigma)` defines one table `T_C`: every row other than `z` is the identity and row `z` fixes `z` and acts as the supplied full cycle `sigma` on the complement.

For arbitrary cell oracles `F:[n]^2 -> [n]`:

1. deterministic or Las Vegas zero-error verification of `F=T_C` has worst-case query complexity exactly `n^2`;
2. among randomized verifiers that always accept `T_C` and make at most `q` distinct queries, the largest worst-case rejection probability over all `F != T_C` is exactly `q/n^2`;
3. the exact query requirement for rejection confidence `beta` is `ceil(beta*n^2)`.

The intended lower-bound witness changes one unqueried cell. For the randomized bound, query-inclusion probabilities on the valid transcript sum to at most `q`; an adversary corrupts a minimum-inclusion cell. Uniform sampling without replacement matches the bound. For a table at Hamming distance `d`, uniform sampling rejects with exact probability

`1 - choose(n^2-d,q)/choose(n^2,q)`.

## Frozen implementation and evidence protocol

1. Add a full fail-closed verifier that scans all `n^2` cells and derives the hidden row only after verifying the family.
2. Add an explicitly bounded-error spot checker requiring a concrete `(z,sigma)` witness, authorization, rational rejection-confidence request, and deterministic RNG seed.
3. Refuse a bare Boolean family assertion in the new safe verification path.
4. Exhaust canonical forward and reverse cycles for every hidden row through `n=32`; exhaust every one-cell corruption and every replacement value.
5. Check the exact hypergeometric detection formula for every `0 <= q <= n^2` and selected multi-cell distances.
6. Run an independently written arithmetic/decision-tree audit through `n=24` without importing the primary verifier.
7. Preserve all failures and rerun byte-identically.

## Prior-art boundary

This protocol does **not** claim novelty for known-string equality testing, Hamming-distance sampling, or the elementary averaging lower bound. Property-testing work already establishes broad linear-query barriers for one-sided testing in adjacent models. The only potentially defensible contribution is the exact rack-certificate interface reduction, its complete finite certificate, and the resulting THEORICA trust-boundary change.

## Holdout integrity

No unopened public catalogue or frozen challenge is used. This is an exact theorem/interface audit; all finite enumerations are development evidence.

