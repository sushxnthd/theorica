# Nonfaithful Translation Reconstruction: Exact Boundary and System Correction

**Result date:** 13 October 2026  
**Classification:** exact theorem correction + exhaustive finite verification + system capability  
**Overall breakthrough gate:** **INCONCLUSIVE** (priority and external validation remain open)

## Smallest supported claim

Let `F:S x S -> S` have bijective left translations `L_x`, and suppose a
certified permutation group `G <= Sym(S)` contains every `L_x`.  If `r`
completely queried rows generate `G` and `B` is a base of size `b`, then the
whole table is exactly reconstructible from

```
rn + (n-r)b
```

distinct oracle values.  The map `x -> L_x` need not be injective.

For the remaining-row promise class in which each row may be any element of
known `G`, a common queried coordinate set identifies every possible row if
and only if it is a base of `G`.

## Proof

Query the `r` generator rows completely to recover `G`.  A base `B` makes the
restriction map `g -> g|B` injective on `G`; therefore the `b` answers on `B`
uniquely identify each remaining translation.  Repeated signatures correctly
mean repeated translations, not ambiguity.  Reusing generator-row answers
gives `rn+(n-r)b` queries.

Conversely, if a common coordinate set `C` is not a base, distinct `g,h in G`
agree on `C`.  Two promised remaining rows equal to `g` and `h` therefore have
identical transcripts on `C` but differ elsewhere.  Hence `C` cannot identify
all promised rows.

## Decisive exact evidence

Two separately written enumerators rebuilt group closure, minimum generators,
bases, and signature reconstruction.  Both exhaust all permutation-row binary
operations through order 4.

| Order `n` | All operations | Faithful | Nonfaithful | Reconstruction failures |
|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 0 | 0 |
| 2 | 4 | 2 | 2 | 0 |
| 3 | 216 | 120 | 96 | 0 |
| 4 | 331,776 | 255,024 | 76,752 | 0 |
| **Total** | **331,997** | **255,147** | **76,850** | **0** |

Primary enumeration canonical digest:
`4c986ea98c68d26bcfc90b1cf03e4d5284248cdd22db20b7ee83f668999de0ab`.

Independent audit canonical digest:
`28646f21b4cdc2dde89355be9bfb1a37d81b5dfcc27ee472912c94fa43b24e56`.

## Minimal counterexample to the old implementation boundary

On `S={0,1}`, let

```
F = [[0,1],
     [0,1]].
```

Both left translations are the identity.  The operation is nonfaithful, yet
one complete generator row determines the trivial group, whose empty set is a
base.  Reconstruction is exact in 2 queries.  The pre-correction discovery
learner rejects the same table with
`nonfaithful_or_unresolved_translation_action`.

This is a counterexample to the learner's old *scope*, not to its safety: when
the current subgroup is not certified complete, a collision can still mean
that an unseen translation lies outside it.

## SCIENCE ledger

- **KNOWN:** faithfulness is absent from the reconstruction proof and is not a
  conditional identifiability requirement.
- **KNOWN:** a group base is the sharp common-coordinate boundary for uniformly
  identifying arbitrary members of a certified permutation group.
- **KNOWN:** two independent implementations found zero failures in all
  331,997 operations through order 4, including 76,850 nonfaithful cases.
- **FALSIFIED:** repeated translations necessarily make exact reconstruction
  ambiguous.
- **CONFLICTING:** collisions are harmless under a certified complete group but
  remain unsafe evidence under an incomplete discovered subgroup.
- **UNTESTED:** automatic certification/refinement that safely recovers
  nonfaithful actions without externally supplied generator completeness.
- **UNTESTED:** historical priority for this exact operation-reconstruction
  statement; no first-ever claim is made.

## CONSEQUENCE ledger

- Added a certified-generator reconstruction path that accepts repeated
  translations and returns exact tables.
- Corrected the public theorem premise and sharpened its query accounting.
- Expanded the mathematically supported scope from faithful racks/quandles to
  nonfaithful ones **when** group containment and generation are certified.
- Preserved the conservative discovery learner: it still abstains when the
  completeness promise is unavailable.

## Prior-art collision audit

The ingredients are classical.  Sims introduced bases/strong generating sets
for computational permutation groups, and a base's action coordinates uniquely
determine a group element.  Quandle literature explicitly studies the inner
representation and distinguishes faithful from nonfaithful quandles.  These
sources absorb novelty claims for permutation bases, inner representations,
and nonfaithfulness itself:

- C. C. Sims, *Computational methods in the study of permutation groups*
  (1970): https://doi.org/10.1016/B978-0-08-012975-4.50020-5
- W. E. Clark et al., *Algebraic properties of quandle extensions and values
  of cocycle knot invariants* (2016):
  https://doi.org/10.1016/j.jkss.2015.12.004
- Y. Tada, *On categories of faithful quandles with surjective or injective
  quandle homomorphisms* (2022): https://arxiv.org/abs/2211.15014

The defensible contribution today is an exact correction and capability
expansion inside THEORICA.  A broader novelty claim requires expert prior-art
review and an external nonfaithful benchmark.

## Reproduction

```bash
python scripts/verify_nonfaithful_translation_reconstruction.py \
  --max-n 4 --output results/nonfaithful_translation_boundary.json
python scripts/audit_nonfaithful_translation_reconstruction.py \
  --max-n 4 --output results/nonfaithful_translation_boundary_audit.json
pytest -q
```

## Limitations and next decisive experiment

This result assumes bijective translations, certified containment in `G`, and
certified generator completeness.  It does not solve safe group discovery from
an unknown nonfaithful operation, prove subquadratic behavior for large-base
groups, or establish field-first priority.

The cheapest decisive next experiment is a frozen public corpus of
nonfaithful quandles/racks with hidden generator certificates, paired with a
collision-refinement learner.  Success requires exact reconstruction without
false acceptance on out-of-promise controls; failure should localize whether
completeness certification or base growth is the limiting mechanism.
