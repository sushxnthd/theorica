# All-positive-cost upper route: exact falsification

## Result

The universal six-face adversarial lower boundary remains exact on every
prospective scalar instance tested, but it cannot be proved by assigning one
cone-uniform adaptive policy to each active face.

Five faces admit such a policy. The face `(3,4,1)` does not.

## Exact obstruction

The active cone of `(3,4,1)` has five primitive extreme rays:

```text
(1,2,0), (2,1,0), (2,2,1), (2,4,1), (4,2,1).
```

An exact multi-budget backward search visited 3,719 states and found no
middle-first decision tree whose every transcript fits the `(3,4,1)` budget
at all five rays. A standard-library-only implementation independently
reproduced the same infeasibility and state count without importing THEORICA.

The simpler repair—triangulating the five-ray cone and using one policy per
three-ray cell—also fails. Only 2 of the 10 three-ray subsets admit a common
policy, so those cells cannot cover the face cone.

## Controls and evidence

| Check | Result |
|---|---:|
| Full face policies feasible | 5/6 |
| Extreme rays independently reproduced | 6/6 faces |
| Feasible policy exposure replays | 5/5 |
| Problem-face exact search states | 3,719 |
| Three-ray subsets feasible | 2/10 |
| Prospective scalar exact optima | 12/12 |
| Independent production imports | 0 |

The five successful policies contain 2,054 terminal transcripts in total.
Every serialized terminal exposure satisfies every extreme-ray budget of its
face. The twelve frozen positive cost triples include asymmetric ancestor
costs and cheap, interior, and expensive leaves; all match the six-face value.

## Consequence

This falsifies the one-policy-per-face and naïve three-ray-triangulation proof
architectures, not the six-face value formula. The next viable upper proof
must synthesize a finer policy fan whose internal rays are induced by policy
exposure inequalities, or derive a set-valued dynamic certificate directly.

The claim remains bounded to the binary, four-copy, one-substitution,
one-erasure class conditioned on a middle-level first query. No unrestricted
first-action, higher-arity, deeper-tree, deployment, or external-novelty claim
is made.
