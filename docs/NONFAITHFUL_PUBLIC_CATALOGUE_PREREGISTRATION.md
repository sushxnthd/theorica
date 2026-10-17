# Frozen external protocol: nonfaithful public-catalogue reconstruction

**Frozen before outcome generation: 13 October 2026**  
**Classification:** prospective external validation / discrimination

## Question and mechanism

Does the corrected certified-group reconstruction theorem expand THEORICA's
real capability on previously unopened public nonfaithful quandles, while
using materially fewer oracle values than complete-table disclosure?

Mechanism: once complete generator rows certify the translation group, a group
base identifies each remaining translation.  Repeated translations are then a
compression opportunity, not an ambiguity.

## Corpus and contamination controls

- Source: GAP RightQuasigroups v0.9.12 `SmallQuandle` catalogue.
- Orders: 8 and 9.
- Select 80 catalogue IDs per order by the frozen arithmetic walk in
  `scripts/export_gap_nonfaithful_public_holdout.g`.
- Exclude every ID selected by the previously opened v1/v1.1 sampler
  (step 37, offsets 23 and 29).
- Keep only exported tables whose left-translation rows are bijective and whose
  carrier-to-translation map is noninjective.
- Previously opened faithful connected quandles cannot enter the eligible set
  by definition.
- No table, property label, result, or aggregate from the selected IDs may be
  inspected before this protocol and runner are committed.

## Frozen procedure

For each eligible table:

1. Generate the full translation group from all distinct rows.
2. Produce a deterministic certificate by scanning rows in carrier order and
   adding a row exactly when it expands the generated subgroup.
3. Call the production `reconstruct_from_translation_generators` path with
   those certified row indices.
4. Independently reconstruct each row from base signatures without calling the
   production reconstruction function.
5. Run the pre-correction automatic discovery learner as a matched control.
6. Record exactness, query count, full-table fraction, group size, base size,
   distinct-translation count, and control disposition.

No tuning is permitted after outcomes.  Group-size cap is 20,000 and base-size
cap is 12, matching the published implementation.

## Preregistered predictions and gates

All gates must pass:

1. At least 50 eligible public nonfaithful holdouts.
2. Production reconstruction exact on 100% of eligible tables.
3. Independent reconstruction exact on 100% and agrees with production.
4. At least 90% of eligible tables use fewer than `n^2` distinct queries.
5. Median query reduction versus complete-table disclosure is at least 25%.
6. The old discovery learner accepts none of the eligible nonfaithful cases.
7. Selected IDs have zero overlap with the documented opened v1 sample.
8. Two complete executions produce byte-identical canonical result payloads.

## Interpretation

- **PASS:** external public-catalogue validation of the corrected scoped
  theorem and a concrete capability expansion.
- **FAIL:** preserve the exact failed gate and downgrade utility or external
  generality accordingly.
- This cannot establish automatic discovery from an unknown incomplete group,
  field-first priority, or efficiency on large-order algebras.

