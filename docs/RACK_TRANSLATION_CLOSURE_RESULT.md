# Rack-generated closure eliminates per-row completeness probes

**Classification:** EXACT CONDITIONAL THEOREM / SYSTEM CAPABILITY  
**Status:** PASS  
**Breakthrough gate:** INCONCLUSIVE pending expert priority review

## Smallest supported claim

Let `(X, *)` be a finite left rack of order `n`, with left translation
`L_x(y) = x * y`. If a seed set `S` forward-generates `X` under `*`, then the complete
operation table is determined by querying only the `|S|` seed rows: exactly `|S|*n`
oracle cells. A deterministic closure algorithm reconstructs every other row and records
a derivation certificate.

This replaces THEORICA's general exact completeness cost
`|S|*n + (n-|S|)*(n-1)` with `|S|*n` **under the certified rack and generation promises**.

## Proof

Left self-distributivity states `x * (y * z) = (x * y) * (x * z)`.
Since every `L_x` is a permutation, this is equivalent to
`L_(x*y) = L_x L_y L_x^-1`.

Query every row indexed by `S`. Whenever rows `L_x` and `L_y` are known, the carrier
index `x*y = L_x(y)` and the full row at that index are therefore known, without another
oracle call. Induction over the forward-operation closure of `S` determines every row
when that closure is `X`. Each seed row costs `n` distinct cells, giving `|S|*n` total.
The implementation checks that alternative derivations of one row agree.

## Decisive evidence

| Evidence | Scope | Result |
|---|---:|---:|
| Permutation-row operations exhausted | orders 1–4 | 331,997 |
| Labeled racks / quandles | orders 1–4 | 130 / 43 |
| Generating seed subsets reconstructed | all eligible | 773 / 773 |
| Rack counterexamples | exact search | 0 |
| Independent Alexander-quandle families | moduli 2–32 | 323 |
| Independent generating cases | deterministic seed corpus | 3,741 / 3,741 |
| Independently derived rows / conflicts | all cases | 72,389 / 0 |

Primary canonical SHA-256:
`31c29e5ac8d8dbdef0a786ad021afa0f829e49f2ea023a96a3371cc0a5806694`

Independent-audit canonical SHA-256:
`1f0af3b7da8b4eccb756d9d8df69d70f74a755757e4e9c80657b6b11830ecf68`

## Adversarial falsification and boundary

- Predicting `L_(x*y)=L_y` instead of conjugating fails at order 3.
- Reversing the conjugation order fails at order 4.
- A minimal order-2 non-rack is incorrectly reconstructed when the rack promise is
  omitted. The method cannot certify its own algebraic promise from seed rows alone.
- A non-generating seed set causes deterministic abstention after exactly `|S|*n` calls.
- The theorem says nothing about the minimum number of seed rows needed for a given rack.

## Prior-art boundary

The rack axioms, the fact that left translations are automorphisms, translation groups,
and the conjugation identity are classical. Subrack generation is also established theory.
The contribution supported here is the exact black-box query consequence and its fail-closed
THEORICA implementation—not a claim to have discovered the rack identity. A targeted search
did not locate this exact `|S|*n` reconstruction/certificate formulation, but historical
novelty remains unverified.

- D. Stanovský, *Quandles: from knots to transitive groups* (2013):
  https://www.karlin.mff.cuni.cz/~stanovsk/math/slides_olomouc_quandles.pdf
- S. Kayacan, *Subrack Lattices of Conjugation Racks* (2024):
  https://arxiv.org/abs/2410.04127

## SCIENCE ledger

- **KNOWN:** certified rack structure plus forward generation collapses exact reconstruction
  to the queried seed rows, `|S|*n` cells.
- **KNOWN:** all 773 exhaustive eligible cases through order 4 and 3,741 independent
  Alexander-quandle cases reconstruct exactly.
- **FALSIFIED:** the saving holds without a rack promise; an order-2 counterexample refutes it.
- **ANOMALOUS:** a classical structural identity completely removes the per-untrusted-row
  completeness burden once algebraic generation replaces translation-group generation.
- **BELIEVED:** small operation-generating sets can materially outperform translation-group
  generators followed by black-box completeness certification.
- **UNTESTED:** sharp minimum seed-query complexity and adaptive seed acquisition.

## CONSEQUENCE ledger

- THEORICA now has an exact certified-rack path: query full rows only for an operation-
  generating set, derive the remainder, and emit derivation triples.
- The runtime must distinguish operation generation from translation-group generation.
- The generic near-quadratic certificate remains mandatory when rack structure is not certified.
- The next decisive kernel is adaptive discovery of a small operation-generating seed set with
  a checkable external rack certificate; absent that certificate, the system must abstain.

## Reproduction

```bash
pip install -e '.[dev]'
pytest -q tests/test_rack_translation_closure.py
python scripts/verify_rack_translation_closure.py --max-n 4 --output /tmp/rack-primary.json
python scripts/audit_rack_translation_closure.py --max-modulus 32 --output /tmp/rack-audit.json
```
