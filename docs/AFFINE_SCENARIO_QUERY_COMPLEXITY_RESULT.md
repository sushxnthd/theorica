# Optimal query complexity for certified affine scenario families

## Smallest supported claim

Let `m` ambiguity scenarios have known rational descriptors
`z_s in Q^d` that affinely span dimension `d`, where `1 <= d <= 3`.
Assume an external certificate establishes that every component-local action
payoff is affine in `z_s`, and that total payoff is additive across components.
Then THEORICA can reconstruct the complete local payoff table from exactly
`d + 1` scenario-oracle calls, independent of `m`, and pass that table to its
existing exact product-free robust planner.  In the worst case, no
deterministic exact algorithm can guarantee even the robust value with `d`
queries.

This is an optimal query law for the stated certified model, not a claim about
uncertified, noisy, or approximately low-rank games.

## Proof

Write one local payoff as

`f(z) = b + a_1 z_1 + ... + a_d z_d`.

The vector `(b,a_1,...,a_d)` has `d + 1` rational coordinates.  Because the
descriptors span affine dimension `d`, THEORICA can select `d + 1` scenarios
whose augmented rows `(1,z_s)` form a nonsingular square matrix.  Exact
rational interpolation recovers the coefficient vector for every local
action, hence every unqueried scenario payoff.  The downstream robust game is
therefore byte-for-byte the full-table game, so its value, policy,
randomization classification, and certificate are unchanged.

For necessity, run any deterministic algorithm for at most `d` queries on the
all-zero oracle.  The queried descriptors lie in a proper affine subspace.
There is a nonzero affine function `h` that vanishes on that entire transcript.
Choose its sign so `h` is negative at an unqueried descriptor.  A one-action
zero game and the one-action game `h` are indistinguishable to the algorithm,
but their exact robust values differ.  Thus `d` calls cannot guarantee the
value, while `d + 1` calls suffice.

## Frozen evidence

- 120/120 opened exact families reconstructed and planned identically.
- 30/30 prospective holdouts passed at 41, 64, 97, 127, and 193 scenarios.
- All oracle traces contained exactly `d + 1` distinct calls and no access to
  an unqueried scenario.
- 60/60 indistinguishable-transcript lower-bound witnesses had unequal robust
  values after only `d` queries.
- 39 evaluated families required strict randomization, preventing pure-policy
  coincidence from explaining the result.
- The independent standard-library checker passed all 150 reconstruction
  cases and all 60 lower-bound witnesses without importing production code.
- Primary evidence digest:
  `209053020c22deb9fe318485cc4e43b69ff5c473e8d0bee7697e43a1c1905104`.

## Strongest alternatives and falsification

Coordinate-extrema sampling is not a general substitute for an affine basis:
an extrema set can be affinely dependent and leave one coefficient
unidentified.  The lower-bound witnesses also rule out the stronger idea that
robust value alone always needs fewer observations than payoff reconstruction.
The 39 randomized cases rule out agreement caused only by a shared dominating
pure action.

## Executable consequence

`reconstruct_affine_scenario_payoffs` selects the lexicographically first exact
affine basis, makes only those oracle calls, reconstructs all local payoffs with
`Fraction` arithmetic, and records the queried indices.  It refuses missing
affinity certification, malformed oracle shapes, nonspanning descriptors, and
dimensions outside the certified range before downstream planning.

For a rank-three family with 193 scenarios, the payoff-query count is four
rather than 193.  The saving compounds with the existing scenario-polytope and
additive-product laws: payoff acquisition depends on descriptor dimension,
while planning depends on the retained hull and tie arrangement rather than on
the Cartesian joint-action count.

## Priority audit

The interpolation theorem is classical, not novel.  Neidinger, *Multivariate
Polynomial Interpolation in Newton Forms* (SIAM Review, 2019), explicitly
develops exact rational multivariate interpolation algorithms:
<https://epubs.siam.org/doi/10.1137/17M1124188>.  The standard derivative-free
optimization notion of a `d + 1` point set poised for linear interpolation is
also documented by Conn, Scheinberg, and Vicente, *Introduction to
Derivative-Free Optimization* (SIAM, 2009):
<https://epubs.siam.org/doi/book/10.1137/1.9780898718768>.

The defensible THEORICA contribution is the explicit optimal oracle law for
certified additive robust games, its adaptive indistinguishability boundary,
the exact query selector and reconstruction API, end-to-end policy replay on
unseen algebraic families, and fail-closed integration with the existing
rank-aware planner.  No broad novelty is claimed for affine interpolation or
dimension counting.

## Limitations

- Affinity is externally certified; `d + 1` samples cannot validate it on
  unqueried scenarios.
- Arithmetic and descriptors are exact rationals.  Noise requires a different
  statistical problem and invalidates the equality certificate.
- Production routing remains limited to descriptor dimension at most three
  and the existing downstream hull-size caps.
- The lower bound is worst-case deterministic exact query complexity.  It does
  not address approximation, distributional priors, or randomized error.
- The theorem does not apply to nonadditive payoffs or unknown descriptors.

## Reproduction

```bash
python scripts/verify_affine_scenario_query_complexity.py
python scripts/audit_affine_scenario_query_complexity.py
pytest -q tests/test_robust_provenance.py
```
