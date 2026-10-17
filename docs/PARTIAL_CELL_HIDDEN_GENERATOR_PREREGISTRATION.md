# Frozen protocol: partial-cell localization of hidden rack generators

**Frozen:** 16 October 2026  
**Classification:** exact query-complexity theorem / system-interface discrimination  
**Active kernel:** partial-cell acquisition of sufficient rack witnesses  
**Prior broad reconstruction mechanism:** retired as prior art

## Precise question

In the rank-2 adversarial rack family used by the complete-row acquisition lower
bound, what is the exact deterministic cell-query complexity of locating a
sufficient two-element generating seed?

For (nge 3), a distinguished element (z), and an arbitrary full cycle
(sigma) on (Xsetminus{z}), define (R(n,z,sigma)) by

- (L_x=mathrm{id}) for (x
e z);
- (L_z(z)=z) and (L_z|_{Xsetminus{z}}=sigma).

The oracle answers individual cells (x*y=L_x(y)). The family promise
(R(n,z,sigma)) is externally certified, but (z) and (sigma) are unknown.
The task is only to return a valid two-element operation-generating seed, not to
reconstruct the full table.

## Frontier and controls

The existing complete-row theorem forces (n) row acquisitions in the worst
case, costing (n^2) cells, even though the generating rank is 2. It explicitly
does not cover partial-cell queries.

Controls:

1. complete-row acquisition: (n^2) cells in the deterministic worst case;
2. full-table acquisition: (n^2) cells;
3. semantic seed: zero oracle cells when (z) is supplied;
4. partial-cell scan: query one off-diagonal cell in candidate rows and infer
   the last remaining row after (n-1) identity answers.

## Exact hypothesis

The deterministic zero-error query complexity of locating (z), and hence a
valid seed ({z,a}) for any (a
e z), is exactly (n-1) cells.

- Upper bound: for each of (n-1) candidate rows, query any column different
  from the row label. A nonidentity answer identifies (z); if all answers are
  identity, the omitted row is (z).
- Lower bound: after fewer than (n-1) queries, at least two row labels have
  never received an off-diagonal query. The all-identity transcript is
  compatible with either label being (z), using a full cycle on its
  complement. A deterministic zero-error algorithm cannot identify (z).

The predicted uniform-label expected cost of a fixed scan order is
((n+1)/2-1/n), counting inference of the final unqueried candidate.

## Strongest alternative explanation

The apparent reduction may fail if a full cycle fixes a queried off-diagonal
column, if the constructed tables violate the rack identity, if two elements do
not generate the operation closure, or if adaptivity can eliminate multiple
candidate rows with one cell query.

## Cheapest decisive falsification

For every (3le nle64), every distinguished row (z), and canonical cycles
in both orientations:

- verify the rack identity exactly;
- verify minimum generating rank 2;
- run the partial-cell scan for every omitted-last ordering;
- require localization in at most (n-1) queries;
- construct the two unprobed-row indistinguishability witness for every
  transcript length (q<n-1);
- check the exact expected-cost identity using rational arithmetic.

A separately written audit must reproduce the construction and all formulas
without importing the primary verifier.

## Gates

All must pass:

1. zero rack-identity failures;
2. zero generating-rank disagreements;
3. maximum localization cost exactly (n-1) for every (n);
4. zero invalid returned seeds;
5. zero lower-bound witness failures for every (q<n-1);
6. exact expected-cost equality for every (n);
7. independent audit exact agreement.

## Publishable success condition

A proof plus exact and independent verification of the (n^2) versus (n-1)
oracle-interface separation, stated only for this promised rack family.

## Project-relevance threshold

THEORICA must gain a concrete partial-cell query-planner primitive: when a
family certificate guarantees one hidden fixed-point-free generator row,
localize it with off-diagonal probes before requesting any complete row.

## Kill condition

Kill the claimed separation if any family member is not a rack, has generating
rank other than 2, requires more than (n-1) probes, admits a deterministic
zero-error strategy with worst-case fewer than (n-1), or fails independent
reproduction.

## Claim boundary

This is not a lower bound or algorithm for arbitrary racks, noisy oracles,
unknown family membership, or full-table reconstruction. It assumes the family
promise is certified outside the private query transcript. Historical priority
is not asserted.
