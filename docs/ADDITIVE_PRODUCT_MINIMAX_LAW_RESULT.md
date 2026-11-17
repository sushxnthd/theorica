# Additive rectangular-product minimax law

## Smallest supported claim

For a finite robust game with joint actions `A = product_t A_t`, rectangular
ambiguity vertices `B = product_t B_t`, and additive payoff

`M(a,b) = sum_t M_t(a_t,b_t)`,

THEORICA may solve the component games independently. The joint maximin value
and best-pure value are respectively

`V = sum_t V_t` and `P = sum_t P_t`.

Consequently the joint game has strict randomized advantage exactly when at
least one component has strict randomized advantage. If an optimal component
policy has `s_t` positive atoms, the implemented common-mass coupling returns
an optimal joint policy with at most

`1 + sum_t (s_t - 1)`

positive joint actions. The implementation is exact over rational payoffs and
fails closed unless additivity and rectangularity are explicitly certified.

This is an executable decomposition/certificate law for THEORICA, not a claim
that finite minimax, separable optimization, or transportation-polytope
sparsity is new.

## Proof

Let `mu` be any joint action distribution and `mu_t` its component marginals.
For a joint ambiguity vertex `b`, linearity gives

`E_mu M(a,b) = sum_t E_{mu_t} M_t(a_t,b_t)`.

Because nature ranges over the full Cartesian product,

`min_b E_mu M(a,b) = sum_t min_{b_t} E_{mu_t} M_t(a_t,b_t)`.

Every tuple of component marginals admits a coupling (their independent
product is one), so maximizing over joint distributions is equivalent to
maximizing each summand independently. This proves `V = sum_t V_t`. For pure
joint actions the same separation proves `P = sum_t P_t`. Each component gain
`V_t-P_t` is nonnegative; their sum is positive exactly when one is positive.

For sparsity, order the positive atoms of every component policy. Emit the
tuple of current atoms with mass equal to the smallest remaining current mass,
subtract it, and advance every exhausted atom. The construction preserves all
marginals. Each nonfinal emission exhausts at least one of the
`sum_t(s_t-1)` nonfinal marginal atoms, proving the stated bound.

## Frozen validation

- Exhaustive: all `81^2 = 6,561` pairs of `2 x 2` component games over
  `{0,1,2}`.
- Result: all value, best-pure, strictness, marginal, realized-payoff, and
  support checks passed; 2,072 pairs had strict advantage; maximum realized
  joint support was 3.
- Mixed dimensions: three frozen `2 x 3` / `3 x 2` pairs passed.
- Prospective holdout: 24 three-factor games generated from seed `20261025`
  passed without changing the protocol or implementation.
- Independent checker: standard-library rational arithmetic only, no import
  from the production solver; exactly reproduced 6,561 passes, 2,072 strict
  pairs, and maximum support 3.
- Production tests: exact values, exponential representation reduction, and
  fail-closed structural gates pass.

Artifacts are in `results/additive_product_minimax/`. Reproduce with:

```bash
PYTHONPATH=src python scripts/verify_additive_product_minimax.py
PYTHONPATH=src python scripts/audit_additive_product_minimax.py
PYTHONPATH=src python -m pytest -q
```

## Sharp assumption boundaries

- Removing rectangularity breaks the sum law. Two crossing components each
  have value 1, hence rectangular value 2. Restricting nature to only joint
  vertex `(0,0)` raises the actual value to 4.
- Removing additivity breaks the sum law. Two zero component games predict 0;
  adding the parity-matching cross term yields a uniform-policy lower bound
  `1/2`.
- The executable fast path currently accepts a component only when it has two
  actions or two ambiguity vertices, matching THEORICA's independently
  certified exact component solvers. The theorem itself is not limited to
  those sizes.

## Priority audit and novelty boundary

The mathematical ingredients are classical. Altschuler and Boix-Adserà define
the multi-marginal coupling polytope and explicitly call its sparse optimum a
folklore LP fact, proving a support bound of `nk-k+1` for equal marginal sizes:
https://doi.org/10.1007/s10107-022-01868-7. De Loera and Kim survey the much
older transportation-polytope literature:
https://arxiv.org/abs/1307.0124. Stein, Ozdaglar, and Parrilo study finitely
supported equilibria in separable games:
https://arxiv.org/abs/0707.3462.

The defensible contribution here is narrower: the exact robust-game
factorization, strict-advantage routing rule, constructive rational coupling,
fail-closed API, frozen assumption counterexamples, and independently checked
THEORICA implementation. Do not describe the general mathematical ingredients
as a new theorem.

## Project consequence

Certified additive rectangular products no longer need expanded enumeration of
`product_t |A_t|` actions against `product_t |B_t|` ambiguity vertices.
THEORICA can solve the factors, couple the resulting policies, and return a
small exact certificate. Uncertified products remain on the general path.
