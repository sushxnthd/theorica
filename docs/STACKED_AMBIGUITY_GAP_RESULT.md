# Stacked ambiguity-gap result

## Exact law

Let each feasible completion `theta` be a finite robust game with the same `a`
actions and exact value `v_theta`. When all values agree at `v`, concatenate all
scenario columns across completions into a single stacked game with value
`v_stack`. Then

`v_stack <= v`, and a common exact robust policy exists if and only if
`v_stack = v`.

The exact scalar

`Delta = v - v_stack`

is therefore zero exactly when model ambiguity is decision-irrelevant. A
positive gap measures the robust-value loss forced by requiring one policy to
work across every transcript-consistent completion.

If `Delta > 0`, at most `a` individual scenario columns already force a value
below `v`. This is stronger than returning whole-completion indices: the
certificate identifies the exact scenario constraints that make a common
decision impossible. The bound is sharp.

## Proof

Every policy feasible for the stacked game is evaluated against every scenario
of every completion, so its stacked payoff cannot exceed any individual robust
value. If `v_stack = v`, a stacked-optimal policy earns at least `v` in each
completion and is therefore optimal in every one. Conversely, a common optimal
policy earns `v` against every stacked column, proving `v_stack >= v` and hence
equality.

For a strict gap, intersect the action simplex with the halfspace induced by
each scenario column at threshold `v`. The full intersection is empty. Helly's
theorem in affine dimension `a-1` supplies an empty subintersection of at most
`a` such halfspaces, which is exactly a scenario-level game with value below
`v`.

Sharpness uses `a` one-scenario completions. Completion `i` pays `-1` on action
`i` and `0` on every other action. Each completion has value zero; every proper
subfamily has a common pure action; all `a` columns together have value `-1/a`.
Thus `Delta = 1/a` and every scenario column is necessary.

## Frozen evidence

| Gate | Result |
|---|---:|
| Opened corrupted-query zero-gap cases | 40 / 40 |
| Prospective reciprocal-feature zero-gap cases | 20 / 20 |
| Existing three/four-action positive-gap attacks | 20 / 20 |
| Prospective five-action sharp witnesses | 10 / 10 |
| Unequal-value cases correctly abstained | 20 / 20 |
| Independent positive cases | 60 / 60 |
| Independent sharp witnesses | 30 / 30 |
| Independent production imports | 0 |
| Primary digest | `58be3839bff6c97790664f9233c03f27c3b5f5b957d21959e5a0b152cab33659` |
| Independent digest | `62241bb35199b16c0b6e6cc206fc162ac63b72edffcaa7839f728b78eff33d04` |

The ten frozen five-action cases returned exact stacked value `-1/5`, gap
`1/5`, and a minimal five-column witness while every proper subfamily retained
zero gap. All prior model-ambiguous positive transcripts retained exact zero
gap and their common policy.

## Executable consequence

THEORICA now emits an exact decision-ambiguity margin alongside every
multi-action completion certificate. A zero gap returns the stacked game's
policy and replays it against every completion. A positive gap returns at most
`a` labelled `(completion, scenario)` constraints that independently justify
abstention. Unequal individual values remain a separate, earlier failure mode.

## Novelty boundary and limitations

Finite minimax duality, robust optimization over a union of scenario sets,
convex policy sets, and Helly's theorem are classical. The bounded contribution
is their exact composition with THEORICA's corrupted algebraic version space:
one scalar quantifies whether ambiguity changes the decision, and a sharp
scenario-level certificate explains why.

This result covers finite exact rational games only. It does not cover floating
point tolerances, approximate equality, continuous actions, infinite completion
families, uncertain feature maps, or stochastic corruption.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_stacked_ambiguity_gap.py
python scripts/audit_stacked_ambiguity_gap.py
pytest -q
```

The frozen branch passed all 175 tests and scoped Ruff checks on every changed
Python file. Repository-wide Ruff remains non-gating because the inherited tree
contains 258 pre-existing findings outside this kernel; none is introduced by
the changed files.
