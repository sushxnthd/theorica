# Frozen protocol: symmetric-slice convex-hull certificate

Date frozen: 2026-10-28

## Question

For the binary depth-three, four-copy, one-substitution, one-erasure
middle-first game, does the unresolved three-dimensional convex-hull mechanism
become an exact scalar theorem after identifying root and middle query costs?

Set `a=b=x` and `c=y`.  Project every exposure vector
`(r,m,l)` to `(r+m,l)`.

## Prospective theorem

The exact middle-first value on the symmetric slice is predicted to be

```text
S(x,y) = max(7x+y, 6x+3y, 5x+4y).
```

Equivalently, the active face is:

- `(7,1)` when `x >= 2y`;
- `(6,3)` when `y <= x <= 2y`;
- `(5,4)` when `x <= y`.

The key prediction is that the projected componentwise adversary recursion
contains `(7,1)`, even though its three-dimensional lift `(3,4,1)` is not
componentwise unavoidable.  This would turn the observed tradeoff between
`(2,5,1)` and `(4,3,1)` into a theorem for an unseen infinite algebraic
family rather than a single numerical witness.

## Decisive experiment

1. Re-run the exact finite-state guarantee recursion after mapping both root
   and middle queries to the first projected coordinate.
2. Require the maximal projected guarantee antichain to contain all three
   predicted faces `(7,1)`, `(6,3)`, and `(5,4)`.
3. Synthesize exact optimal middle-first policies at one interior integer
   point per cone and enumerate every terminal exposure.
4. Verify each policy's projected exposures against both extreme rays of its
   cone, which proves the corresponding affine upper bound throughout that
   cone.
5. Check boundary ties at `x=y` and `x=2y`, plus frozen unseen integer
   points spanning every cone.
6. Reproduce the lower antichain and all upper-cone inequalities in a
   standard-library-only auditor importing zero THEORICA modules.

## Frozen holdouts

The exact solver must not be run on these until this file is committed:

```text
(79,1), (81,40), (41,40), (40,41), (1,79), (2,1), (1,1)
```

Each pair is `(x,y)`; the corresponding three-level costs are `(x,x,y)`.

## Acceptance

The theorem passes only if:

- all three projected lower faces are exact adversarial guarantees;
- all cone policies satisfy every extreme-ray inequality;
- all seven holdouts equal `S(x,y)`;
- both boundary ties match exactly;
- the independent audit agrees and imports zero THEORICA modules;
- artifacts reproduce byte-for-byte;
- the full regression suite and scoped Ruff checks pass.

Any missing projected face, violated extreme ray, or holdout mismatch is a
falsification and must be preserved.  A timeout is not a proof.

## Claim boundary

Passing proves exactness only for positive integer costs with `a=b` in the
binary middle-first conditioned class.  It does not prove the full
three-dimensional six-face law, unrestricted root dominance, q-ary
generalization, or leaf-first exactness.
