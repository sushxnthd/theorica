# Two-branch boundary transfers to a second unseen cost ray

## Exact prospective result

The preregistered P0 holdout at level costs `(a,b,c)=(4,11,2)` passed.  At the
frozen post-erasure state, none of the three remaining middle queries is a
clean separator, and exact Bellman enumeration gives

`V(P0) = a + 3*b = 37`.

The previously committed P2 result on the same ray is `V(P2)=3*b=33`, so the
prospective family gap is exactly `V(P0)-V(P2)=a=4`.  Together with the first
unseen ray `(3,10,3)`, where the corresponding values were 33 and 30, this is
a second prospective transfer of both branches and of the root-cost gap.

## Bellman certificate

The exact solver proves matching lower and constructive upper bounds of 37
over 5,392 value states, 4,571 actions, and 135 compatibility states.  Root
group 0 and middle group 3 tie as optimal:

- root group 0: child values `[17,17,33]`, action value 37;
- middle group 3: child values `[26,22]`, action value 37;
- each informative leaf group: action value 39;
- middle groups 1 and 2: action value 48.

Middle group 3 remains optimal even though its response cells fail the clean
criterion; thus clean separation identifies the lower `3*b` branch but is not
necessary for a middle query to participate in an optimal policy on the
`a+3*b` branch.  A zero-production-import audit reconstructed all partition
classifications, the Bellman root minimum, `4+3*11`, the four-unit gap, and the
reserved-case count solely from the emitted artifact.

## Executable consequence

For this witness state on both prospectively tested rays, a planner can use the
clean-cell predicate to distinguish the exact residual branches: a clean P2
instance attains `3*b`; the complementary non-clean P0 instance incurs exactly
one additional root-query cost `a`.  The stored root-action table provides an
optimal policy certificate rather than only a numerical comparison.

## Scope and limitations

This is a state-local two-ray theorem candidate backed by exact prospective
enumeration, not a universal proof over all positive cost triples or all
candidate states.  It does not establish that every non-clean family pays
exactly `a`, nor that clean separation is necessary for an optimal middle
action.  Four reserved family/cost cases have been opened cumulatively, leaving
14 sealed.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_ternary_no_clean_separator_second_ray.py
PYTHONPATH=src python scripts/audit_qary_ternary_no_clean_separator_second_ray.py
```
