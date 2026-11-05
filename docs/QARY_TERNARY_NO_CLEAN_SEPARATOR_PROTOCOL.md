# Frozen complementary no-clean-separator experiment

## Prior evidence

At the post-erasure witness state, P2 has a middle-level clean separator and
its exact residual values follow `3*b`: 27 at `(2,9,3)` and prospectively 30
at `(3,10,3)`.  At the discovery ray, P0 has no clean separator and its exact
residual is 29, equal to `a + 3*b`.

## Frozen prospective claim

Open exactly one additional reserved family/cost case:

- family: P0 = `{0,1}^3 union {(2,0,0),(2,1,0)}`;
- level costs: `(a,b,c)=(3,10,3)`;
- state: after one erased middle query and root answer `2`, with the eight
  binary-cube completions at lie count one, the two added completions at lie
  count zero, three copies left of query groups 0 and 1, and four copies of
  every other group;
- structural prediction: no remaining middle query cleanly separates both
  zero-lie completions from each other and from all one-lie completions;
- numerical prediction: the exact residual value is `a + 3*b = 33`;
- separation prediction: the P0/P2 residual gap at this ray is exactly 3.

The claim passes only if exhaustive enumeration rejects every middle clean
separator and exact Bellman search independently proves matching lower and
constructive upper bounds of 33.  Any finite value other than 33,
infeasibility, or discovered clean separator falsifies the claim and must be
preserved.  No other reserved case may be opened in this run.  A pass leaves
16 reserved family/cost cases sealed.

## Independent audit

The primary artifact must contain every remaining middle response partition,
the exact root action table, state/action counts, and the prior P2 value 30.
A non-importing audit must recompute clean-separator absence directly from the
emitted partitions, check `3 + 3*10 = 33`, check the exact gap 3, and verify the
reserved-case count.
