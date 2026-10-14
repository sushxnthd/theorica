# Preregistration: rack-generated translation closure

**Frozen before outcome inspection:** 2026-10-14  
**Kernel:** family-specific compression of exact translation reconstruction

## Precise question

For a finite operation whose left translations form a rack, can THEORICA replace the general
`r*n + (n-r)*(n-1)` completeness-certificate cost by exact reconstruction from only `r*n`
oracle cells when the queried row indices generate the carrier under the operation?

## Hypothesis and mechanism

For a left rack, left self-distributivity gives

`L_(x*y) = L_x L_y L_x^-1`.

Therefore complete rows for a seed set `S` determine the row at every element in the forward
operation closure of `S`. If that closure is the entire carrier, all rows are determined without
base probes, random validation, or a translation-group completeness certificate.

## Preregistered predictions

1. A deterministic closure algorithm reconstructs every finite rack table whenever its supplied
   seed set forward-generates the carrier.
2. Reconstruction uses exactly `|S|*n` distinct oracle cells.
3. Every alternative derivation of the same row yields the same permutation.
4. Removing conjugation, reversing composition order, or applying the method to a non-rack yields
   a concrete disagreement on the exhaustive development corpus.
5. Exhaustive enumeration of every permutation-row operation through order 4 finds no rack
   counterexample for any nonempty forward-generating seed subset.

## Exact objective and gates

- Exhaust all `(n!)^n` permutation-row operations for `n=1..4`.
- Check left self-distributivity exactly on every ordered triple.
- For every rack and every nonempty seed subset, run the closure reconstruction whenever the
  subset forward-generates the carrier.
- **PASS** only if all eligible reconstructions equal the full table, every derived-row collision
  agrees, and observed oracle calls equal `|S|*n`.
- Independently check the theorem on deterministic dihedral and conjugation-rack families using a
  separately written evaluator.

## Strongest alternative explanation

The apparent saving may be an artifact of selected faithful/connected quandles, a composition-
orientation mistake, or a hidden dependence on knowing unqueried rows. Exhausting all small
permutation-row operations and all generating subsets directly tests those alternatives.

## Claim boundary

The theorem is conditional on a valid rack promise and a seed set whose forward operation closure
is the full carrier. It does **not** cheaply certify that an arbitrary black-box operation is a rack,
and it does not improve the prior worst-case lower bound without this algebraic promise.

## Project-relevance threshold

The result counts only if implemented as a fail-closed THEORICA capability that either returns an
exact reconstructed table with a derivation certificate or abstains because the seeds do not close
the carrier / the queried rows contradict the identity.

## Kill condition

Kill or narrow the kernel if any valid rack with a forward-generating seed set produces an
incorrect or derivation-dependent reconstruction, or if the implementation needs any unqueried
oracle cells beyond the seed rows.
