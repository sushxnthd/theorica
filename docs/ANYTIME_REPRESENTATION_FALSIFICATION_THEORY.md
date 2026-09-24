# Anytime-Valid Representation Falsification

## Scope

This note formalizes the statistical gate used in THEORICA campaign F003/F004.
The gate certifies evidence against a **frozen predictive theory**. It does not
prove that every member of the theory's originating grammar is false.

Let `F_{t-1}` denote all information available before challenge experiment
`t`. The experiment `x_t`, the frozen explicit prediction `f_t=f(x_t)`,
the frozen alternative prediction `g_t=g(x_t)`, sensor noise
`sigma_t > 0`, and adequacy tolerance `epsilon_t >= 0` must be predictable
from information available before observing `Y_t`.

The null is

[
H_0:quad |mathbb E[Y_tmid F_{t-1},x_t]-f_t|leepsilon_t
]

with conditional Gaussian measurement noise of known standard deviation
`sigma_t`.

## Proposition 1 — composite adequacy e-process

Let

[
q_t(y)=phi_{sigma_t}(y-g_t)
]

and define the null-envelope density value

[
m_t(y)=sup_{|mu-f_t|leepsilon_t}
       phi_{sigma_t}(y-mu).
]

Set

[
e_t=rac{q_t(Y_t)}{m_t(Y_t)},qquad
E_n=prod_{t=1}^n e_t.
]

Then under every conditional null mean satisfying the adequacy band,

[
mathbb E[e_tmid F_{t-1}]le1.
]

Therefore `E_n` is a nonnegative supermartingale and, by Ville's inequality,

[
Pr_{H_0}!left(sup_n E_ngerac1alphaight)lealpha.
]

### Proof

For the actual null mean `mu_t`, its Gaussian conditional density
`p_t(y)` is one member of the family over which `m_t(y)` takes a supremum.
Hence pointwise `p_t(y) <= m_t(y)`. Therefore

[
mathbb E[e_tmid F_{t-1}]
 =int p_t(y)rac{q_t(y)}{m_t(y)},dy
 leint q_t(y),dy=1.
]

Multiplication of predictable conditional e-values gives a nonnegative
supermartingale. Ville's inequality yields the stopping guarantee. QED.

For equal-variance Gaussians, the implemented log increment is

[
log e_t=
rac{d_t(Y_t)^2-(Y_t-g_t)^2}{2sigma_t^2},
]

where

[
d_t(y)=max(|y-f_t|-epsilon_t,0)
]

is the distance from `y` to the closest mean allowed by the null band.

## Proposition 2 — why disagreement is the falsification experiment

For the simple-null case `epsilon_t=0`, suppose the alternative prediction is
the true conditional mean:

[
Y_tmid F_{t-1},x_tsim
mathcal N(g_t,sigma_t^2).
]

Then

[
mathbb E_g[log e_tmid F_{t-1}]
 =rac{(f_t-g_t)^2}{2sigma_t^2}.
]

Thus, among a finite legal experiment pool with equal known noise, choosing the
point maximizing `|f(x)-g(x)|` maximizes expected one-step log evidence
against the frozen explicit theory.

### Proof

With `epsilon_t=0`, `e_t` is the likelihood ratio of
`N(g_t,sigma_t^2)` to `N(f_t,sigma_t^2)`. Its expected log under the
alternative is their KL divergence,

[
D_{KL}(mathcal N(g_t,sigma_t^2)|
       mathcal N(f_t,sigma_t^2))
=rac{(f_t-g_t)^2}{2sigma_t^2}.
]

QED.

## What the guarantee does and does not cover

The anytime-valid guarantee survives adaptive challenge-point selection and
data-dependent stopping **because each challenge action is chosen before its
outcome is observed**.

The guarantee assumes:

- the explicit and alternative predictive distributions used for scoring are
  frozen or otherwise predictable before each scored outcome;
- Gaussian measurement noise with the supplied `sigma_t`;
- the stated adequacy band is the null being tested;
- no challenge outcome is used retrospectively to construct the alternative
  that scores that same outcome.

F003/F004 supply the exact synthetic noise standard deviation, analogous to a
calibrated sensor specification. A physical deployment should instead use a
preregistered conservative noise bound or a separately calibrated sequential
noise model.

This machinery is established sequential-testing mathematics applied to
THEORICA's representation decision. The statistical theorem is not claimed as
new e-value theory.
