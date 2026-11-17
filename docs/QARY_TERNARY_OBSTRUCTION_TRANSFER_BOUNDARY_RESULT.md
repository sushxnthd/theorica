# Algebraic obstruction-pair transfer boundary

## Result

The prior prospective failure was caused by a missing symmetry-orbit closure,
not by a genuinely new policy requirement.  The level-coloured partition
hypergraphs for

- `P0={(2,0,0),(2,1,0)}`, and
- `P1={(2,0,0),(2,2,0)}`

are exactly isomorphic.  The verifier emits a complete vertex bijection and
checks every colour and incidence edge in both directions.  Transporting the
510-node exact `P0` policy through this bijection gives cost **51** on `P1`,
where the terminated family-local column method predicted 52.

The third obstruction `P2={(2,1,0),(2,2,0)}` is not in this orbit.  Joint
one-dimensional Weisfeiler--Leman refinement already gives different stable
colour multiplicities, providing a compact, independently reproduced
non-isomorphism certificate.

## Theorem and executable consequence

For a finite query system, form an incidence graph with completion vertices,
query vertices coloured by cost level, and vertices for every nonempty response
cell.  A colour-preserving graph isomorphism maps completions, queries, and
response cells.  Inductively on a policy tree, map each query and each observed
response cell; preserve the erasure branch.  The feasible completion states,
substitution counts, remaining physical-copy multiplicities, and query-level
exposures are carried bijectively at every node.  Thus any transported terminal
identification objective has the same adaptive minimax value for every positive
level-cost vector.

The checked mapping and tree transporter make this constructive.  Here every
completion has a distinct decision target, so the transported terminal goal is
exact identification.  For a general decision-identification task, decision
labels must also be transported by the completion bijection.

## Prospective unseen-family test

The frozen protocol applied every nonidentity coordinatewise `1 <-> 2` swap
that fixes the distinguished symbol `0` to all ten source words.  All seven
transformed families were unseen before execution.

| Check | Result |
|---|---:|
| Opened `P1` transfer | 51 |
| Unseen transformed families | 7/7 at 51 |
| Explicit isomorphisms edge-checked | 8/8 |
| Transported exposure antichains preserved | 8/8 |
| Independent exact boundaries, feasible at 51 | 8/8 |
| Independent exact boundaries, infeasible at 50 | 8/8 |
| Reserved cost holdouts opened | 0 |

The production solver visited 43,623 states for the source synthesis.  The
zero-THEORICA-import audit independently visited 106,284 states across the
eight target boundaries, reconstructed every partition mapping, replayed every
transported policy, and independently reproduced the `P0/P2` refinement
separation.

## Scientific consequence and limits

The old result's statement that the missing policy was family-specific is too
strong.  `P0` and `P1` require the same policy up to a non-obvious query-system
isomorphism.  Counterexample-guided policy learning over these problems must
close every new policy under certified partition-hypergraph isomorphisms before
claiming transfer failure.

This does not collapse all three obstructions into one type: `P2` is already
structurally separate.  Nor does graph non-isomorphism prove different scalar
minimax values at any particular costs.  The theorem applies to finite query
systems with matching physical multiplicities and transported terminal
decision labels; it does not establish a closed-form global ternary cost cone.

