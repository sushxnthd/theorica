# Theory note: experimental axiom discovery and latent coordinates

## 1. Representation target

Suppose an unknown binary operation `F` on an interval admits a strictly
monotone coordinate `g` such that

```
g(F(x,y)) = g(x) + g(y).
```

Then

```
F(x,y) = g^{-1}(g(x)+g(y)).
```

Classical functional-equation results give conditions under which associative,
continuous, strictly monotone operations admit additive-generator
representations. THEORICA does not claim those representation theorems.

The autonomous-science problem is different: the scientist is not told in
advance that the observed black box is associative or that such a coordinate
should be used. It must obtain evidence for the structural premise through
experiments before invoking the representation.

## 2. Finite-basis identifiability certificate

Let a candidate coordinate be represented in a fixed basis

```
g_c(x) = c^T phi(x),
```

with `c in R^d`. For observed operation triples
`z_i = F(x_i,y_i)`, define

```
a_i^T = phi(z_i)^T - phi(x_i)^T - phi(y_i)^T
```

and stack these rows into `A`.

The additive-coordinate constraints are

```
A c = 0.
```

### Proposition

If `rank(A)=d-1`, then the coordinate coefficient vector is identified within
that basis up to a nonzero scalar multiple. One independent anchor, such as
`g(x_*)=1`, fixes the remaining scale.

### Proof

The rank-nullity theorem gives

```
dim null(A) = d-rank(A) = 1.
```

Therefore every nonzero solution of `Ac=0` lies on the same one-dimensional
subspace and differs only by a multiplicative constant. An anchor not
orthogonal to that null direction fixes the constant. □

If `rank(A) <= d-2`, the observations do not uniquely identify a coordinate
within the chosen basis; multiple linearly independent coordinates satisfy the
sampled constraints. This provides an explicit reason for the scientist to
collect additional experiments rather than report a unique law.

## 3. Noisy observations

With measurement error the constraints become approximate. A finite-basis
version can estimate `c` from the right singular vector associated with the
smallest singular value of `A`. The separation between the smallest and next
smallest singular values acts as an empirical identifiability diagnostic:
larger separation means the inferred one-dimensional null direction is less
sensitive to perturbations.

The current implementation uses a piecewise-linear coordinate and smoothness
regularization rather than exposing this finite-basis certificate as its main
estimator. The rank/spectral-gap criterion is therefore a theory-backed next
step for active experiment selection.

## 4. Scientific interpretation

Ordinary surface regression treats every triple `(x,y,z)` as an unrelated
sample of a bivariate function. A recovered additive coordinate asserts a
stronger invariant:

```
g(F(F(x,y),z))
 = g(x)+g(y)+g(z)
 = g(F(x,F(y,z))).
```

Thus associativity is encoded by construction after the representation is
learned.

This suggests an active-science loop:

1. probe algebraic identities;
2. reject identities that fail on fresh interventions;
3. select a representation theorem compatible with the surviving identities;
4. fit the representation;
5. inspect identifiability;
6. choose new experiments to reduce representation ambiguity;
7. compress the recovered representation into an interpretable symbolic law;
8. falsify it on held-out compositions.

## 5. Novelty boundary

The mathematics of additive generators for associative operations is
established. Functional-network methods have also used such representations
when the operation's associativity is provided as prior knowledge.

The research hypothesis for THEORICA is narrower and empirical:

> An autonomous experimental scientist can discover enough algebraic structure
> from black-box interventions to choose an appropriate representation class,
> recover its hidden coordinate, and turn that coordinate into a reusable
> symbolic law without being handed the governing equation or named transform.

The 24 September 2026 frozen result supports this hypothesis for one-dimensional
commutative associative operations. Broader algebraic families, stronger
baselines, and independent review are required before making a field-level
novelty claim.
