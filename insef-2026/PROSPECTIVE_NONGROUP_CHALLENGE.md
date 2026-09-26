# INSEF 2026 Prospective Non-Group Challenge

**Frozen:** 26 September 2026, before inspecting any challenge outcomes.

## Purpose

Translation-Action Challenge v1.2 established cross-family exactness on public groups, faithful connected quandles, and nonassociative loops, but its non-group instances were small enough that the fixed 64-query validation budget usually exhausted the remaining table. This prospective challenge tests the unresolved claim: can the unchanged translation-base learner reconstruct *larger non-group operations* with genuinely subquadratic oracle use?

This is an INSEF-specific validation protocol. It does not modify or reinterpret v1.2.

## Primary hypothesis

On previously unopened public non-group operations satisfying the existing compact-action promise, THEORICA will exactly reconstruct every eligible operation while using less than 35% of the complete table in median total oracle calls, including validation.

The 35% threshold is deliberately weaker than the <25% v1 gate because this experiment targets harder non-group actions and counts validation calls.

## Corpus requirements

Use only public, independently curated finite-algebra catalogues that were not used in v1-v1.2 at the selected orders/identifiers. Prefer faithful connected quandles/racks and nonassociative loops of order >= 12. If a public catalogue cannot supply at least 20 unique unopened eligible non-group structures at order >= 12 under feasible compute limits, report that as a protocol feasibility failure rather than substituting opened structures.

No family label, catalogue identifier, generators, action group, base, or eligibility flag may be passed to the learner.

All exact selected catalogue identifiers/order ranges must be committed in a second freeze *before* generating learner outcomes. Selection may inspect catalogue metadata and full tables only to enforce deduplication and the scoring-only eligibility predicate; no THEORICA outcome or acquisition trace may be inspected during selection.

## Frozen learner

Use the v1.2 learner behavior unchanged:

1. acquire a full translation;
2. require bijectivity;
3. generate the action subgroup;
4. compute a permutation base;
5. identify unknown translations from base signatures;
6. acquire unresolved/colliding translations in full;
7. use a fresh validation counterexample to acquire the falsifying translation and strictly enlarge the action subgroup;
8. reconstruct or abstain.

No algorithm change is permitted after challenge outcomes are opened. Any scientifically motivated change creates a separately named successor experiment and this challenge remains a null/failure.

Frozen limits unless feasibility preflight proves they are computationally impossible before outcomes are opened:

- maximum generated action-group size: 100,000;
- maximum base size: 16;
- maximum acquired complete translation rows: 12.

A feasibility-only adjustment must be committed before outcome generation and cannot depend on reconstruction performance.

## Validation budget

To prevent validation from becoming exhaustive on moderate tables, validation uses

`v(n) = min(64, max(16, ceil(0.05*n^2)))`

uniformly sampled, previously unqueried table cells, or all remaining cells if fewer remain.

Report acquisition and validation calls separately. Duplicate oracle requests count once in total unique queried cells and must also be reported as raw calls for auditability.

## Scoring-only eligibility

After evaluation, the hidden full table may be used only by the scorer. An operation is eligible iff:

1. every learner-side left translation is a permutation;
2. the carrier-to-translation map is injective;
3. the full translation group has at most 100,000 elements;
4. a deterministic greedy base has size at most 16.

Eligibility is never exposed to the learner.

## Baselines

Run all baselines on the identical selected structures and frozen seeds:

1. **Same-representation random acquisition:** identical representation, closure, base, signatures, validation, and limits; when a new full translation is needed, select a uniformly random unqueried translation rather than the unresolved/counterexample-directed one.
2. **Uniform-cell sampling:** spend exactly THEORICA's realized unique-query budget on uniformly sampled table cells; it receives no family label. Score exact full-table recovery only if its observations uniquely determine a table under an explicitly implemented hypothesis class; otherwise mark as non-reconstruction. This baseline is diagnostic and must not be overstated.
3. **Full table:** n^2 oracle values, shown as the trivial reference cost, not a competing learner.

The random-acquisition baseline is the primary policy ablation.

## Frozen seeds

Use acquisition seeds 307, 401, and 503 for each selected algebra. These seeds have not been used in v1-v1.2.

## Primary gates

The prospective result passes only if all are true:

1. at least 20 unique eligible unopened non-group algebras of order >= 12 are evaluated;
2. THEORICA exactly reconstructs 100% of eligible task/repeat cases;
3. zero false acceptances occur on any retained out-of-promise controls;
4. median total unique-query fraction on eligible cases is < 35%;
5. at least 75% of eligible unique algebras individually have median query fraction < 50%;
6. among cases where both policies are exact, THEORICA's mean unique-query count is lower than same-representation random acquisition and the one-sided paired Wilcoxon p-value is < 0.05;
7. every result is reproducible from a clean environment using committed code and public catalogue provenance.

No gate may be relaxed after outcomes are opened.

## Secondary analyses

Report without converting them into post-hoc success criteria:

- query fraction versus n;
- acquired full-row count;
- discovered action-group size and base size;
- validation-triggered subgroup expansions;
- family-stratified results;
- abstentions and failure mechanisms;
- exact wins/ties/losses versus random acquisition;
- wall-clock time and peak memory.

## Failure policy

Any failed primary gate is preserved as a negative result. Do not drop difficult structures, replace failed seeds, weaken thresholds, increase row/base/group limits after seeing outcomes, or relabel a null as success. Diagnose the mechanism and, only if justified, preregister a distinct successor experiment.

## Claim boundary if passed

A pass would support: on a prospective public set of larger, previously unopened non-group operations satisfying the stated compact-action promise, the family-agnostic learner reconstructed exactly while querying a minority of table cells, and its representation-aware acquisition policy outperformed a same-representation random acquisition control.

It would **not** establish universal finite-algebra reconstruction, historical priority, robustness to noisy oracle answers, or superiority to specialized algorithms given the correct algebraic family in advance.
