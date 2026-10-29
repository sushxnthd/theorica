# Binary middle-first six-face profile

## Outcome

The prospectively frozen candidate passed every acceptance criterion. For a
binary three-level prefix-query problem with positive integer level costs
`(a,b,c)`, all twelve unseen exact searches conditioned on a middle-level
first query agreed with

```text
M(a,b,c) = max(
    a + 5b + c,
    2a + 3b + 4c,
    2a + 4b + 3c,
    3a + 3b + 3c,
    3a + 4b + c,
    4a + 2b + c,
).
```

This remains a finite, prospectively supported candidate law rather than a
universal theorem.

## Prospective evidence

The protocol was committed before any holdout optimum was opened. Six 79:1
scale rays uniquely activated the six proposed faces:

| Costs `(a,b,c)` | Exact cost | Unique active face | Winning margin |
|---|---:|---|---:|
| `(1,79,1)` | 397 | `(1,5,1)` | 76 |
| `(1,1,79)` | 321 | `(2,3,4)` | 78 |
| `(1,79,53)` | 477 | `(2,4,3)` | 26 |
| `(79,1,53)` | 399 | `(3,3,3)` | 26 |
| `(79,79,1)` | 554 | `(3,4,1)` | 77 |
| `(79,1,1)` | 319 | `(4,2,1)` | 76 |

Six additional rays tested predicted phase boundaries. Every case retained
its predicted unique face and exact value with a winning margin of one:

| Costs `(a,b,c)` | Exact cost | Unique active face |
|---|---:|---|
| `(59,30,1)` | 298 | `(3,4,1)` |
| `(59,29,1)` | 295 | `(4,2,1)` |
| `(59,1,58)` | 354 | `(3,3,3)` |
| `(58,1,59)` | 355 | `(2,3,4)` |
| `(29,59,1)` | 325 | `(1,5,1)` |
| `(1,59,58)` | 412 | `(2,4,3)` |

The candidate had been inferred from 76 opened cases: the complete
`{1,...,4}^3` grid and twelve earlier high-ratio rays. The prospective suite
therefore raises exact middle-first agreement to 88 distinct cost triples.

## Independent verification

A separate standard-library dynamic program rebuilt the grouped binary
prefix-query problem and reproduced all twelve conditioned optima. It imports
no `theorica` module and does not consume production search states. A
deterministic rerun produced byte-identical primary and audit artifacts.

## Executable capability

`certify_binary_three_level_middle_first` evaluates all six affine faces,
returns every active face, and labels its scope as `binary_middle_first`.
Boolean, non-integral, zero, and negative costs fail closed. The production
verifier separately checks the certificate against exact conditioned search.

## Preserved negative result

The analogous leaf-first profile did not collapse to a single max of integer
affine faces on the opened grid and high-ratio evidence. The candidate convex
envelope missed 16 opened cases. Consequently this work makes no leaf-first
closed-form claim; that route is falsified in its present form and requires a
different representation or state decomposition.

The subsequent symbolic proof attempt also falsified a stronger-looking but
incorrect lower-bound route. Five faces are componentwise unavoidable
transcript exposures, but `(3,4,1)` is not. A valid avoidance tree instead
realizes the tradeoff pair `(2,5,1)` and `(4,3,1)`, whose midpoint is the
missing face. See `QARY_THREE_LEVEL_MIDDLE_FIRST_PROOF_RESULT.md`. The next
kernel therefore uses convex-hull exposure menus rather than scalar transcript
witnesses.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_three_level_middle_first.py
python scripts/audit_qary_three_level_middle_first.py
pytest -q
```

Machine-readable primary and independent evidence is stored under
`results/qary_three_level_middle_first/`.

## Claim boundary

The evidence establishes exact prospective agreement on a deliberately
adversarial finite suite, including all six proposed faces and six margin-one
boundaries. It does not prove the formula for every positive cost triple,
derive the required exchange lemma, solve the leaf-first profile, or extend to
larger arity, greater depth, another fault budget, or reduced query
multiplicity.
