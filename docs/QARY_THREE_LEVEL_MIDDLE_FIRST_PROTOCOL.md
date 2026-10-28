# Frozen protocol: middle-first conditioned six-face law

Status: frozen before opening any exact solve below.

## Candidate law

Exploratory exact searches on the opened `{1,...,4}^3` grid and the preceding
twelve ancestor-bypass rays suggest that the exact binary cost conditioned on
a middle-level first query is

```text
M(a,b,c) = max(
    a + 5b + c,
    2a + 3b + 4c,
    2a + 4b + 3c,
    3a + 3b + 3c,
    3a + 4b + c,
    4a + 2b + c,
).
```

This is a candidate inferred from opened evidence, not a theorem. The frozen
experiment tests whether it extrapolates to unseen high-ratio rays and narrow
phase boundaries.

## Frozen holdouts

The first six uniquely activate the six proposed faces at 79:1 scale:

```text
(1,79,1)  (1,1,79)  (1,79,53)
(79,1,53) (79,79,1) (79,1,1)
```

The next six have a predicted winning margin of exactly one:

```text
(59,30,1) (59,29,1) (59,1,58)
(58,1,59) (29,59,1) (1,59,58)
```

All triples are primitive and outside every grid used to infer the candidate.

## Acceptance criteria

1. Exact production middle-first optima equal the frozen candidate on 12/12.
2. Each of the six coefficient faces is uniquely active on its designated
   79:1 holdout.
3. All six one-margin cases retain their predicted active face and cost.
4. A standard-library-only conditioned solver reproduces all twelve optima
   with zero THEORICA imports.
5. The accepted law is exposed as an executable certificate with explicit
   `binary_middle_first` scope; invalid costs fail closed.
6. Full tests, Ruff, deterministic reruns, diff checks, and hosted workflows
   pass.

## Kill criteria

- any exact conditioned optimum differs from the six-face prediction;
- a purported unique face ties on a frozen holdout;
- the independent solver disagrees; or
- the implementation presents this conditioned binary law as unrestricted or
  q-ary exactness.

## Claim boundary

Passing gives prospective exact support for a finite middle-first max-plus
law. It does not prove that law for every positive cost triple, solve the
non-convex leaf-first profile, prove unrestricted six-face exactness, or
establish larger-arity, greater-depth, or different-fault-budget results.
