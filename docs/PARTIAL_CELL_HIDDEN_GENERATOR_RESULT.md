# Exact partial-cell hidden-generator boundary

**Date:** 16 October 2026  
**Branch:** `breakthrough-engine/nonfaithful-reconstruction-boundary-20261013`  
**Frozen protocol:** `1bce1288ad1b4d59c96d3d363c12b1f42dd91249`  
**Verified implementation:** `6ea486b30ab2717d98b5165b987aa1a3bef07e61`  
**Workflow:** [partial-cell-hidden-generator run 38876052583](https://github.com/sushxnthd/theorica/actions/runs/38876052583) — PASS  
**Artifact:** `partial-cell-hidden-generator`, ID `12035885231`, digest `sha256:d480fa47a6795a1d26ea6df28d87ccf279fd1fa493c0a008d6c06c8f3853c925`

## Smallest supported claim

For the externally certified family (R(n,z,\sigma)), (n\ge3), in which every
left translation except (L_z) is the identity and (L_z) fixes (z) while
acting as a full cycle on (X\setminus\{z\}), the deterministic zero-error
cell-query complexity of locating (z), and therefore returning a
two-element operation-generating seed, is exactly

[
D_0(R_n)=n-1.
]

A fixed scan order has uniform-hidden-label expected cost

[
\mathbb E[Q]=\frac{n+1}{2}-\frac1n.
]

This yields an exact oracle-interface separation on this promised family:
complete-row acquisition can consume (n^2) cells, whereas partial-cell seed
localization needs exactly (n-1) cells in the worst case.

Historical novelty is **not** asserted. The mathematical lower bound is an
instance of deterministic unique-marked-item search; the project result is the
proved rack-family reduction and the resulting fail-closed THEORICA interface.

## Proof

### Upper bound

Probe one off-diagonal cell in each of (n-1) candidate rows. In every identity
row the reply equals the queried column. In row (z), every off-diagonal
element lies in the full cycle on (X\setminus\{z\}), so it is not fixed and
the reply differs from the queried column. A nonidentity reply identifies
(z); if all (n-1) replies are identity, the omitted row is (z).

For any (a\ne z), closure of ({z,a}) contains the full
(sigma)-orbit of (a), hence all of (X\setminus\{z\}), and therefore
all of (X).

### Lower bound

Consider the all-identity transcript after (q<n-1) off-diagonal cell queries.
At most (q) distinct row labels have been probed, so at least two labels
(z_1,z_2) remain unprobed. For either choice (z=z_i), select any full cycle
on (X\setminus\{z_i\}). Both resulting family members agree with the whole
transcript, but require different distinguished rows. Hence no deterministic
zero-error algorithm can identify (z) with fewer than (n-1) queries.

### Expected cost

For hidden positions (1,ldots,n-1), costs are (1,ldots,n-1); the omitted
last position also costs (n-1). Thus

[
\frac{1+\cdots+(n-1)+(n-1)}{n}
=\frac{n+1}{2}-\frac1n.
]

## Exact evidence

The primary verifier and separately written audit import no code from one
another.

| Gate | Result |
|---|---:|
| Family members checked, (3\le n\le64), two cycle orientations | 4,154 |
| Explicit cubic rack-identity checks, (3\le n\le12) | 150 |
| Two-element generating-seed checks | 174,716 |
| Partial-cell scan cases | 4,154 |
| Lower-bound ambiguity witnesses | 2,015 |
| Exact rational expectation checks | 62 |
| Independent audit checks | 4,092 |
| Failures | 0 |

Primary result:

- canonical payload: `24f0d756e20c363a3476ebab815a2b4aa819c6e3918fc5254a27acb73e825e03`
- file SHA-256: `4a48fbd0f6c974db56ee80f1a426777ebf31f02deedfccfc182b5284f3f46c23`

Independent audit:

- canonical payload: `cd20d71c6f8c46202363e8e54583def40b2e67c34f00c9c3f62e3e2c3edcce43`
- file SHA-256: `301d052183c5fbb0a85af1777f6630d221a21de35dadf8d0e3fb30c5214b6790`

The workflow also reran both verifiers and byte-compared their outputs. Runtime
tests exhaust every hidden row for (3\le n\le32), attain the (n-1) bound,
verify returned seed closure, reject uncertified inputs without an oracle call,
and reject out-of-range oracle values.

## Infrastructure failure preserved

Earlier workflows `38875673595` and `38875933777` used a generic repeated
binary-operation closure inside 174,716 seed checks and remained stuck in the
primary verifier. No scientific failure was observed; the implementation was
replaced, in follow-up commit `6ea486b`, by the exact orbit-closure algorithm
valid for the one-active-translation family. The successful workflow preserves
the same frozen hypothesis and gates.

## Priority audit

The audit found adjacent but not identical prior work:

- Blackburn, *Enumerating finite racks, quandles and kei* (2013), develops the
  operator-group/permutation view of finite racks:
  https://arxiv.org/abs/1203.6504
- Lopes and Roseman, *On Finite Racks and Quandles* (2006), studies finite racks
  through their translation permutations:
  https://arxiv.org/abs/math/0412487
- Janota, Araújo, and Vojtěchovský, *Computing Generating Sets of Minimal Size
  in Finite Algebras* (2022), treats minimal generating sets from an explicitly
  available operation:
  https://www.cs.du.edu/~petr/data/papers/computing_generating_sets_of_minimal_size_in_finite_algebras.pdf
- Standard deterministic decision-tree search already implies the generic
  marked-item lower-bound pattern.

No located source states this promised rack-family cell-query theorem or its
THEORICA acquisition consequence. Because the lower-bound core is elementary
and generic, this report does not claim a new field-level query-complexity
theorem. Its defensible contribution is a precise interface boundary, exact
family reduction, independent verification, and deployed reasoning primitive.

## SCIENCE ledger

- **True:** the exact deterministic zero-error bound is (n-1), with the stated
  exact expected cost.
- **Survived alternatives:** all constructed members are racks; rank is exactly
  two; no off-diagonal probe of the active row is falsely identity; every
  returned pair generates; the ambiguity witness survives adaptivity.
- **Not established:** noisy-oracle bounds, randomized complexity, unknown
  family membership, arbitrary-rack acquisition, or historical novelty.

## CONSEQUENCE ledger

THEORICA now exposes
`locate_hidden_generator_by_cells(..., family_certified=True)`.

- It uses at most (n-1) cell calls rather than requesting (n) complete rows.
- It returns the distinguished row and a verified-by-theorem two-row seed.
- It refuses uncertified family use with zero oracle calls.
- The previous complete-row planner remains the general fail-closed fallback.

This changes the reasoning capability from “acquire full rows until closure” to
“select an oracle interface from a certified structural hypothesis.” The
separation therefore alters both benchmark design and runtime query planning.

## Claim boundary

Do not generalize this result to arbitrary racks, uncertified inputs, noisy
answers, randomized algorithms, or full-table reconstruction. A family
certificate is part of the input contract, not inferred from the same private
cell transcript.
