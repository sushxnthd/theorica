# Prospective coverage of all six corrected binary faces

## Outcome

The frozen experiment passed. Each of the six surviving root-respecting
coefficient vectors was the unique maximizer on one previously unopened
40:1-scale cost triple, and the unrestricted exact binary solver matched that
prediction in all 6/6 cases.

| Costs `(a,b,c)` | Unique active face | Exact unrestricted | Six-face prediction | Margin |
|---|---|---:|---:|---:|
| `(1,1,40)` | `(2,2,4)` | 164 | 164 | 39 |
| `(1,40,21)` | `(2,3,3)` | 185 | 185 | 2 |
| `(1,40,1)` | `(2,4,1)` | 163 | 163 | 38 |
| `(40,1,20)` | `(3,2,3)` | 182 | 182 | 1 |
| `(40,21,1)` | `(3,3,1)` | 184 | 184 | 2 |
| `(40,1,1)` | `(4,1,1)` | 162 | 162 | 37 |

The two narrowest cases had margins one and two over the next six-face
competitor. They therefore probe phase transitions rather than only interiors
of broad cones. Across the six searches, the production solver evaluated
279,426 cost-bounded states and 347 compatibility states.

## Independent check and adversarial control

A separate standard-library dynamic program reproduced all six unrestricted
optima with zero `theorica` imports. It constructs the raw prefix-query problem
directly and does not read the production solver's search results.

As a fail-closed control, one required physical query copy was removed from
the `(40,1,20)` instance. The production solver abstained instead of returning
a finite certificate. This preserves the kernel's no-false-pass behavior under
an incomplete action set.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_three_level_face_coverage.py
python scripts/audit_qary_three_level_face_coverage.py
pytest -q
```

Machine-readable primary and independent records are stored under
`results/qary_three_level_face_coverage/`.

## Bounded conclusion

The corrected six-face expression now agrees with exact unrestricted binary
search on 240 cost triples: the prior exhaustive `{1,...,6}^3` box, six
prospective counterexamples to the retired seventh face, and these six
prospective face-coverage holdouts, followed by twelve conditioned
ancestor-bypass rays. Every surviving face has exact evidence at a 40:1 cost
ratio, including near-boundary margins of one and two. The later conditioned
suite found root-first exact and both descendant-first levels strictly worse
on all twelve rays; see `QARY_THREE_LEVEL_ANCESTOR_BYPASS_RESULT.md`.

This is stronger falsification evidence, not a universal theorem. Finite
binary searches do not exclude an ancestor-bypass counterexample elsewhere
in the positive cost lattice, and they do not establish the law for larger
arities, greater depths, different fault budgets, or reduced query
multiplicity. A complete unrestricted lower-bound or exchange proof remains
open.
