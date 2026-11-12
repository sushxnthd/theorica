# Frozen protocol: symbolic middle-first proof attempt

Status: frozen before symbolic state elimination.

## Target statement

For the binary depth-three prefix-query problem with four physical copies of
each query, one adversarial substitution, one recognized erasure, and positive
level costs `(a,b,c)`, require the first physical query to be at the middle
level. The target exact value is

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

## Symbolic proof obligations

The experiment must not establish the statement by sampling additional cost
triples. It must discharge both universal obligations over the nonnegative
cost cone, with strictly positive costs obtained by restriction.

1. **Lower bound.** An independent finite-state adversary recursion must show
   that every permitted decision tree has, for each of the six target vectors,
   a root-to-leaf transcript whose level-query count dominates that vector
   componentwise.
2. **Upper bound.** For every nonempty face-dominance cone, an exact feasible
   policy must be extracted. Every root-to-leaf exposure vector of that policy
   must cost no more than the active face throughout the entire cone.
3. **Cone certificate.** The upper implication must be checked exactly on all
   rational extreme rays of each three-dimensional polyhedral cone, not on a
   numeric grid.
4. **Independent audit.** A standard-library-only checker with zero THEORICA
   imports must replay the lower recursion, extreme rays, and policy-exposure
   inequalities from a machine-readable certificate.
5. Full tests, Ruff, deterministic reruns, diff checks, and exact-head hosted
   workflows must pass.

## Kill criteria

- any target face is absent from the exact adversary guarantee set;
- a face cone is nonempty but no feasible policy covers it;
- any policy exposure violates its active-face inequality on an extreme ray;
- rational and production checks disagree; or
- the certificate relies on a finite cost grid as a substitute for a cone
  proof.

If a kill criterion fires, preserve the smallest state, face, cone ray, or
policy exposure that falsifies the proof route and reformulate the kernel.

## Claim boundary

Passing proves the exact formula only for the binary, depth-three,
middle-first conditioned class with four copies, one substitution, and one
recognized erasure. It does not prove unrestricted root-first dominance,
solve leaf-first behavior, or extend to another arity, depth, fault budget, or
copy count.
