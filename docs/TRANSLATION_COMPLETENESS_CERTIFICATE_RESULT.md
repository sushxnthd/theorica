# Translation-group completeness certification is worst-case near-quadratic

**Classification:** EXACT THEOREM / SYSTEM IMPOSSIBILITY BOUNDARY  
**Status:** PASS  
**Breakthrough gate:** INCONCLUSIVE pending expert priority review

## Smallest supported claim

Let an unknown `n x n` operation table have permutation rows. Suppose `r` fully queried rows generate a candidate subgroup `H <= Sym(n)`. Without any additional algebraic promise, the exact worst-case number of distinct oracle values required to certify that every remaining row belongs to `H` is

```
r*n + (n-r)*(n-1).
```

The bound is both necessary and sufficient. Therefore the externally supplied generator-completeness certificate used by THEORICA's fast reconstruction path cannot, in general, be replaced by a similarly cheap zero-error learner: automatic certification collapses the query saving to at most one cell per untrusted row.

## Proof

### Sufficiency

Query the `r` trusted generator rows completely and construct `H`. For every other row, query any `n-1` coordinates. Because the row is promised to be a permutation, the only output value not yet observed is forced at the last coordinate. The entire row is now known and exact membership in `H` is decidable. The query count is `r*n+(n-r)(n-1)`.

### Necessity

Take `H={id}` and an operation whose rows are all the identity permutation. Consider any zero-error adaptive learner. If it stops while some untrusted row has two unqueried coordinates `a,b`, replace that row by the transposition `(a b)`. The modified row is a permutation outside `H`, but every answer already observed by the learner is unchanged. Thus the same transcript is consistent with both a complete and an incomplete generated group, so the learner cannot certify correctly. It must query at least `n-1` entries of every untrusted row. Adding the `r*n` trusted-row queries proves the lower bound.

The argument also applies to zero-error randomized learners after fixing their internal randomness.

## Exact evidence

The primary verifier exhausted every permutation and every queried-coordinate subset through order 8.

| Check | Result |
|---|---:|
| Orders exhausted | 2–8 |
| Permutations enumerated across orders | 46,212 |
| Coordinate subsets of size at most `n-2` | 466 |
| Outside permutations matching those transcripts | 125,162 |
| Ambiguity failures | **0** |
| `n-1`-coordinate uniqueness failures | **0** |

An independently written constructive checker verified the transposition adversary and forced-last-image argument in 133,141 cases through order 64 with zero failures. The production certificate tests passed, and the complete repository CI passed.

- Primary canonical SHA-256: `955f18f38a8de6af6a39438aad0b250105c7d8b692a42756e2405082922d5e92`
- Independent-audit SHA-256: `97865be69d736ebaf0bb0abf74e8622d67f004cb0795307412d71a931c90c293`
- Workflow artifact digest: `sha256:0ceed7eda450bd8912f340ab4c4682495bd2e22c36fa4549008c72925d35a5b2`

## SCIENCE ledger

- **KNOWN:** `n-1` point images are necessary and sufficient to certify membership of an arbitrary untrusted permutation in the worst case.
- **KNOWN:** the exact whole-table certificate cost is `r*n+(n-r)(n-1)`.
- **FALSIFIED:** automatic zero-error generator-completeness certification generally preserves the linear-query advantage of base-signature reconstruction.
- **ANOMALOUS:** one missing answer per row is harmless because permutation bijectivity forces it; two missing answers permit an indistinguishable outside transposition.
- **BELIEVED:** meaningful subquadratic automatic certification requires additional identities, a restricted row family, probabilistic error, or an external certificate.
- **UNTESTED:** the sharp bounds under rack, quandle, group, loop, or other family-specific identities.

## CONSEQUENCE ledger

- THEORICA now has an executable fail-closed exact certificate path for arbitrary permutation-row operations.
- The fast `r*n+(n-r)b` reconstruction path must continue to require a supplied completeness certificate; silently inferring completeness from base signatures would be unsound.
- The discovery learner should preserve its abstention/validation behavior unless it can establish stronger family-specific structure.
- The next active research kernel becomes family-specific certificate compression: determine whether rack/quandle identities reduce the `n-1` per-row barrier while retaining zero false acceptance.

## Prior-art boundary

Permutation-group bases, strong generating sets, and membership testing are classical, and modern query-complexity work explicitly connects a group's minimal base size to identifying a known group element. The present result concerns a different promise gap: certifying that an unknown permutation belongs to the discovered group at all. A targeted search did not identify this exact operation-learning statement, but no historical-first claim is made without expert review.

## Reproduction

```bash
python scripts/verify_translation_completeness_certificate.py \
  --max-n 8 --output /tmp/translation-completeness-boundary.json
python scripts/audit_translation_completeness_certificate.py \
  --max-n 64 --output /tmp/translation-completeness-audit.json
pytest -q tests/test_translation_certificate.py
```
