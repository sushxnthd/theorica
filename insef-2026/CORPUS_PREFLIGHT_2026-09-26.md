# Prospective non-group corpus feasibility preflight

**Date:** 26 September 2026  
**Status:** pre-outcome corpus feasibility only. No THEORICA learner outcome or acquisition trace was inspected.

## Decision

The preregistered requirement of at least 20 previously unopened public non-group operations of order >=12 is feasible from independently curated GAP catalogues. There is no justification to weaken the corpus gate or reuse opened v1-v1.2 structures.

## Public catalogue evidence

### Primary source: GAP LOOPS / RightQuasigroups

The maintained LOOPS package exposes independently curated libraries of nonassociative loops. Its Moufang catalogue alone contains:

| order | catalogue size |
|---:|---:|
| 12 | 1 |
| 16 | 5 |
| 20 | 1 |
| 24 | 5 |
| 28 | 1 |
| 32 | 71 |
| 36 | 4 |
| 40 | 5 |
| 42 | 1 |
| 44 | 1 |
| 48 | 51 |
| 52 | 1 |
| 54 | 2 |
| 56 | 4 |
| 60 | 5 |
| 64 | 4262 |

The same package contains 80 nonassociative Steiner loops of order 16, and its right-conjugacy-closed catalogue contains 155 order-12, 97 order-14, 17 order-15, and 6317 order-16 loops, among much larger higher-order collections.

Primary documentation:
- https://gap-packages.github.io/loops/doc/chap9.html
- https://gap-packages.github.io/RightQuasigroups/doc/chap12.html

### Secondary independent family: connected quandles

RightQuasigroups documents a catalogue containing all connected quandles of order <48 up to isomorphism. This supplies a second non-group family if unopened identifiers/orders remain after comparison with the v1-v1.2 manifest.

Documentation:
- https://gap-packages.github.io/RightQuasigroups/doc/chap12.html
- https://github.com/gap-packages/rig

## Selection policy for the second freeze

Do **not** run the learner yet. The next corpus-selection step must:

1. read the complete v1-v1.2 corpus manifest and exclude every previously opened catalogue family/order/identifier;
2. enumerate catalogue metadata only from maintained public GAP libraries;
3. materialize full tables only for deduplication and the already-frozen scoring-only eligibility predicate;
4. reject associative/group tables and isomorphic duplicates across overlapping catalogues;
5. prefer a family-stratified challenge rather than filling the set with one abundant catalogue;
6. target at least 30 selected structures if >=20 pass the frozen eligibility predicate, giving the experiment resilience to legitimate pre-outcome ineligibility without post-outcome replacement;
7. freeze exact package versions, catalogue identifiers, table hashes, selection script hash and eligibility output before any THEORICA or baseline acquisition outcome is generated.

Suggested candidate strata, subject to unopened-manifest audit:
- nonassociative Moufang loops: orders 16, 24, 32, 36, 40, 48;
- Steiner loops: order 16;
- RCC loops: orders 12, 14, 15, 16;
- connected quandles: unopened orders 12-47.

The exact identifiers are deliberately **not** selected in this document because the previous challenge manifest must be mechanically compared first. Selecting by memory risks leakage or accidental reuse.

## Important orientation check

The frozen learner is written in terms of left translations. RightQuasigroups/Rig documentation often describes quandles using right multiplication. The corpus builder must normalize each public operation into the learner's declared orientation and then apply the frozen scoring-only predicates. Do not silently transpose a table merely to make a structure eligible. Any orientation conversion must be deterministic, documented, applied to an entire declared catalogue stratum, and frozen before outcomes.

## Feasibility conclusion

Gate 1 is feasible at the catalogue-supply level by a wide margin. The bottleneck is now not finding >=20 public structures; it is producing a leakage-safe exact identifier manifest that is disjoint from v1-v1.2 and satisfies the frozen action-group/base limits. No experiment threshold or learner limit needs modification at this stage.
