# Representation-Closure Frozen Holdout Preregistration

Date frozen: 24 September 2026

## Frozen method

The representation-closure implementation is frozen at commit:

`f3c3c6cdd89f4edd6970e90a7da817a425c04b8c`

No method or gate changes are permitted after inspecting the holdout outcomes.
Any later scientific change creates a new campaign version.

Compatibility note: the first clean CI attempt failed before any holdout task ran because NumPy 2 removed `np.trapz`. Commit `8c181efa2039d32ecf1f80077dc097df7c35c2de` replaces only that call with the equivalent `np.trapezoid`; no algorithm, gate, seed, family, or benchmark logic changed.

Development used ordinary exponentials/oscillations and exploratory Airy,
Bessel, parabolic-cylinder, and Legendre examples. None of the four holdout
families below has been executed against this frozen implementation before this
preregistration.

## Question

Can one small, family-agnostic differential meta-grammar repair THEORICA's
explicit hypothesis language on mathematical families that were not named,
coded, or tuned during method development, while leaving already-expressible
laws in the simpler explicit representation?

The operator meta-grammar contains only terms of the form

[
x^k D^j[y], qquad j\le2,quad k\le2,
]

with at most four active terms. It contains no `hermite`, `laguerre`,
`hyp1f1`, or modified-Bessel primitive.

## Frozen out-of-language holdout

20 independent tasks from each family, seeds 10000-10019:

1. high-order Hermite functions, order 8-12;
2. high-order Laguerre functions, order 8-12;
3. confluent hypergeometric 1F1 functions with continuously sampled parameters;
4. modified Bessel I_nu functions with continuously sampled order and scale.

All tasks use 0.3% Gaussian measurement noise relative to the clean training
signal standard deviation and a fresh extrapolation sweep outside the training
range.

## In-language specificity controls

20 polynomial tasks of degree 2-5 and 20 fixed-frequency trigonometric mixtures,
seeds 11000-11019.

These controls test whether representation closure fires unnecessarily when the
existing symbolic grammar is already adequate.

## Comparators

1. current THEORICA bounded compositional symbolic synthesis with trial width
   increased to 200;
2. degree-selected polynomial regression, degrees 1-12, selected only from
   training-edge validation;
3. the falsification-gated representation-closure scientist.

## Frozen gate

The operator representation is adopted only when:

- operator edge-validation NRMSE <= 0.08, and
- operator edge-validation NRMSE <= 0.50 times explicit symbolic
  edge-validation NRMSE.

Otherwise the explicit symbolic theory is retained.

## Primary success conditions

The campaign is considered positive only if all are satisfied:

1. representation closure beats current THEORICA on at least 60/80
   out-of-language paired tasks;
2. median out-of-language NRMSE for closure is <= 0.03;
3. at least 30/40 in-language controls remain in explicit mode;
4. median in-language closure NRMSE is no worse than 1.25 times current
   THEORICA's median error.

All failures and family-specific negative results are retained.
