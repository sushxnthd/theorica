# Exact rational-ratio middle-first theorem

## Theorem

For positive integers `p,q,u,y` with `p >= 2q`, binary middle-first planning
has exact worst-case cost

```text
R_{p/q}(u,y) = max((4p+2q)u+y, (3p+3q)u+3y, (2p+3q)u+4y)
```

at level costs `(pu,qu,y)`, and

```text
M_{p/q}(u,y) = max((5p+q)u+y, (4p+2q)u+3y, (3p+2q)u+4y)
```

at level costs `(qu,pu,y)`. The phase boundaries are `2y=(p-q)u` and
`y=pu`.

## Continuous lower certificate

The exact projected adversary recursion was instrumented at every branch
comparison. Its only realized structural transitions above ratio two occur at
ratios two, three, and four. Exact traces at those boundaries and inside the
three open cells returned the same three source triples in both orientations.
Every affine comparison root was reconstructed, with zero roots inside a
certified open cell or above four in the tail. This proves the lower envelope
for every real ratio at least two, not only the sampled rationals.

## Upper certificate and prospective evidence

The six cone-uniform policies from the integer theorem have affine margins in
the ratio, nonnegative value at two, and nonnegative slope. They therefore
remain feasible for every real ratio at least two. All 48 frozen exact minimax
problems at ratios `13/6, 7/3, 5/2, 7/2, 9/2, 17/3` matched the theorem,
including both phase boundaries and extreme cost regimes.

The independent audit imports zero THEORICA modules, reconstructs all trace
roots, rechecks all six policy certificates, and independently solves all 48
holdouts.

## Executable consequence

`certify_binary_middle_first_rational_ratio(...)` returns the exact optimum,
active phase, projected faces, and integer level costs for any encoded rational
ratio in the proved domain. Invalid ratios and costs fail closed.

## Limitations

The theorem remains limited to the binary, four-copy, one-substitution,
one-erasure, middle-first conditioned class. It does not prove ratios below
two, unrestricted first actions, higher arity, or leaf-first exactness.
