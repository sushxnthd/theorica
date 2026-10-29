# Frozen protocol: rational-ratio middle-first law

## Question

Does the exact integer-ratio theorem extend from integer `k >= 2` to every
rational ancestor-cost ratio `rho = p/q >= 2`, or do noninteger comparison
crossings create new adversary faces or invalidate the cone-uniform policies?

## Candidate theorem

For positive integers `p,q,u,y` with `p >= 2q`, predict

```text
R_{p/q}(u,y) = max((4p+2q)u+y, (3p+3q)u+3y, (2p+3q)u+4y)
```

for level costs `(pu,qu,y)`, and

```text
M_{p/q}(u,y) = max((5p+q)u+y, (4p+2q)u+3y, (3p+2q)u+4y)
```

for level costs `(qu,pu,y)`. The predicted phase boundaries are
`2y=(p-q)u` and `y=pu`.

## Exact proof route

Instrument every affine comparison and equality used by the exact projected
adversary recursion. Query-copy bounds imply that each compared first
coordinate has form `rho*r+m`, so its sign can change only at a rational root.

Evaluate the recursion exactly at `rho = 2, 3, 4`, inside the two bounded open
cells at `5/2` and `7/2`, and in the unbounded tail at `5`. For each open cell,
require the trace to contain no comparison root in its interior. For the tail,
require no root above four. Matching the same three source triples throughout
then proves the lower certificate for every real `rho >= 2`, hence every
rational ratio.

Reuse the six frozen upper policies from the integer theorem. Their extreme-ray
margins are affine in `rho`, nonnegative at two, and have nonnegative slope;
the upper certificate therefore already covers every real `rho >= 2`.

## Frozen prospective suite

Open only after this protocol is committed:

- ratios `13/6, 7/3, 5/2, 7/2, 9/2, 17/3`;
- both root-heavy and middle-heavy orientations;
- four cost regimes per ratio: ancestor-heavy extreme, first phase boundary,
  second phase boundary, and leaf-heavy extreme;
- 48 exact minimax solves in total.

## Completion gate

- all 12 exact trace evaluations return the predicted three source triples;
- every bounded cell has zero interior comparison roots and the tail has zero
  roots above four;
- all six upper-policy cones retain their universal affine certificate;
- all 48 prospective rational holdouts match exactly;
- an independent zero-THEORICA-import audit recomputes all 48 exact optima and
  validates every recorded trace root and cell certificate;
- evidence is deterministic; full tests, lint, and hosted workflows pass;
- an executable rational-ratio certificate fails closed outside the theorem's
  domain.

Any new face, trace crossing inside a certified cell, holdout mismatch, or
independent disagreement falsifies the extension and is preserved.

## Scope

The target remains binary, depth three, four copies, one substitution, one
recognized erasure, and a required middle-level first query. It does not cover
ratios below two, irrational input encodings, unrestricted first actions,
higher arity, or leaf-first planning.
