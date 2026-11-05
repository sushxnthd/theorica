# Frozen clean-separator residual experiment

## Discovery evidence (not prospective)

At level costs `(a,b,c)=(2,9,3)`, follow the common optimal prefix in the
P0/P2 obstruction families: erase the first middle query, then answer `2` to
the root query.  Eight binary-cube completions then have lie count one and the
two added completions have lie count zero.  The exact continuation values are
29 for P0 and 27 for P2.

P2, but not P0, has a remaining middle-level query whose response partition
puts the two zero-lie completions in distinct cells and puts no one-lie
completion in either cell.  Call this Boolean state predicate a **clean
separator**.  The observed values are exactly

`3*b` when a clean separator exists, and `a + 3*b` when it does not.

## Frozen prospective claim

Open exactly one previously reserved family/cost case:

- family: P2 = `{0,1}^3 union {(2,1,0),(2,2,0)}`;
- level costs: `(3,10,3)`;
- state: the analogous state after one erased middle query and root answer
  `2`, with three copies left of those two query groups and four copies of all
  other groups;
- structural prediction: the clean-separator predicate is true;
- numerical prediction: the exact residual value is `3*b = 30`.

The experiment passes only if an exact Bellman search independently verifies
both the structural predicate and residual value 30.  A different finite
value, infeasibility, or failed replay falsifies the claim and is preserved.
No second reserved case is opened in this run.  Success leaves 17 reserved
family/cost cases sealed.

## Audit requirements

The verifier must emit the witness query and its response cells, an exact
lower/upper value agreement, explored-state counts, and a deterministic JSON
artifact.  A separate audit must recompute the predicate from the emitted
cells and check the preregistered arithmetic without importing the production
verifier.
