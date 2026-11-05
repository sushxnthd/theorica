# Frozen protocol: binary three-level face coverage

Status: frozen before opening any exact solve below.

## Question

The corrected binary conjecture predicts that unrestricted minimax cost equals
the maximum of the six proved root-respecting faces. Prior evidence covered a
dense low-cost box and the cone that falsified the retired seventh face, but it
did not prospectively activate every surviving face at large cost ratios.

Do all six faces survive unrestricted ancestor bypass on unseen 40:1-scale
costs, including the narrow transition cones where the predicted winning face
beats its nearest competitor by only one or two units?

## Frozen holdouts

Each cost triple uniquely activates the listed coefficient vector:

| Costs `(a,b,c)` | Predicted face | Predicted cost | Margin |
|---|---|---:|---:|
| `(1,1,40)` | `(2,2,4)` | 164 | 39 |
| `(1,40,21)` | `(2,3,3)` | 185 | 2 |
| `(1,40,1)` | `(2,4,1)` | 163 | 38 |
| `(40,1,20)` | `(3,2,3)` | 182 | 1 |
| `(40,21,1)` | `(3,3,1)` | 184 | 2 |
| `(40,1,1)` | `(4,1,1)` | 162 | 37 |

The margins are the gaps to the second-largest six-face prediction and were
computed before exact unrestricted search.

## Acceptance criteria

1. All 6/6 exact unrestricted binary optima equal the frozen six-face values.
2. Every one of the six faces is uniquely active in one holdout.
3. A standard-library-only solver with zero THEORICA imports reproduces all
   six optima from the raw prefix-query problem rather than reading predictions.
4. A necessary-copy deletion still causes conservative abstention.
5. Primary and independent evidence is deterministic; full tests, scoped Ruff,
   diff checks, and hosted workflows pass.

## Kill criteria

- any holdout optimum is below its six-face prediction, demonstrating an
  unrestricted ancestor-bypass improvement;
- any holdout optimum exceeds the feasible root-respecting prediction;
- either implementation disagrees; or
- a missing-copy instance receives a finite certificate.

## Claim boundary

Passing establishes prospective exact coverage of every surviving face at
large ratios and narrow phase boundaries. It does not turn six finite cases,
or the preceding 216-case box, into a universal proof over all positive costs,
larger arities, greater depths, or different fault budgets.
