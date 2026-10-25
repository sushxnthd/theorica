# Exact feature queries with adversarial errors and known erasures

## Smallest supported claim

Let `Phi` be a known rational scenario-feature matrix of row rank `r`, and
suppose every payoff component is certified to lie in its column span.  If up
to `t` returned scenario vectors can be adversarially wrong and up to `s`
queried scenarios can be explicitly unavailable, a queried row set `Q` permits
exact reconstruction of every payoff table if and only if

`d_min(C_Q) >= 2t+s+1`,

where `C_Q = {Phi_Q beta}` is the rational evaluation code.  Equivalently,
deleting any `2t+s` rows from `Phi_Q` leaves rank `r`.  Distinct-point
Vandermonde and Cauchy families therefore attain the tight count
`r+2t+s`; arbitrary feature geometry can require more queries or make the
budget impossible.

This is a classical error-and-erasure decoding law, not a new coding theorem.
The contribution in this branch is an executable, outcome-independent THEORICA
selector and exact rational decoder, constructive robust-value lower bounds,
prospective validation on a second algebraic family, and a fail-closed project
boundary.

## Proof

After the locations of `s` erasures are known, puncture the query code at those
coordinates.  Two remaining codewords can be confused after at most `t` errors
on each transcript exactly when their punctured Hamming distance is at most
`2t`.  Since puncturing `s` coordinates lowers distance by at most `s`, every
allowed erasure pattern is uniquely decodable exactly when the original code
has distance at least `2t+s+1`.

A nonzero codeword has support of size at most `2t+s` exactly when deleting
that support makes the selected feature rows lose rank.  This gives the
deletion-rank equivalence.  The Singleton bound gives
`|Q| >= r+2t+s`; MDS feature geometry has distance `|Q|-r+1` and attains
equality.

Necessity is constructive.  At one query below the bound, choose a nonzero
minimum-weight codeword, erase `s` support coordinates, and split the remaining
support into two sets of size at most `t`.  Corrupt the zero table on the first
set and the alternative table on the second.  The visible transcripts are
identical although the exact robust values differ.

## Exact evidence

| Gate | Result |
|---|---:|
| Opened Vandermonde cases | 120 / 120 |
| Prospective Cauchy holdouts | 30 / 30 |
| Constructive robust-value lower bounds | 60 / 60 |
| Independent reconstructions | 150 / 150 |
| Independent lower bounds | 60 / 60 |
| Error-only false acceptances | 60 / 60 attacks |
| Queries saved vs treating erasures as errors | 187 total |
| Independent production imports | 0 |

Every decoded table reproduced the exact two-action robust value and policy.
The primary evidence digest is
`763360d9b6d679fc7ae0c67e1bd1632efb328531910e6ce959288ce6c3f67be3`;
the independent audit digest is
`85eec1ddc154c90cfd61c2fcb466ffd80d5a89c02ffc5c7cd2ee8ab1a91d8e09`.

## Strongest controls and falsification

- **Ignore erasures:** the `2t+1` distance criterion false-accepted all 60
  controls.  One known erasure removes enough redundancy to make two payoff
  tables observationally identical under the remaining error budget.
- **Treat erasures as errors:** safe but unnecessarily spends one extra query
  for every known erasure on MDS geometry.  The exact decoder saved 187 calls
  over the 150 reconstruction cases with no value or policy loss.
- **Repeated-basis voting:** requires `r(2t+s+1)` calls and assumes repeated
  calls expose independent evidence.  The feature-code selector works over
  distinct scenarios and computes the actual geometry certificate.
- **Universal Singleton count:** falsified by rank-two repeated-row geometry.
  Four copies of each coordinate direction need eight queries for `t=s=1`,
  not the lower bound five.  Seven available rows are rejected before any
  oracle call.

## Direct project consequence

THEORICA can now separate unavailable scientific measurements from adversarial
or incorrect measurements.  Missing responses are recorded as erasures, not
silently charged as errors or coerced into values.  The selector certifies the
joint budget before querying; the decoder reports erased and corrected scenario
indices separately; and insufficient feature geometry fails closed before
touching the oracle.

## Reproducibility

- Frozen protocol: `docs/ERROR_ERASURE_FEATURE_QUERY_PROTOCOL.md`
- Production implementation:
  `src/theorica/agents/corruption_resilient_features.py`
- Primary checker: `scripts/verify_error_erasure_feature_queries.py`
- Independent checker: `scripts/audit_error_erasure_feature_queries.py`
- Raw evidence: `results/error_erasure_feature_queries/`
- Hosted gate: `.github/workflows/additive-product-minimax.yml`

## Priority and limitations

Error-and-erasure unique decoding, the Singleton bound, and MDS codes are
classical.  The earlier branch audit cites Reed--Solomon and
characteristic-zero coding references; this result makes no historical-first
claim for the inequality or its rank characterization.

The result assumes a known exact rational feature map, certified exact
feature-span membership, explicit erasure locations, and correct hard budgets
`t` and `s`.  It does not cover silent timeouts misreported as values, errors
beyond budget, approximate features, stochastic noise, floating-point
conditioning, adaptive corruption of feature metadata, or optimal subset
search beyond the configured combinatorial cap.  Large-family downstream
validation remains limited to exact two-action robust games.
