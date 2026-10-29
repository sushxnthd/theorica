# Frozen protocol: exact all-positive-cost middle-first planning

Status: frozen before policy synthesis and prospective evaluation.

## Question

Does the six-face adversarial lower envelope already proved for binary,
four-copy, one-substitution, one-erasure planning conditioned on a middle-level
first query admit matching policies for every positive root, middle, and leaf
query cost?

## Predicted theorem

For every positive integer cost triple `(a,b,c)`, the exact worst-case cost is

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

The prior exact adversary recursion supplies the lower bound. For the upper
bound, each face defines a closed homogeneous polyhedral cone where it is
maximal. Enumerate that cone's primitive extreme rays exactly. Synthesize one
adaptive decision tree whose every transcript fits the face budget at every
extreme ray. Linearity then bounds that tree by the face throughout the cone.
The six face cones must cover the positive orthant.

## Frozen experiment

- Enumerate extreme rays from pairs of active face and nonnegativity
  constraints; reject any ray failing a cone inequality.
- Use an exact multi-budget backward search, with one remaining budget per
  extreme ray, to synthesize one common policy per face.
- Replay every terminal transcript and retain its three-level exposure vector.
- Test twelve untouched positive cost triples spanning asymmetric ancestor
  costs and cheap, interior, and expensive leaf regimes against the exact
  production planner.
- Independently enumerate the cones and replay all terminal exposure vectors
  using only the Python standard library and serialized evidence.
- Reproduce evidence byte-for-byte.

## Strong baselines

- The proved universal six-face adversarial lower bound.
- Exact scalar planning at each prospective triple.
- The earlier ratio-at-least-two phase-boundary policy construction.
- Per-point scalar-optimal trees, which are insufficient as cone-uniform
  certificates unless their full transcript exposure set passes every ray.

## Publishable and kill boundary

Publish only if all six cone policies exist, every terminal exposure satisfies
every ray budget, the cone union covers all positive costs, all prospective
exact optima match, and a zero-import audit reproduces the result. Preserve a
failed face, ray, or prospective triple as falsification and reformulate the
kernel; do not weaken the protocol.

The claim remains conditioned on the binary four-copy middle-first class. It
does not cover unrestricted first actions, higher arity, deeper trees, other
fault budgets, or novelty relative to external literature.
