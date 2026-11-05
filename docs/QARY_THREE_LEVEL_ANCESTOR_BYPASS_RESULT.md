# Conditioned ancestor-bypass profile

## Outcome

The frozen experiment passed without a strict ancestor-bypass counterexample.
On all twelve unseen primitive binary cost rays, the unrestricted optimum
equaled both the corrected six-face prediction and the exact optimum
conditioned on querying the root first.

More strongly, every descendant-first restriction was strictly worse. No
middle-first or leaf-first optimal tie occurred.

| Costs `(a,b,c)` | Unrestricted | Root first | Middle first | Leaf first |
|---|---:|---:|---:|---:|
| `(1,1,97)` | 392 | 392 | 393 | 489 |
| `(1,97,49)` | 440 | 440 | 537 | 489 |
| `(1,97,1)` | 391 | 391 | 487 | 392 |
| `(97,1,48)` | 437 | 437 | 438 | 485 |
| `(97,49,1)` | 439 | 439 | 488 | 440 |
| `(97,1,1)` | 390 | 390 | 391 | 391 |
| `(7,31,53)` | 288 | 288 | 319 | 341 |
| `(53,31,7)` | 259 | 259 | 290 | 266 |
| `(11,47,29)` | 250 | 250 | 297 | 279 |
| `(47,11,29)` | 250 | 250 | 261 | 279 |
| `(29,47,11)` | 257 | 257 | 286 | 268 |
| `(29,11,47)` | 268 | 268 | 279 | 308 |

The forced middle-first penalty ranged from 1 to 97 cost units. The forced
leaf-first penalty ranged from 1 to 97. Thus the absence of bypass was not an
artifact of the solver returning a root-first representative from a tied set:
the exact conditioned values separate every descendant-first action on this
suite.

## Executable capability

The production weighted-fault solver now accepts an optional validated set of
permitted initial physical query indices. The restriction applies only to the
initial state; every later action remains unrestricted. This turns a scalar
optimum checker into an exact mechanism probe that can distinguish:

1. strict ancestor bypass (`unrestricted < root-first`);
2. a non-root-first optimal tie; and
3. strict first-action root dominance.

Empty, duplicate, Boolean, non-integer, and out-of-range restrictions fail
closed. Default behavior remains unrestricted.

## Independent audit and adversarial control

A separate standard-library dynamic program reproduced all 48 conditioned
optima with zero `theorica` imports. It builds the raw grouped prefix-query
problem independently and does not read production search states.

Deleting a required physical query copy from the `(97,1,48)` instance still
caused conservative abstention rather than a finite certificate.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_three_level_ancestor_bypass.py
python scripts/audit_qary_three_level_ancestor_bypass.py
pytest -q
```

Machine-readable primary and independent evidence is stored under
`results/qary_three_level_ancestor_bypass/`.

## Bounded conclusion

The corrected six-face expression now agrees with unrestricted exact binary
search on 240 cost triples. The twelve newest instances add a stronger fact
than scalar agreement: root-first conditioning is exact, while both possible
descendant levels are strictly suboptimal as first actions.

This remains finite evidence, not a universal exchange theorem. The experiment
does not exclude bypass at another positive cost ray and does not prove results
for larger arities, greater depths, different fault budgets, or reduced query
multiplicity. The next mathematical target is a symbolic first-query exchange
lemma explaining the observed strict dominance.

## Subsequent conditioned-law evidence

The next prospectively frozen experiment isolated the middle-first branch.
Its six-face max-plus candidate matched twelve unseen exact optima, including
one unique activator for every face and six predicted margin-one boundaries;
an independent zero-import solver reproduced all twelve. See
`QARY_THREE_LEVEL_MIDDLE_FIRST_RESULT.md`. This sharpens the numerical
first-action profile but still does not supply the universal exchange lemma.
