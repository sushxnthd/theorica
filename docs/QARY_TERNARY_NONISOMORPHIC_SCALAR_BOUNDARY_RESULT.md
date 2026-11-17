# Non-isomorphic ternary scalar boundary: negative result

## Decisive outcome

The preregistered prediction was false.  Although the third minimal ternary
obstruction is not isomorphic to the first two as a level-coloured partition
hypergraph, it is not separated by the tested scalar or root-policy
invariants at level costs `(2,9,3)`.

| Exact invariant | Isomorphic-orbit representative `P0` | Non-isomorphic `P2` |
|---|---:|---:|
| Unrestricted optimum | 51 | 51 |
| Sorted middle-root profile | `[51,51,52]` | `[51,51,52]` |
| Unrestricted canonical exposure antichain | equal | equal |
| Three root-conditioned canonical antichains | equal | equal |

The exact root-conditioned profiles compare policies forced to begin in each
of the three logical middle subtrees while leaving every later query
unrestricted.  Sorting removes arbitrary query names.  Thus the equality is
not an artefact of relabelling roots after execution.

## Independent verification

A zero-THEORICA-import dynamic program independently proved feasibility at
each recorded value and infeasibility one unit below for:

- two unrestricted problems; and
- all six middle-root-conditioned problems.

All **8/8** exact boundaries passed over **62,004** independent states.  The
audit also confirms the equality of scalar costs, sorted root profiles, and
the recorded canonical exposure antichains.

## Scientific consequence

Partition-hypergraph isomorphism is a sufficient certificate for complete
policy transport, but its failure is not witnessed by scalar optimum, the
three-query root-cost profile, or the deterministic solver's Pareto exposure
antichains in this case.  These invariants are therefore strictly coarser than
query-system isomorphism on the observed family.

This is a preserved negative result.  The next experiment must use a finer
executable invariant, such as a bisimulation quotient of reachable mixed-fault
states or a complete set-valued policy signature.  Merely opening more cost
vectors without such an invariant would not distinguish mechanism from
coincidence.

## Limits and holdout accounting

One previously reserved case was opened: `P2` at `(2,9,3)`.  The other **18**
reserved cost-family cases remain sealed.  Equality of one canonical exposure
antichain does not enumerate every optimal policy, and the result does not
imply that the non-isomorphic families have equal values at all positive cost
vectors.

