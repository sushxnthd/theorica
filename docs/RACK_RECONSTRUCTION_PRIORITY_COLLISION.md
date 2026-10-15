# Rack reconstruction priority audit: decisive claim narrowing

**Audit date:** 2026-10-16  
**Repository line:** `breakthrough-engine/nonfaithful-reconstruction-boundary-20261013` / PR #4  
**Decision:** **PRIOR-ART COLLISION for broad algebraic novelty; retain only scoped oracle-model and systems claims**

## Question

Is THEORICA's certified reconstruction of a finite left rack from seed translations, using

[
L_{x*y}=L_xL_yL_x^{-1},
]

and therefore (|S|n) complete-row oracle cells for an operation-generating seed set (S), a new algebraic reconstruction mechanism?

## Answer

No. The broad reconstruction mechanism is absorbed by the established Joyce–Blackburn representation of racks by permutation groups and rack envelopes. Vojtěchovský and Yang explicitly use this representation for rack/quandle enumeration, and the official GAP **RightQuasigroups** package implements rack envelopes. In that representation, translations for orbit elements are recovered from representative translations by conjugation, after which the operation table is recovered from the translations.

THEORICA's exact (|S|n) count is a valid cost statement for its particular complete-row oracle: acquiring (|S|) full translations costs (|S|n) cells. The audit did not locate that cost statement verbatim. However, once the classical representation is known, this is elementary accounting rather than a sufficiently distinct field-level algebraic contribution.

## Primary evidence

1. **Vojtěchovský and Yang, “Enumeration of racks and quandles up to isomorphism,” Mathematics of Computation 88(319), 2019.** The paper states that its enumeration algorithms are based on the representation of racks and quandles in symmetric groups due to Joyce and Blackburn and gives reconstruction/enumeration procedures using rack envelopes.  
   DOI: https://doi.org/10.1090/mcom/3409

2. **GAP RightQuasigroups manual, Chapter 11 (“Racks and quandles”).** The documented Joyce–Blackburn rack envelope is a triple consisting of a permutation group, orbit representatives, and representative translations. The manual reconstructs every translation by conjugation and then reconstructs the rack operation; it exposes `RackByRackEnvelope` and `QuandleByQuandleEnvelope`.  
   Documentation: https://gap-packages.github.io/RightQuasigroups/doc/chap11_mj.html

These are stronger than a terminology-level resemblance: they contain the same representation-level mechanism and a working external implementation.

## Collision matrix

| Component of the THEORICA line | Priority assessment | Status |
|---|---|---|
| Translation conjugation identity | Classical rack theory | **ABSORBED** |
| Recovering all rack translations from representative translations and their permutation action | Joyce–Blackburn rack envelopes; implemented in GAP | **ABSORBED** |
| Full operation-table reconstruction once translations are known | Standard consequence of translations | **ABSORBED** |
| Exact (|S|n) complete-row query count for an operation-generating seed set | Not located verbatim; direct oracle-accounting corollary of the established mechanism | **VALID BUT NOT FLAGSHIP-NOVEL** |
| Fail-closed certificate and runtime integration in THEORICA | Project-specific systems work | **ENGINEERING CONTRIBUTION** |
| Complete-row seed acquisition lower bound: rank (2) yet (n) queried rows may be necessary | No direct collision found in this audit | **REMAINS A CANDIDATE; PRIORITY UNRESOLVED** |
| General permutation-row completeness cost (rn+(n-r)(n-1)) | Separate oracle-model theorem; not implied by the rack-envelope constructor | **REMAINS A CANDIDATE; PRIORITY UNRESOLVED** |

“Not located” is not evidence of novelty. The two unresolved rows require a dedicated expert and primary-literature audit before any priority claim.

## SCIENCE ledger update

### KNOWN

- For certified finite left racks, the translation conjugation identity is correct.
- Under an externally valid operation-generating seed certificate, THEORICA reconstructs the table after acquiring (|S|) full seed rows.
- The Joyce–Blackburn/rack-envelope literature already reconstructs racks from permutation-group data and representative translations.
- An official GAP package implements the envelope construction.

### FALSIFIED

- **Falsified claim:** the seed-translation reconstruction is a new algebraic mechanism.
- **Falsified positioning:** the (|S|n) result by itself can serve as THEORICA's flagship mathematical novelty.

### BELIEVED

- The (|S|n) statement remains useful as an exact cost contract for THEORICA's complete-row oracle and as a systems optimization.
- THEORICA's strongest potentially distinct result in this line is now the separation between a small reconstruction certificate and the cost of discovering/certifying it.

### CONFLICTING / UNTESTED

- Historical priority for the exact complete-row acquisition lower bound remains unresolved.
- Historical priority for the general (rn+(n-r)(n-1)) promise-certification boundary remains unresolved.
- No claim is made about partial-cell, noisy, randomized, average-case, or family-specific query complexity.

## CONSEQUENCE ledger update

1. **Demote** the rack seed-row theorem from prospective flagship novelty to a correctness/performance feature built on classical representation theory.
2. **Keep** the implementation and exhaustive checks: they validate THEORICA's fail-closed rack path, but should be described as systems evidence.
3. **Do not market** the conjugation/reconstruction mechanism as new in HAA or publication materials.
4. **Reformulate the active kernel** around the unresolved systems-science boundary:

   > Under partial-cell access, what is the sharp zero-error or explicitly probabilistic cost of acquiring and certifying a sufficient rack reconstruction witness, and when can family-specific identities beat the complete-row impossibility?

5. The next kernel must compare against:
   - direct full-table acquisition;
   - Joyce–Blackburn/rack-envelope reconstruction with externally supplied representatives;
   - complete-row adaptive acquisition;
   - the existing general permutation-row certification bound;
   - any partial Latin-square/quasigroup completion and black-box algebra controls found in the next audit.

## Smallest supported claim

> THEORICA implements a fail-closed, exact-cost rack reconstruction path that specializes the classical translation/rack-envelope representation to a complete-row oracle. Its algebraic mechanism is not new. The scientifically unresolved contribution is the oracle-model gap between possessing a small reconstruction witness and discovering or certifying one.

## Kill and success conditions for the reformulated kernel

**Kill:** primary literature already gives an equal-or-stronger partial-query lower/upper bound under the same oracle promises, or the proposed bound does not alter THEORICA's runtime contract.

**Publishable success:** a sharp lower/upper bound or minimal counterexample for partial-cell/noisy witness acquisition that (i) survives exact finite enumeration and an independent proof/check, (ii) is not absorbed by rack envelopes, table completion, or black-box algebra, and (iii) changes THEORICA's query planner or certificate format.

## Breakthrough gate

**FAIL for broad novelty of the rack reconstruction mechanism.**  
**INCONCLUSIVE for the remaining acquisition/certification boundaries.**

This audit is intentionally a claim reduction, not a negative assessment of correctness or engineering value.
