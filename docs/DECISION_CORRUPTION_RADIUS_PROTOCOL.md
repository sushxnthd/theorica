# Frozen protocol: decision-quotient corruption radius

Status: frozen before implementation.

## Question

Given a finite algebraic completion list, a fixed nonadaptive family of
follow-up queries, and up to `t` adversarially corrupted query outcomes, when
does every possible received transcript still determine one exact robust
policy?

## Predicted theorem

Each completion `theta` has a query codeword `c(theta)`. For a received word
`y`, let

`L_t(y) = {theta : d_H(c(theta), y) <= t}`.

Let a completion subset be *incompatible* when its games do not share one
exact robust policy and value. Define its Hamming covering radius

`rho(W) = min_y max_{theta in W} d_H(c(theta), y)`

and define the decision corruption radius

`rho_dec = min_{W incompatible} rho(W)`.

Then the query schedule identifies a robust decision against every `t`-error
transcript exactly when `rho_dec > t`. If all completions already share a
decision, set `rho_dec = infinity`.

Proof prediction: a false decision certificate exists exactly when some
received word has an incompatible list. Such a word is a common radius-`t`
center of that incompatible set, giving both directions immediately.

For `a` actions it suffices to examine incompatible witnesses of size at most
`a`: unequal values have a two-completion witness, while equal-value policy
polytopes use the existing Helly bound. When incompatibility is genuinely
pairwise, the law reduces to the classical quotient-code boundary
`d_min >= 2t + 1`, since a pair has radius `ceil(d_H / 2)`.

## Frozen experiments

- Opened two-action binary-code families with 2--16 completions.
- Prospective untouched 32- and 64-completion coordinate families under one
  corrupted answer; tripled coordinates should have decision radius two.
- Decision-quotient families where many model completions share one policy;
  tripling only the decision bit should tolerate one error using three queries,
  versus 15 and 18 queries for unique recovery at dimensions five and six.
- Missing-repetition attacks should fail at the exact predicted radius.
- Higher-order three- through six-action face families where every pair is
  compatible but the complete family is not. Unit codewords should have radius
  one; tripled unit codewords should have radius three.
- Independent checker with no production imports.

## Strong baselines

- Unique-model minimum distance.
- Pairwise decision-conflict distance.
- No-error decision depth.
- Repetition-code construction.

## Publishable threshold

- Exact agreement with exhaustive received-word enumeration on all small
  families.
- Prospective radii two on 32/64 completion families and three on unseen
  five/six-action higher-order families.
- Zero pairwise conflict edges on the higher-order negative cases.
- A strict query saving over unique recovery.
- An executable selector returning either a certified error budget or a
  concrete received word plus incompatible completion witness.

## Novelty and kill boundary

Hamming error correction, covering radius, and Helly's theorem are classical.
The bounded contribution sought is their exact composition with THEORICA's
non-transitive common-policy predicate. Kill or reformulate if pairwise distance
is sufficient on every frozen family, if the radius law disagrees with
exhaustive received words, or if the selector cannot emit a replayable attack.
