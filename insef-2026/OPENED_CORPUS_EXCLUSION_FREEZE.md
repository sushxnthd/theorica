# INSEF prospective challenge: opened-corpus exclusion freeze

**Date:** 26 September 2026  
**Status:** pre-outcome exclusion boundary. No prospective THEORICA learner or baseline outcome is opened by this document.

## Purpose

This file mechanically records the public catalogue strata that were already opened by Translation-Action Challenge v1-v1.2 and therefore cannot be used as prospective evidence in the INSEF non-group challenge.

The source of truth for this audit is the frozen v1.1 exporter `scripts/export_gap_translation_challenge_v1_1.g`; v1.2 reused the same public corpus and changed the learner mechanism after the preserved v1.1 failure.

## Already-opened catalogue strata

### SmallGrp

All catalogue identifiers at orders:

- 24
- 32
- 36
- 40
- 48

are opened. No SmallGrp instance at those orders is eligible for the prospective non-group challenge. The new challenge is non-group in any case.

### SmallQuandle abstention controls

At orders 6, 7, 8 and 9, 25 deterministic catalogue IDs per order were opened using the frozen `SampleIds(count, 25, offset)` rule with offsets 11, 17, 23 and 29 respectively.

These exact IDs are excluded. More conservatively, the prospective challenge will use no order <12 structure, so the entire opened SmallQuandle range is outside the preregistered order gate.

### Faithful connected quandles

At each of orders 6, 7, 8 and 9, up to 25 deterministic positions in `ConnectedQuandles(n, IsFaithfulRightQuasigroup)` were opened using offset `101 + 13*n`.

All of these are excluded. Again, the prospective challenge's order >=12 gate makes the exclusion automatic.

### SmallLoop

Opened positive nonassociative-loop structures:

- every `SmallLoop(5,id)` for id 1..5;
- 25 deterministic IDs from the 107 order-6 SmallLoops, sampled with offset 41.

All are excluded. The order >=12 gate makes the exclusion automatic.

## Consequence for the prospective challenge

The preregistered order >=12 requirement creates a clean catalogue-order separation from every previously opened non-group instance in v1-v1.2. Therefore a new corpus drawn exclusively from maintained public non-group catalogues at order >=12 cannot reuse a v1-v1.2 table by exact order/identifier, provided:

1. associative/group tables are rejected;
2. exact table hashes are checked against any earlier exported artifact that becomes available;
3. isomorphic duplicates within the new prospective corpus are removed before learner outcomes;
4. connected-quandle orientation is normalized by one catalogue-wide deterministic convention, never per-instance based on eligibility or performance;
5. exact package versions, catalogue identifiers, table hashes and eligibility outputs are frozen before learner/baseline acquisition is run.

## Frozen orientation rule

The historical exporter documents that RightQuasigroups quandle tables were transposed because the package's catalogue convention exposes right translations while THEORICA's frozen learner is expressed through left translations. For the prospective challenge:

- loop catalogues: use `MultiplicationTable(L)` without transposition;
- RightQuasigroups connected-quandle catalogues: use `TransposedMat(MultiplicationTable(Q))` for every selected quandle, independent of eligibility/outcome;
- no table may be transposed or re-oriented after its scoring-only eligibility result or learner outcome is known.

This preserves the previously declared semantic convention rather than choosing an orientation opportunistically.

## Next freeze

The next artifact must be an exact prospective identifier manifest. It should preferentially include multiple independently catalogued non-group families at order >=12 and target >=30 preselected structures if >=20 satisfy the frozen scoring-only eligibility predicate. The identifier manifest, table hashes, package versions and selection-script hash must be committed before any prospective learner or baseline result is generated.
