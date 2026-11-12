# Exact corruption radius of the decision quotient

## Result

Let each feasible algebraic completion `theta` induce both an exact rational
robust game and a fixed follow-up-query codeword `c(theta)`. After at most `t`
adversarial answer substitutions, a received word `y` leaves the list

`L_t(y) = {theta : d_H(c(theta), y) <= t}`.

Call a completion subset incompatible when its games do not share one exact
robust policy and value. For such a subset `W`, define

`rho(W) = min_y max_{theta in W} d_H(c(theta), y)`.

The exact decision corruption radius is

`rho_dec = min_{W incompatible} rho(W)`.

The fixed query schedule identifies one robust decision after every transcript
with at most `t` corruptions if and only if

`rho_dec > t`.

If every completion already shares a decision, the radius is infinite. The
implementation returns the exact radius and maximum certified error budget. At
or beyond the boundary it returns a received word and labelled incompatible
completion witness that independently replay the failure.

## Proof

If a received word `y` has an incompatible radius-`t` list, no single robust
policy is valid for every completion consistent with the transcript, so safe
decision identification is impossible. Conversely, if identification fails
for some received word, its candidate list is an incompatible set with
covering radius at most `t`. Minimizing over incompatible sets proves both
directions.

For `a` actions, it is enough to examine witnesses of size at most `a`.
Unequal completion values have a two-completion witness. When values agree,
optimal-policy sets are convex subsets of the `(a-1)`-dimensional probability
simplex, so the existing Helly certificate supplies an incompatible subfamily
of size at most `a`.

For a two-completion witness, the radius is
`ceil(d_H(c(theta), c(phi)) / 2)`. Hence genuinely pairwise decision classes
recover the familiar `d_min >= 2t + 1` boundary. That reduction is not valid
for general multi-action decision compatibility.

## Frozen evidence

| Family | Exact result |
|---|---:|
| Opened binary codes, 2–16 completions | 15/15 |
| Prospective 32/64-completion codes | radius 2 in both |
| Missing-repetition attacks | 5/5 failed at radius 1 |
| Decision-quotient savings | 2/2 |
| Higher-order unit-code attacks, 3–6 actions | 4/4 radius 1 |
| Higher-order tripled codes, 3–6 actions | 4/4 radius 3 |
| Independent stdlib-only radius checks | 26/26 |

The dimension-five and dimension-six decision quotients tolerate one corrupted
answer with three queries. Unique-model recovery by tripled coordinate codes
uses 15 and 18 queries respectively, a total saving of 27 queries across the
two frozen cases.

The higher-order face family is the decisive falsification of the pairwise
baseline. Every pair of completion games shares an optimal policy, so the
pairwise decision-conflict graph has zero edges. Nevertheless the full
three- through six-completion family is incompatible. Unit codewords have a
common radius-one received word; tripling each coordinate raises the exact
radius to three. The selector returns the full higher-order witness and attack
word rather than incorrectly certifying from an empty conflict graph.

## Executable consequence

THEORICA can now validate a fixed follow-up measurement schedule before
execution. It either reports the exact number of adversarial answer errors the
decision quotient tolerates or abstains with a concrete transcript and bounded
incompatibility witness. Compatible model completions may deliberately share a
codeword, so the selector can spend queries on protecting the decision rather
than reconstructing scientifically irrelevant model distinctions.

## Reproduction

```bash
python scripts/verify_decision_corruption_radius.py
python scripts/audit_decision_corruption_radius.py
pytest -q tests/test_corruption_resilient_features.py
```

Deterministic primary and independent evidence is stored under
`results/decision_corruption_radius/`.

## Novelty boundary and limitations

Hamming error correction, covering radius, repetition codes, and Helly's
theorem are classical. The bounded contribution is their exact composition
with THEORICA's algebraic version space and non-transitive common-robust-policy
predicate, including higher-order attack certificates that pairwise quotient
distance cannot see.

The current selector covers finite enumerated completions, fixed nonadaptive
queries, exact finite outcome alphabets, substitutions with a known budget, and
exact rational games. Witness and center enumeration are exponential. Adaptive
queries with lies, erasures, stochastic noise, continuous completion spaces,
and approximate-policy tolerances require separate bounds and are not claimed.
