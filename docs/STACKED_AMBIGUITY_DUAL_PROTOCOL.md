# Stacked ambiguity dual protocol

Status: frozen before implementation.

## Question

Can THEORICA turn the scalar stacked ambiguity gap into a sparse, weighted,
independently replayable adversarial certificate rather than only a subset of
incompatible scenario constraints?

## Prediction

Let all feasible completion games share `a` actions and exact robust value `v`.
Stack their labelled scenario columns into payoff matrix `U`, with exact maximin
value `v_stack` and gap `Delta = v - v_stack`.

The minimax dual predicts a probability vector `q` over labelled scenarios such
that

`max_i sum_j q_j U[i,j] = v_stack = v - Delta`.

An optimal `q` exists with support at most `a`. Thus the same certificate upper
bounds every pure action, and therefore every randomized policy, at the exact
ambiguity-degraded value. Zero gap should return matching primal and dual exact
values; positive gap should justify abstention quantitatively.

## Frozen boundary sweep

- Reuse the opened affine and prospective reciprocal-feature zero-gap families.
- Reuse three-, four-, and five-action sharp face attacks.
- Add an untouched six-action sharp family; predict uniform dual mass `1/6`,
  exact stacked value `-1/6`, gap `1/6`, and support six.
- Add asymmetric rational games with more scenarios than actions; predict exact
  primal-dual equality and dual support no greater than the action count.
- Preserve unequal-value abstention as an earlier failure mode.

## Strong controls

- Compare the weighted certificate with the existing unweighted Helly witness.
- Replay every dual mixture directly against every action using `Fraction`.
- Independently solve the column player's exact game without importing
  THEORICA production code.
- Require deterministic byte-identical evidence.

## Publishable threshold

- Exact primal-dual equality in every case.
- Every returned dual support is at most `a`.
- All sharp families attain support exactly `a`, including untouched six-action
  cases.
- The weighted mixture's maximum action payoff equals `v - Delta` exactly.
- Full regression and independent checker pass.

## Smallest claim and limits

Finite minimax duality and sparse equilibrium support are classical. The bounded
claim is an executable dual ambiguity certificate for THEORICA's corrupted
algebraic version space. It covers finite exact rational games only.

## Kill condition

Kill the extension if any exact game lacks primal-dual equality, if an optimal
dual certificate requires support greater than `a`, or if the certificate does
not change the abstention explanation beyond the existing subset witness.
