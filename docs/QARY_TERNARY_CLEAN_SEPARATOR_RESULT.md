# Clean-separator residual law: one prospective exact success

## Result

The frozen one-case prediction in
`docs/QARY_TERNARY_CLEAN_SEPARATOR_PROTOCOL.md` passed.  For the reserved P2
family at level costs `(3,10,3)`, the exact residual value at the preregistered
post-erasure state is 30, matching the prediction `3*b`.

The smallest observed structural mechanism is a clean middle separator.  Query
group 3 has three response cells: all eight one-lie cube completions, the first
zero-lie added completion, and the second zero-lie added completion.  Thus its
two fragile candidates are separated without sharing a cell with any candidate
that has already consumed its lie budget.

The exhaustive Bellman calculation proves a lower bound of 30 and constructs
an action attaining 30.  Its optimal first continuation costs 10 and has child
values 16, 20, and 20.  The search evaluated 3,291 actions over 4,537 value
states and 115 compatibility states.  The discovery-ray regression remains 27.

An independent, non-importing audit recomputed the separator predicate from
the emitted cells, checked `3*10=30`, checked exact lower/upper agreement, and
verified that exactly one reserved case was opened.

## Executable consequence

At this state, the planner can detect a clean separator directly from the
partition of zero-lie and one-lie candidates.  When it exists in P2, the
preregistered continuation policy begins with that middle query and attains
the sharp residual boundary 30.  This is a state-local policy-selection rule,
not merely a family label.

## Scope and limitations

This is one prospective family/cost case, not a universal theorem over all
cost rays or all ternary families.  It establishes the P2 branch of the
candidate law at `(3,10,3)` and explains the earlier 27/29 split.  It does not
yet prove the complementary `a+3*b` branch for a new P0/P1 holdout, nor prove
that clean separation is necessary outside this fixed post-erasure state.
Seventeen reserved family/cost cases remain sealed.

## Reproduction

```bash
PYTHONPATH=src python scripts/verify_qary_ternary_clean_separator.py
PYTHONPATH=src python scripts/audit_qary_ternary_clean_separator.py
```

The deterministic artifacts are
`results/qary_ternary_clean_separator/results.json` and
`results/qary_ternary_clean_separator/audit.json`.
