# Exact provenance-weighted hidden-generator query frontier

Status: **EXACT SYSTEM/INTERFACE THEOREM — PASS**

Frozen protocol: `567255ce8cfcad6adecebffe15b9a36a633fefa5`

## Smallest supported claim

Let the hidden generator label `Z` of the certified hidden-cycle rack family
have a trusted prior distribution `pi` on `n` labels. With at most `q` cell
queries, where `0 <= q <= n-1`, the exact maximum Bayes probability of returning
the correct generator is

\[
\boxed{P^*(\pi,q)=\sum_{i=1}^{q+1}\pi_{(i)}},
\]

where `pi_(1) >= ... >= pi_(n)` are the ordered prior masses. Consequently the
least exact budget for target confidence `alpha` is

\[
\boxed{R_\alpha(\pi)=\min\left\{q:\sum_{i=1}^{q+1}\pi_{(i)}\ge\alpha\right\}}.
\]

The uniform case reduces to the earlier `(q+1)/n` law.

## Proof

Under the certified family promise, probing one fixed off-diagonal cell in row
`x` is an equality test for `Z=x`: identity is returned for every other label,
while the active complement cycle has no fixed point at that column.

Fix a deterministic policy of depth at most `q`. A positive observation names
the tested label and terminates. Along the unique all-negative path, the policy
can test at most `q` distinct labels and make one terminal guess. Therefore it
is correct on a set of at most `q+1` labels, whose prior mass is at most the sum
of the largest `q+1` masses. A randomized policy is a distribution over such
deterministic trees, so its Bayes success cannot exceed the same bound.

For attainability, select the `q+1` largest-mass labels, query any `q` of them,
and guess the remaining label after all negative observations. This succeeds
exactly when `Z` lies in that selected set, attaining the bound. Sorting queried
labels by descending mass also minimizes calls within the selected set; this
cost refinement is not needed for the success theorem.

## Exact evidence

| Gate | Result |
|---|---:|
| Positive integer prior vectors (`3 <= n <= 8`, weights `1..3`) | 9,828 |
| Exact frontier cases | 73,791 |
| Production planner/hidden-label executions | 560,925 |
| Exhaustive deterministic correct-label subsets | 2,005,668 |
| Exact confidence-budget inversions | 73,791 |
| Independent combinatorial checks | 2,079,459 |
| Focused runtime tests | 62/62 PASS |
| Scientific failures | **0** |
| Fresh byte-identical rerun | **PASS** |

Primary canonical SHA-256:
`6888a5a13553a81a843ec5eb3421cf17ac5f666179c3aa3900101449bf73a167`

Primary file SHA-256:
`9eba9d37b068d5a787805833d84899ebde76ad8f2df9e9eb5e3de1712a7a0ee0`

Independent canonical SHA-256:
`57fa0412913a26f03efbb596527aef5547dc50581b60bccc626cd6053ebeeb98`

Independent file SHA-256:
`c2ad799e6acd9ce7c402a367209a03672b21ce91297997c9ba7ce48b23d402f9`

The primary verifier exercises the production planner against every hidden
label. The independent audit imports no production planner and instead
enumerates every possible correct-label subset of size `q+1`.

## Prior-art and novelty boundary

The abstract result is a weighted finite search/equality-query fact and is not
presented as a new general Bayesian-search theorem. The rack-family reduction,
exact confidence contract, independently checked implementation, and enforced
trusted-provenance boundary are the defensible THEORICA result. Historical
field-level novelty is **not claimed**.

## SCIENCE ledger

- **TRUE:** adaptivity cannot beat the top-`q+1` prior mass for this certified
  family because all negative answers follow one path.
- **TRUE:** the uniform frontier is a special case, not a separate mechanism.
- **TRUE:** the exact confidence budget is obtained by cumulative sorted prior
  mass, with no asymptotics or calibration approximation.
- **FALSIFIED ALTERNATIVE:** posterior adaptation after negative probes can
  exceed the fixed top-mass frontier.
- **LIMITATION:** the theorem assumes both the hidden-cycle family promise and
  the provenance distribution are externally trusted. It does not certify or
  calibrate that prior from the same private oracle.

## CONSEQUENCE ledger

THEORICA now exposes `locate_hidden_generator_with_provenance`, which:

1. refuses to query unless both family and provenance certificates are present;
2. requires explicit bounded-error authorization below the pointwise `n-1`
   path;
3. queries the highest-mass labels and emits the exact achieved Bayes fraction;
4. records the query order and all-negative terminal guess; and
5. uses `provenance_weighted_query_budget` to invert an authorized confidence
   target exactly.

Without trusted provenance, THEORICA must retain the symmetric randomized
planner or the fail-closed zero-error verifier. The new mechanism therefore
changes query allocation without weakening the existing certificate boundary.

## Reproduction

```bash
python scripts/verify_provenance_weighted_query_frontier.py \
  --max-n 8 --max-weight 3 --output /tmp/primary.json
python scripts/audit_provenance_weighted_query_frontier.py \
  --max-n 8 --max-weight 3 --output /tmp/audit.json
python -m pytest -q tests/test_rack_seed_acquisition.py
```
