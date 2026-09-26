# INSEF prospective non-group challenge: identifier manifest

**Freeze date:** 26 September 2026  
**Status:** pre-outcome. This manifest fixes catalogue identifiers before any prospective THEORICA learner or baseline acquisition is run.

## Purpose

This is the exact candidate identifier pool for the prospective larger-order non-group challenge. It follows `OPENED_CORPUS_EXCLUSION_FREEZE.md`: all candidates have order >= 12, none belongs to any non-group order opened by Translation-Action Challenge v1-v1.2, and loop tables use their catalogue multiplication-table orientation without outcome-dependent reorientation.

The pool deliberately spans three independently named public RightQuasigroups library families. Catalogue membership is not itself an eligibility signal available to the learner.

## Frozen candidate pool

### A. Moufang loops

Library: `Moufang loops`  
Constructor: `MoufangLoop(32,id)`  
Order: 32  
Candidate IDs (12):

`1, 7, 13, 19, 25, 31, 37, 43, 49, 55, 61, 67`

The maintained RightQuasigroups catalogue documents 71 nonassociative Moufang loops of order 32. The arithmetic progression is fixed here before scoring or learner outcomes.

### B. Steiner loops

Library: `Steiner loops`  
Constructor: `SteinerLoop(16,id)`  
Order: 16  
Candidate IDs (12):

`2, 9, 16, 23, 30, 37, 44, 51, 58, 65, 72, 79`

The maintained catalogue documents 80 nonassociative Steiner loops of order 16. ID 1 is deliberately not privileged; the fixed stride-7 sample is used instead.

### C. right-conjugacy-closed loops

Library: `RCC loops`  
Constructor: `RCCLoop(14,id)`  
Order: 14  
Candidate IDs (12):

`3, 11, 19, 27, 35, 43, 51, 59, 67, 75, 83, 91`

The maintained catalogue documents 97 nonassociative RCC loops of order 14. The fixed stride-8 sample is frozen before scoring or learner outcomes.

**Total frozen candidates: 36.**

## Pre-outcome processing contract

The following steps are permitted before learner/baseline acquisition and must be recorded for every candidate:

1. instantiate the exact catalogue object above;
2. export `MultiplicationTable(L)` exactly as returned by the package;
3. record GAP and RightQuasigroups package versions;
4. compute a SHA-256 hash of a canonical row-major table serialization;
5. verify order and reject any associative/group table if a package/version mismatch unexpectedly returns one;
6. run only the already-frozen scoring-only theorem-promise eligibility predicate;
7. detect exact duplicates and isomorphic duplicates across the 36 candidates without consulting learner query cost, learner correctness or baseline outcomes;
8. retain the first candidate in manifest order when a duplicate equivalence class is found;
9. freeze the resulting eligible/deduplicated table hashes and eligibility outputs in a new commit;
10. only after that commit may prospective THEORICA and baseline acquisition be executed.

No candidate may be replaced because it is ineligible, duplicated, expensive, difficult, or later fails reconstruction. No new candidate may be added to reach a desired result. If fewer than 20 unique candidates survive the frozen pre-outcome filters, the prospective experiment is a preregistered feasibility null and the learner is not opened on a selectively enlarged corpus.

## Orientation

All three selected families are loop catalogues. Therefore every candidate uses `MultiplicationTable(L)` without transposition. The historical quandle transpose convention is irrelevant to this manifest because no RightQuasigroups quandle catalogue is included.

## Why these strata

The pool is intentionally heterogeneous rather than taking 36 neighboring entries from one catalogue. Moufang, Steiner and RCC loops impose different algebraic identities while remaining nonassociative loop families. This makes a positive prospective result more informative about cross-family translation-action reconstruction and makes a failure diagnostically useful.

## Frozen outcome rule

The candidate list, ordering, package orientation and pre-outcome filtering contract above are immutable for this challenge. Any implementation error discovered later must be documented; it cannot be silently repaired after outcomes are inspected. Existing preregistered success gates in the INSEF prospective challenge remain controlling.