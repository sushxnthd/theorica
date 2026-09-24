# Axiom-to-Coordinate Discovery

**Frozen reproducibility result — 24 September 2026**

## Research question

Can an autonomous scientist begin with only experimental access to an unknown
binary composition law, discover structural axioms from interventions, infer
that a latent coordinate should exist, learn that coordinate without being
given its functional form, and compress it back into an interpretable symbolic
law?

THEORICA's axiom-to-coordinate branch tests exactly that chain.

## Method

The scientist receives an oracle `F(x,y)` and an allowed experimental domain.
It is not given the formula for `F`, the simplifying coordinate, or a menu of
answers such as log, atanh, reciprocal, or power transforms.

1. **Experimental axiom tests.** Probe commutativity and associativity using
   fresh oracle calls.
2. **Representation switch.** If the observed operation passes the frozen
   structural tests, search for a scalar coordinate `g` satisfying
   `g(F(x,y)) = g(x)+g(y)`.
3. **Nonparametric recovery.** Learn `g` as piecewise-linear knot values from
   the operation triples. Only one anchor is imposed to remove the unavoidable
   multiplicative-scale ambiguity.
4. **Symbolic compression.** Estimate `g'(x)`, fit a generic low-degree
   rational form `P(x)/Q(x)`, then integrate it symbolically. Named transforms
   are not supplied as target candidates.
5. **Out-of-sample prediction.** Predict new compositions through
   `F(x,y)=g^{-1}(g(x)+g(y))`.

The representation principle is classical. The research contribution being
tested here is the **automated experimental chain** from black-box probing to
axiom detection to representation choice to latent-coordinate recovery and
symbolic compression.

## Canonical rediscovery panel

The clean workflow rediscovered all five simplifying coordinates, up to the
usual additive/multiplicative equivalences:

| Black-box operation | Recovered derivative structure | Coordinate |
|---|---|---|
| multiplication `xy` | `1/x` | `log(x)` |
| relativistic velocity composition | `1/(1-x^2)` | rapidity / `atanh(x)` |
| probabilistic OR `x+y-xy` | `1/(1-x)` | `-log(1-x)` |
| harmonic/parallel composition `xy/(x+y)` | `1/x^2` up to sign | reciprocal coordinate |
| cubic norm composition `(x^3+y^3)^(1/3)` | `x^2` | cubic coordinate |

**5/5** canonical associative worlds passed the structural gate and **5/5**
symbolic coordinate shapes were recovered.

Three deliberately invalid controls were also tested. **3/3 were rejected** by
the axiom gate.

## Frozen hidden-world holdout

To test whether the system merely recognized familiar textbook operations, 50
unseen associative worlds were generated from hidden monotone coordinates whose
derivatives were random low-degree rational functions. THEORICA never received
the hidden rational coefficients or coordinate.

Each world used:

- seed panel **1000–1049**;
- **200** noisy operation measurements;
- output noise standard deviation equal to **0.1% of the experimental-domain span**;
- a generic rational derivative compressor with maximum degree 3;
- fresh out-of-sample operation pairs;
- a direct total-degree-6 bivariate polynomial fit as a non-structural baseline.

### Clean GitHub Actions result

| Metric | Result |
|---|---:|
| Hidden worlds satisfying frozen success gates | **50/50** |
| Median derivative-shape error | **0.001584** |
| 90th-percentile derivative-shape error | **0.004560** |
| Maximum derivative-shape error | **0.006254** |
| Median unseen operation error | **0.0003931** |
| 90th-percentile unseen operation error | **0.0005321** |
| Degree-6 polynomial median error | **0.0008314** |
| Latent-coordinate wins vs polynomial | **46/50** |

The clean workflow installed THEORICA from scratch, passed the targeted tests,
executed the full holdout, and uploaded the result artifact.

Workflow run:
https://github.com/sushxnthd/theorica/actions/runs/36039385226

## Why this is different from ordinary equation fitting

A direct symbolic or polynomial regressor asks for a surface
`z = h(x,y)`.

This branch first asks a different scientific question:

> **What algebraic structure does the experiment obey, and is there a coordinate
> in which that structure becomes simple?**

For the accepted worlds the learned coordinate converts nonlinear composition
into addition. This gives a reusable structural model and preserves
associativity through the representation rather than merely approximating the
observed surface.

## Claim boundary

The following claims are supported by the frozen result:

- THEORICA can experimentally detect the tested commutative/associative
  structure from black-box oracle calls.
- It can recover a latent additive coordinate without receiving a named
  transform as the answer.
- It can symbolically compress several familiar coordinates and generalize to
  50 unseen hidden-coordinate worlds.
- The structural representation outperformed a direct degree-6 polynomial
  baseline on 46/50 noisy hidden worlds.

The following claims are **not** established:

- that the underlying representation theorem is new;
- that no prior system has ever combined related ingredients;
- that the method handles arbitrary algebraic structures or higher-dimensional
  groups;
- that it is state of the art against every symbolic-regression or functional-
  network baseline;
- that the work is a certified field-first result;
- that it guarantees admission, publication, funding, or external recognition.

A targeted literature search found older functional-network work that learns
generators when associativity is already supplied, theorem-guided AI systems
that receive background axioms, and recent proposals for axiom evolution. We
have not yet found a prior system matching the full end-to-end experimental
chain above. That is a **plausible novelty hypothesis requiring broader expert
and literature validation**, not a settled novelty claim.
