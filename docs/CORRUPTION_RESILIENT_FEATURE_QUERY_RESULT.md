# Corruption-resilient feature queries: exact result

## Smallest supported claim

Let `Phi` be a known rational scenario-feature matrix of row rank `r`, and
suppose every payoff component is certified to lie in its column span. If at
most `t` queried scenario responses can be adversarially corrupted, a queried
row set `Q` permits exact reconstruction of every payoff table if and only if
the linear evaluation code

`C_Q = {Phi_Q beta : beta in Q^p}`

has minimum Hamming distance at least `2t + 1`. Equivalently, every deletion of
`2t` rows from `Phi_Q` leaves rank `r`. Thus the exact optimal query count is
the smallest cardinality of a row subset with that property. Distinct-point
Vandermonde families attain the tight count `r + 2t`; general feature geometry
can require more queries or make correction impossible.

This characterization is classical linear error-correcting-code theory. The
THEORICA contribution in this branch is the executable, outcome-independent
row selector and exact rational decoder, its fail-closed integration into the
robust-planning path, and prospective tests of the geometry-dependent boundary.

## Priority audit

The core result must not be presented as a new coding theorem. Reed and
Solomon's 1960 polynomial-evaluation construction already supplies the MDS
mechanism (DOI `10.1137/0108018`), and Singleton's 1964 bound supplies the
classical distance ceiling (DOI `10.1109/TIT.1964.1053661`). More directly for
this implementation's coefficient field, Sippel, Ott, Puchinger, and Bossert
study Reed--Solomon codes over characteristic-zero fields, including the
rationals (`arXiv:1901.06863`). The distance/deletion-rank equivalence is the
standard generator-matrix characterization of linear-code distance.

The audited project claim is narrower: THEORICA now converts those classical
facts into an exact scenario-selection certificate, decoder, constructive
impossibility witness, and robust-planning abstention rule for arbitrary known
rational feature geometry. No first-priority claim is made for that software
composition without a broader systems-literature audit.

## Proof

Restriction to `Q` maps a coefficient vector to a word in the `r`-dimensional
linear code `C_Q`. Two words can be confused after at most `t` errors each
exactly when their Hamming distance is at most `2t`. Therefore unique recovery
against every weight-`t` corruption is possible exactly when the minimum
nonzero codeword weight is at least `2t + 1`.

A nonzero codeword has zeros on a set `D` precisely when the rows indexed by
`D` fail to distinguish one nonzero coefficient direction. Hence a codeword
of weight at most `2t` exists exactly when deleting its support leaves rank
below `r`. This proves the deletion-rank equivalence.

The Singleton bound gives `|Q| >= r + 2t`. For distinct-point Vandermonde rows,
every `r` rows are independent, so the code is MDS with distance
`|Q| - r + 1`; equality is attained at `|Q| = r + 2t`.

The persisted lower-bound generator makes the necessity constructive: from a
weight-at-most-`2t` nonzero codeword it splits the support into two sets of at
most `t`, producing two different payoff tables and two valid corruption
patterns with the same observed transcript.

## Exact evidence

| Gate | Result |
|---|---:|
| Opened Vandermonde cases | 120 / 120 exact |
| Prospective holdout seeds | 30 / 30 exact |
| Constructive lower-bound witnesses | 60 / 60 |
| Independent reconstructions | 150 / 150 |
| Independent lower bounds | 60 / 60 |
| Rank-only false acceptances | 60 |
| Strict query savings vs repeated-basis majority | 150 cases |
| Independent production imports | 0 |

The production selector chose exactly `r + 2t` scenarios in every MDS case,
corrected the injected corruptions, reconstructed every component payoff, and
reproduced the exact two-action robust value and policy. The independent
checker reimplemented rank, distance, decoding, and robust-value enumeration
using only the Python standard library.

The geometry boundary was also exercised. For six rows consisting of three
copies of each coordinate vector in rank two with `t = 1`, the optimal query
count is six rather than the Singleton lower bound four. With only five such
rows, the production selector rejects before calling the oracle.

## Strongest controls and falsification

- **Rank-only interpolation:** falsely accepted all 60 adversarial controls;
  exactly `r` observations have no residual redundancy.
- **Repeated-basis majority:** uses `r(2t + 1)` calls and assumes repeated-call
  corruption semantics. The distinct-scenario selector uses `r + 2t` calls on
  MDS geometry.
- **Universal `r + 2t` rule:** falsified by repeated-row geometry. Production
  computes the distance certificate from features before outcomes and either
  selects a larger subset or abstains.
- **Necessity:** 60 indistinguishable-transcript pairs make recovery impossible
  whenever distance is at most `2t`.

## Direct project consequence

Certified feature-rank compression can now be used in an adversarial query
channel without silently converting corrupt observations into a complete but
wrong payoff table. The new path selects scenarios before observing outcomes,
returns the corrected query indices and distance certificate, and fails closed
if the feature geometry or search cap cannot certify correction.

## Reproducibility

- Primary checker: `scripts/verify_corruption_resilient_feature_queries.py`
- Independent checker: `scripts/audit_corruption_resilient_feature_queries.py`
- Primary results (gzip-compressed JSON):
  `results/corruption_resilient_feature_queries/primary.json.gz`
- Independent results:
  `results/corruption_resilient_feature_queries/independent_audit.json`
- Preserved failed scalability gate:
  `results/corruption_resilient_feature_queries/failed_full_hull_gate.json`

The first attempted downstream replay used the general full-hull solver and
did not finish within 120 seconds on large scenario counts. It was terminated
and preserved rather than hidden. The decisive downstream gate was replaced
by an exact two-action many-scenario solver, which tests the reconstruction-to-
planning consequence without conflating it with unrelated hull scalability.

## Limits

The result assumes a known exact rational feature map, certified exact span
membership, and a correct hard bound `t` on scenario-wise corruptions. It does
not address unknown or approximate features, stochastic noise, corruptions
beyond `t`, floating-point conditioning, or optimal subset search beyond the
configured candidate cap. The large-family downstream validation is limited
to exact two-action robust games. The mathematical characterization and MDS
boundary are classical; no priority claim is made for coding theory itself.
