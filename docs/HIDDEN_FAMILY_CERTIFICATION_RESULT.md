# Exact hidden-family certificate verification boundary

**Date:** 17 October 2026  
**Classification:** exact interface theorem with enforced runtime consequence  
**Frozen protocol:** `0a373069e8001bf602bf7bc381646e8f7aee8587`

## Smallest supported claim

Let an explicit witness `C=(z,sigma)` define the operation table `T_C` on an
`n`-element carrier: every row other than `z` is the identity, while row `z`
fixes `z` and acts as the supplied full cycle `sigma` on the complement.  An
algorithm receives cell-query access to an otherwise arbitrary operation
`F:[n]^2 -> [n]`.

1. The deterministic and Las Vegas zero-error query complexity of certifying
   `F=T_C` is exactly

   \[
   \boxed{V_0(n)=n^2}.
   \]

2. For a one-sided randomized verifier that always accepts `T_C` and makes at
   most `q` distinct cell queries, the exact largest worst-case rejection
   probability over all `F != T_C` is

   \[
   \boxed{S^*(n,q)=\frac{q}{n^2}}.
   \]

3. The minimum query budget for worst-case rejection confidence `beta` is

   \[
   \boxed{V_\beta(n)=\lceil \beta n^2\rceil}.
   \]

If `F` differs from `T_C` in exactly `d` cells, uniform sampling without
replacement rejects with the exact probability

\[
1-\frac{\binom{n^2-d}{q}}{\binom{n^2}{q}}.
\]

Consequently, THEORICA's earlier `n-1` deterministic localization law and
`(q+1)/n` randomized localization law are genuine *promise-problem* gains.
They cannot also establish their own promise against an unrestricted oracle.

## Proof

**Zero error.** Querying every cell and comparing with `T_C` is sufficient.
If a deterministic verifier omits a cell on the valid transcript, change only
that cell to any other carrier value.  The invalid table produces the same
transcript, so the verifier cannot accept the valid table and reject the
corruption.  Conditioning a Las Vegas verifier on any random tape gives the
same argument; zero error therefore forces every cell to be queried in the
worst case.

**One-sided frontier.** Run any randomized `q`-query verifier on `T_C`.  Let
`p_i` be the probability that cell `i` is queried.  Because there are at most
`q` distinct queries, `sum_i p_i <= q`, hence some cell has
`p_i <= q/n^2`.  Corrupt only that cell.  One-sided completeness makes the
valid transcript accepting, so the corruption can be rejected only when that
cell is queried.  Worst-case rejection is at most `q/n^2`.  Conversely,
sampling `q` cells uniformly without replacement rejects every invalid table
with probability at least `q/n^2`, with equality for a one-cell corruption.
The confidence inversion and distance-`d` formula follow immediately.

## Exact evidence

| Gate | Result |
|---|---:|
| Canonical family instances through `n=32` | 1,047 |
| Production full-verifier acceptances | 1,047 |
| Exhaustive one-cell replacement witnesses | 13,934,554 |
| Active-row duplicate checks | 534,662 |
| Exact frontier checks | 11,465 |
| Hypergeometric checks | 750 |
| Production spot-check contract checks | 5,235 |
| Independent checks through `n=24` | 105,040 |
| Failures | **0** |
| Focused runtime tests | **58/58 PASS** |
| Byte-identical primary and audit rerun | **PASS** |

- Primary canonical SHA-256:
  `51a57e29ffdee1aaacbb7ed7419a31314b998dda178d9c7eb10cd1308cb09d42`
- Primary file SHA-256:
  `e58873c6df0c9087eea7ae1ca6be5deba946a57da53ec82c0d43c72f3a064fba`
- Independent canonical SHA-256:
  `89535b73c8319d661dab5ce617162d73d1a9118d5f69ccbdd4ce758efa45df6c`
- Independent file SHA-256:
  `d9bf46705eb63f5c9f4e6792f1aafafa0ae7fc05820ea4a5533009cc4b735d91`

The primary and independent programs share no membership predicate or
frontier implementation.  The audit materializes one corruption at every cell
and checks the averaging and hypergeometric laws using exact rational
arithmetic.

## Prior-art and novelty boundary

Known-string equality testing, Hamming-distance sampling, and the averaging
lower bound are standard.  Property-testing literature also contains broader
linear-query barriers for one-sided testing.  Historical novelty is therefore
**not claimed** for the abstract query theorem.

The defensible project result is the exact reduction of THEORICA's rack-family
certificate interface to this boundary, its independent finite certificate,
and the resulting removal of an ambiguous safety claim.  The prior `n-1`
planner is not self-certifying.

## SCIENCE ledger

- **TRUE:** local zero-error verification of an explicit hidden-cycle witness
  against arbitrary cell oracles costs `n^2`, exactly.
- **TRUE:** each spot query buys exactly `1/n^2` worst-case one-sided rejection
  probability; a single corrupted cell is the sharp adversary.
- **FALSIFIED ALTERNATIVE:** the `n-1` localization transcript can also certify
  the family promise.
- **LIMITATION:** the result does not rule out cheaper verification under an
  independently certified rack promise, cryptographic commitment, trusted
  provenance, or a distributional corruption model.

## CONSEQUENCE ledger

THEORICA now exposes two explicit safe choices:

1. `verify_hidden_cycle_family_by_cells` establishes membership and locates the
   generator without external trust, using exactly `n^2` calls.
2. `spot_check_hidden_cycle_witness` accepts a concrete `(z,sigma)` witness,
   requires bounded-error authorization below confidence one, derives the
   exact budget `ceil(beta*n^2)`, and emits a receipt containing its sharp
   worst-case rejection guarantee.

The existing `n-1` and randomized localization paths remain valid only when an
external family certificate is part of the trusted input contract.  A bare
Boolean assertion is no longer evidence that the promise was locally checked.

## Breakthrough gate

**System-level exact boundary: PASS.  Field-level historical novelty:
INCONCLUSIVE / not asserted.**  This is a consequential interface theorem, not
a claim to a new general property-testing lower bound.

