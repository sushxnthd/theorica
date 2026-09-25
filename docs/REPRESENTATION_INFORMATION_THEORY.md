# Representation-Information Experimental Design

## Scope

This note formalizes the acquisition rule used by THEORICA after it has
experimentally discovered an equational signature, verified the hypotheses of a
representation theorem, and selected a latent-coordinate model.

None of the ingredients below is claimed to make Bayesian/D-optimal
experimental design itself new. The research question is whether experimental
design should target uncertainty in a *discovered mathematical representation*
rather than uncertainty in the raw response surface.

## 1. Latent-coordinate constraints

For a verified representation family, THEORICA models a monotone coordinate

```
g_theta(x) = theta^T phi(x)
```

in a finite basis `phi`.

For an additive-generator operation,

```
g(F(x,y)) = g(x) + g(y),
```

and an observed experiment `z = F(x,y)` induces the linear constraint

```
a(x,y,z)^T theta = 0,
```

where

```
a(x,y,z) = phi(z) - phi(x) - phi(y).
```

For an equally weighted quasi-arithmetic mean,

```
g(F(x,y)) = (g(x)+g(y))/2,
```

so

```
a(x,y,z) = phi(z) - (phi(x)+phi(y))/2.
```

Gauge constraints remove the unavoidable affine or multiplicative
non-identifiability of the coordinate.

## 2. Identifiability

Let `A` stack the experimentally observed constraint rows.

### Proposition 1

Within a `d`-dimensional coordinate basis, if the gauge has removed the
trivial invariance and the resulting constrained design matrix has full
remaining rank, then the latent coordinate coefficients are locally
identifiable in that basis.

Equivalently, before gauge fixing, the additive-generator case has the desired
one-dimensional nullspace when

```
rank(A) = d - 1.
```

This is a direct rank-nullity result. A larger nullspace is experimental
evidence that the current measurements do not uniquely determine the
coordinate and therefore justifies additional experiments.

## 3. One-step information gain

Assume the current coefficient uncertainty is locally Gaussian,

```
theta | D ~ N(theta_hat, C),
```

and a new representation residual is observed with Gaussian variance
`sigma^2`:

```
r = a^T theta + epsilon,
epsilon ~ N(0, sigma^2).
```

Conditioned on a candidate row `a`, the posterior covariance is

```
C_new
= C - C a a^T C / (sigma^2 + a^T C a).
```

### Proposition 2

The one-step differential-entropy reduction about `theta` is

```
I(theta ; r | D, a)
= 1/2 log(1 + a^T C a / sigma^2).
```

Therefore, for fixed residual-noise variance, the myopically
information-optimal candidate is exactly

```
argmax_a a^T C a.
```

### Proof

For a Gaussian random vector, entropy differs from
`(1/2) log det C` only by a constant. The matrix determinant lemma applied to
the rank-one Bayesian covariance update gives

```
det(C) / det(C_new)
= 1 + a^T C a / sigma^2.
```

Taking one half of the logarithm yields the expression above. Since log is
strictly increasing, maximizing information gain is equivalent to maximizing
`a^T C a`. □

## 4. The plug-in experiment design used in THEORICA

Before an experiment, `z = F(x,y)` is not known, so its constraint row is not
known exactly. THEORICA uses its current coordinate model to predict

```
z_hat = g_hat^{-1}(c g_hat(x) + c g_hat(y))
```

and constructs the plug-in row

```
a_hat(x,y) = a(x,y,z_hat).
```

It then queries the candidate maximizing

```
a_hat^T C a_hat.
```

Thus the implemented rule is exactly information-optimal **conditional on the
local Gaussian approximation and the plug-in predicted row**. It is not
claimed to be globally Bayes-optimal for the nonlinear black-box problem.

## 5. Why this differs from output-space active learning

An output-regression acquisition function asks which input makes predictions of
`F(x,y)` most uncertain.

Representation-information design instead asks:

> Which experiment most reduces uncertainty about the coordinate in which the
> discovered algebraic law becomes simple?

Two queries can have similar output uncertainty while contributing very
different linear constraints on `theta`. Conversely, a query with an
apparently predictable raw output can be highly informative about a weakly
identified direction of the representation.

The frozen THEORICA benchmark therefore compares the representation-information
rule against:

1. the same latent-coordinate estimator with random experiments; and
2. an active degree-2-to-6 polynomial query-by-committee that selects inputs by
   raw output disagreement.

## 6. Theorem routing and falsification

The acquisition rule is used only after a separate structural stage.

THEORICA first enumerates a bounded term language over the unknown binary
operation and mines empirical identities. It then treats those identities as
*candidate premises*, not as sufficient proof of a representation theorem.

Current theorem gates include:

- additive-generator candidate:
  commutativity, associativity, and empirical strict monotonicity;
- quasi-arithmetic-mean candidate:
  symmetry/commutativity, reflexivity/idempotence, empirical strict
  monotonicity, and bisymmetry;
- commutative semilattice:
  associativity, commutativity, and idempotence.

The bisymmetry gate was added after constructing smooth, symmetric,
idempotent, monotone decoys that pass the shallow signature but are not
quasi-arithmetic means. A frozen adversarial panel now requires these decoys to
be rejected.

This separation is intentional:

```
empirical identities
    -> candidate theorem
    -> falsify theorem hypotheses
    -> representation
    -> representation-information experiments.
```

## 7. Relation to prior work

Several neighboring areas are established:

- Aczel-style representation theorems and Kolmogorov-Nagumo
  characterizations are classical mathematics.
- Functional Networks learn unknown generators when a functional-equation
  structure such as associativity is supplied.
- QuickSpec-style systems enumerate terms and discover equations by testing
  executable operations.
- Exact learning of equational theories has been studied with membership and
  equivalence queries.
- Bayesian and D-optimal experimental design, active symbolic regression,
  active latent-dynamics learning, and active representation learning are
  established fields.

The current THEORICA novelty hypothesis is therefore narrower:

> **experimentally mine an unknown continuous operation's equational
> signature; empirically verify the hypotheses of a compatible representation
> theorem; instantiate the theorem-induced latent coordinate; then choose new
> physical queries by information gain in that representation rather than in
> the raw output space.**

A literature search performed in September 2026 has not yet located this exact
end-to-end combination. Absence from a search is not proof of priority. The
claim should remain a methodological-novelty hypothesis until broader expert
review and independent replication.

## 8. Falsifiable next tests

A serious field-level claim should fail if any of these occur:

1. a close prior method is found that performs the same end-to-end pipeline;
2. theorem-gated routing collapses on adversarial near-law worlds;
3. representation-information design loses its data-efficiency advantage on
   untouched seeds or stronger active baselines;
4. the advantage disappears under realistic measurement noise;
5. the learned representation does not transfer to physical experiments.

These are research tests, not presentation details.
