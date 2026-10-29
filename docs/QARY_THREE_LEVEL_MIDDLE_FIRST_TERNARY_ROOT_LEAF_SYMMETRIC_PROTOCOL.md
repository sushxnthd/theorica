# Frozen protocol: ternary equal-root-leaf-cost law

## Question

For ternary depth-three prefixes with root and leaf query cost `x` and middle
query cost `y`, determine the exact worst-case middle-first cost under four
physical copies, one adversarial substitution, and one recognized erasure.

## Prospective claim

The embedded binary lower envelope specializes to

```text
T_3(x,y,x) = max(2x+5y, 5x+4y, 6x+3y).
```

The predicted phase boundaries are `y=3x` and `y=x`.

## Preserved parent failure

Projecting the frozen ternary unit-cost policy from exposure `(r,m,l)` to
`(r+l,m)` fails the shared boundary ray `(x,y)=(1,3)`: policy cost **18**
exceeds the candidate face value **17**. Thus neither previous one-policy
slice proof applies. This negative result must remain in the evidence.

## Decisive experiment

Synthesize policies directly against both extreme-ray budgets for each cone:

| Face | Cone rays | Budgets |
|---|---|---|
| `(2,5)` | `(0,1)`, `(1,3)` | `5`, `17` |
| `(5,4)` | `(1,1)`, `(1,3)` | `9`, `17` |
| `(6,3)` | `(1,0)`, `(1,1)` | `6`, `9` |

Each certificate must be one adaptive ternary policy satisfying both rays of
its cone. Separate scalar-optimal policies at the two rays do not count.
Infeasibility of either of the first two cones falsifies the proposed
three-face proof route and must be retained.

## Prospective holdouts

After, and only after, cone synthesis, solve exact scalar instances at:

```text
(x,y) = (79,1), (41,40), (1,1), (40,41), (2,3), (1,3),
        (40,121), (1,79), (5,7), (11,3), (13,17), (29,11).
```

## Independent audit

A zero-production-import implementation must reconstruct the ternary query
rows, replay every terminal exposure against all six ray budgets, re-evaluate
all holdout formulas, and independently verify the exact depth-eight/depth-nine
unit-cost boundary. Artifacts must regenerate byte-for-byte.

## Claim boundary

Success proves only arity three, depth three, costs `(x,y,x)` for positive
integer `x,y`, four copies, one substitution, one recognized erasure, and a
middle-first initial action. It does not prove arbitrary ternary cost triples,
unrestricted first actions, higher arity, deeper trees, or other fault models.
