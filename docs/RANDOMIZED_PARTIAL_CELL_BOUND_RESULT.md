# Exact randomized partial-cell frontier

**Date:** 16 October 2026  
**Classification:** exact theorem extension with deployed runtime contract  
**Frozen protocol:** `97a0e93483b7ff9cee651f04f33b1f13eefdcc6c`

## Smallest supported claim

For the externally certified hidden-generator rack family `R(n,z,sigma)`, let
`R_alpha(n)` be the minimum worst-case number of adaptive classical randomized
cell queries required to locate `z` with success probability at least `alpha`.
Then, for `0 <= alpha <= 1`,

\[
\boxed{R_\alpha(n)=\max\{0,\lceil n\alpha-1\rceil\}.}
\]

Equivalently, the exact success frontier at query budget `q` is

\[
\boxed{P^*(n,q)=\frac{q+1}{n}},\qquad 0\le q\le n-1.
\]

The matching stop-on-hit algorithm uses expected

\[
q-\frac{q(q-1)}{2n}
\]

queries for every hidden label while retaining worst-case success `(q+1)/n`.
At `alpha=1`, the law recovers the prior deterministic zero-error boundary
`n-1` exactly.

## Proof

An off-diagonal cell query in row `x` returns a nonidentity value exactly when
`x=z`; it is a classical equality query for the hidden label.

**Upper bound.** Draw a uniformly random permutation of the `n` rows. Query the
first `q` rows and stop if a nonidentity response appears. After `q` identity
responses, guess the next row in the permutation. For every fixed `z`, success
occurs exactly when `z` occupies one of the first `q+1` permutation positions,
so the success probability is `(q+1)/n`.

**Lower bound.** Put the uniform distribution on `z`. Any deterministic
depth-`q` decision tree has at most `q` positive branches, each identifying the
queried row, plus one all-identity leaf that can correctly name at most one
unqueried label. It is therefore correct on at most `q+1` of the `n` labels.
Yao's minimax principle gives worst-case randomized success at most `(q+1)/n`.
The upper and lower bounds match, and inversion yields the stated query law.

## Exact evidence

| Gate | Result |
|---|---:|
| Frontier cases, `3 <= n <= 128` | 8,253 |
| Hidden-label symmetry checks | 707,259 |
| Confidence-inversion checks | 8,379 |
| Expected-call checks | 8,253 |
| Distributional lower-bound checks | 8,253 |
| Independent audit checks | 732,144 |
| Failures after plumbing correction | **0** |

- Primary canonical SHA-256:
  `b842563e98cc36ee03a73fcebec9ad1cfee0fec739803b2f0d6dcdeb0b41c3ba`
- Primary file SHA-256:
  `80f3b0b79edc404c1a9a27499ba6fdf2225671ce57ebcb0add79e1b7cd273031`
- Independent audit canonical SHA-256:
  `c3f3d89be84a054f8871c879c3babc7604779000632e4d5b87a0cb140c1af17e`
- Independent audit file SHA-256:
  `8563c4d2c356a96fdc769ac6252ca1291ed83b443205518bfbf16a7a16b53cd9`

## Preserved verifier failure

The first primary run reported 8,001 expected-call failures because its direct
check used `t^2/n` instead of `t/n` for a stop at position `t`. The success
frontier, confidence inversion, and lower-bound checks had no failures. The
failure receipt is preserved as
`results/randomized_partial_cell_first_failure_summary.json`; it records the
full source artifact SHA-256
`1d0ad5cae88164a9762096300c964cc5323d3a3e1fe63656911c52f47522b7b1`,
the source canonical payload
`d0eb8317088930f4eaabedb0fb5485a99ce978ea0ef2e993b256c25f24f5eab0`,
all failure counts, and the first 20 exact failures. Its own file SHA-256 is
`7d4d3dcf4f3446da016e7c95ec8a13527a441c9902b8a2784e181280dcfbbc77`.
The follow-up changed only that arithmetic line.

## Priority and claim boundary

The query lower bound is the standard classical unique-marked-item argument;
historical novelty is not claimed for it. The defensible contribution is the
exact rack-family reduction, the complete confidence/query frontier, the
independent certificate, and its integration into THEORICA's query planner.

This result does not cover noisy answers, uncertified family membership,
quantum queries, arbitrary racks, or correctness when the caller falsely
asserts the family certificate.

## SCIENCE ledger

- **TRUE:** each query buys exactly `1/n` additional worst-case success, from
  `1/n` without queries to certainty at `n-1` queries.
- **FALSIFIED ALTERNATIVE:** adaptivity or asymmetric randomization can exceed
  `(q+1)/n` on this certified family.
- **UNTESTED:** noisy-oracle and unknown-family identification.

## CONSEQUENCE ledger

THEORICA now exposes `locate_hidden_generator_randomized` with an exact rational
confidence request and receipt.

- The bounded-error path requires explicit authorization and a family
  certificate; otherwise it makes zero oracle calls and refuses.
- The query budget is derived from the theorem, not tuned empirically.
- `alpha=1` delegates to the deterministic locator and preserves the fail-closed
  zero-error default.
- Receipts distinguish exact localization from a bounded-error guess.

This changes the system from a single worst-case acquisition policy to an exact
confidence-budgeted planner for certified structural hypotheses.

