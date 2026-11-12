# Three-level monotonicity correction and retraction

## Decisive theorem

Let `U_q(a,b,c)` be the unrestricted minimax query cost and let
`R_q(a,b,c)` be the exact cost of the root-respecting policy class. Because
every root-respecting policy is an unrestricted policy,

```text
U_q(a,b,c) <= R_q(a,b,c).
```

The proved root-respecting recurrence gives

```text
R_q(a,b,c) = max(
    2a + 2b + 4c,
    2a + 3b + 3c,
    2a + 4b + c,
    3a + 2b + 3c,
    3a + 3b + c,
    4a + b + c,
).
```

The former seven-face claim added `B(a,b,c)=4b+2c` as an unrestricted
adversarial lower bound. Direct comparison shows

```text
B > R_q  iff  c > 2a and b > 2a+c.
```

Necessity follows by comparing `B` with the faces `(2,4,1)` and `(2,3,3)`.
Conversely, those two strict inequalities imply that `B` exceeds every one of
the six faces. Thus, throughout this cone and for every arity `q >= 2`, `B`
exceeds the cost of an executable policy. It is therefore impossible as a
lower bound. This retracts the published seven-face unrestricted theorem.

The production certificate now exposes only the six root-respecting faces and
labels its policy class explicitly. A separate monotonicity certificate
computes the retired face, both cone margins, and the impossibility verdict.

## Prospective falsification

The protocol was frozen before opening six binary cases in the violation cone.
Every exact unrestricted solve returned the six-face value and strictly
falsified the retired seven-face prediction:

| Costs `(a,b,c)` | Exact unrestricted | Six-face | Retired seven-face |
|---|---:|---:|---:|
| `(1,20,3)` | 85 | 85 | 86 |
| `(1,7,3)` | 33 | 33 | 34 |
| `(2,17,5)` | 77 | 77 | 78 |
| `(3,25,7)` | 113 | 113 | 114 |
| `(1,6,3)` | 29 | 29 | 30 |
| `(2,14,5)` | 65 | 65 | 66 |

The exact unrestricted binary solver also matched the six-face value on all
216 cost triples in `{1,...,6}^3` (2,365,309 cost-bounded states in total).
The analytic cone classification matched direct face comparison in 216/216
cases. Removing a necessary physical query copy still caused conservative
abstention rather than a false certificate.

## Independent audit

A standard-library-only implementation with zero THEORICA imports reproduced
all six prospective optima. Its query semantics deliberately preserve the
production collision between the outside-subtree response and raw symbol
zero; an earlier offset-symbol audit was rejected because it changed the
experiment rather than independently reproducing it.

## Reproduction

```bash
python scripts/verify_qary_three_level_monotonicity_correction.py
python scripts/audit_qary_three_level_monotonicity_correction.py
pytest -q tests/test_corruption_resilient_features.py
```

Deterministic evidence is stored under
`results/qary_three_level_monotonicity_correction/`. The exhaustive record
digest is
`f8e26029a92858b729790a054261f58b4d4f0a34dd5ff1c090ed39296bd82d3`.

## Bounded conclusion and limitations

The general result is the monotonicity veto: the retired face is impossible
on the stated cone for every arity. Exact unrestricted binary searches support
the six-face replacement on 240 tested cost triples (216 exhaustive-grid
cases plus twenty-four prospective holdouts). Six holdouts uniquely
activate every surviving face at 40:1-scale ratios, including phase margins
of one and two; a further twelve conditioned rays found root-first exact and
both descendant-first levels strictly worse. See
`QARY_THREE_LEVEL_FACE_COVERAGE_RESULT.md` and
`QARY_THREE_LEVEL_ANCESTOR_BYPASS_RESULT.md`. Independent implementations
replayed every prospective suite. This finite evidence does
**not** by itself prove the six-face law
for every positive binary cost triple, for arity greater than two, at greater
depth, with other fault budgets, or with fewer physical copies. Those remain
open until a complete exchange proof or a stronger exhaustive certificate is
provided.
