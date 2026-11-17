# Exact all-positive-cost middle-first planning

## Theorem

For every positive integer root, middle, and leaf query cost `(a,b,c)`, the
exact worst-case cost in the binary, four-copy, one-substitution, one-erasure
class conditioned on a middle-level first query is

```text
max(
  a + 5b + c,
  2a + 3b + 4c,
  2a + 4b + 3c,
  3a + 3b + 3c,
  3a + 4b + c,
  4a + 2b + c
).
```

The earlier exact affine adversary recursion proves the lower bound. The upper
bound is now supplied by a finite policy fan.

## Upper mechanism

Five face-active cones admit one adaptive policy each. The exceptional face
`(3,4,1)` has five extreme rays and no single common policy. Its cone is
partitioned into six simplicial cells:

- two outer cells use the original wing rays;
- four central cells share `(2,2,1)` and partition the zero-leaf edge at
  ancestor-cost ratios `1/2, 2/3, 1, 3/2, 2`.

Each cell has one exact adaptive tree whose every terminal exposure satisfies
the face budget on all three generating rays. Linearity extends each bound to
the full cell. Exact normalized cross-section areas give

```text
exceptional cone area = fan area = 11/105,
```

and the boundary rays occur in strict ratio order, certifying coverage without
a positive-cost gap.

## Evidence

| Check | Result |
|---|---:|
| Single-policy face cones | 5/5 |
| Exceptional-face fan cells | 6/6 |
| Terminal transcripts replayed | 4,508 |
| Prospective exact cost triples | 18/18 |
| Independent exposure replays | 11/11 |
| Independent coverage area | 11/105 |
| Production imports in audit | 0 |

The artifacts reproduce byte-for-byte. The executable
`certify_binary_middle_first_all_costs(a,b,c)` returns the six exact face
values, optimum, and active phases while failing closed on nonpositive or
nonintegral inputs.

## Preserved negative result

No single policy covers all five exceptional rays, and only 2/10 triples of
the original extreme rays admit a common policy. The internal boundary rays
are necessary. This negative result remains part of the proof, rather than
being overwritten by the successful fan.

## Scope

The theorem is conditioned on binary arity, depth three, four physical copies
per query, one substitution, one erasure, and a middle-level first action. It
does not cover unrestricted first actions, higher arity, deeper trees, other
fault budgets, or establish external literature novelty.
