# Clean-separator law survives a second unseen cost ray

## Exact result

The preregistered P2 holdout at level costs `(a,b,c)=(4,11,2)` passed.  At the
frozen post-erasure state, middle query group 3 remains a clean separator and
is the unique optimal first continuation.  The exact residual value is

`V(P2) = 3*b = 33`.

This extends the same state-local law from the discovery ray `(2,9,3)` and the
first unseen ray `(3,10,3)` to a ray with a larger root cost and a smaller leaf
cost.  The evidence therefore rules out the simplest explanation that the
first prospective success depended on the original root/leaf balance.

## Bellman certificate

The exact solver proves matching lower and constructive upper bounds of 33
over 4,537 value states, 3,291 actions, and 115 compatibility states.  The
optimal clean query costs 11 and has child values `[17,22,22]`.

Every competing root action is strictly worse:

- root group 0: value 37;
- middle groups 1 and 2: value 44;
- each informative leaf group: value 35.

Thus the clean separator is uniquely optimal with a two-unit margin over the
nearest leaf-query alternative.  The independent zero-production-import audit
reconstructed the clean cells, root minimum, formula `3*11`, and reserved-case
count directly from the artifact.

## Executable consequence

At this witness state, the planner can select query group 3 by detecting that
the two zero-lie candidates occupy separate response cells containing no
one-lie candidate.  On both unseen cost rays tested so far, this action attains
the sharp residual branch `3*b`.

## Scope and limitations

This is cross-ray prospective evidence, not a proof for every positive cost
triple.  The tested P2 rays are `(2,9,3)`, `(3,10,3)`, and `(4,11,2)`; the
piecewise-linear boundary outside them remains unknown.  It does not prove
clean separation sufficient for arbitrary candidate states.  Three reserved
family/cost cases have been opened cumulatively, leaving 15 sealed.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_ternary_clean_separator_second_ray.py
PYTHONPATH=src python scripts/audit_qary_ternary_clean_separator_second_ray.py
```
