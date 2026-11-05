# Finite-list error-erasure selector protocol

Status: frozen before adversarial execution.

## Question

Which queried feature geometries guarantee, before observing outcomes, that
THEORICA's exact completion set remains finite after every placement of up to
`s` known erasures and `t` adversarial corruptions?

## Proposed law

Let `C_Q` be the rational evaluation code on the selected query rows, with
feature rank `r`. The worst-case completion list after any `s` erasures and
`t` corruptions is finite if and only if

\[
d_{\min}(C_Q) \ge t+s+1.
\]

Equivalently, deleting any `t+s` selected rows preserves rank `r`.

After a realized erasure set `E`, puncturing gives
`d_min(C_{Q\\E}) >= t+1`, so the existing transcript-level finite-list gate
applies. Conversely, a rank-dropping deletion of at most `t+s` rows can be
partitioned into erased and corrupted positions (padding either set when the
witness is smaller); the remaining correct equations admit a nonzero null
direction and hence infinitely many completions.

For MDS geometry the exact query count is `r+t+s`, versus `r+2t+s` for unique
decoding.

## Frozen gates

- Add an outcome-independent exact selector implementing the distance test.
- Exhaust every allowed erasure placement on at least 80 MDS cases spanning
  ranks two and three and error/erasure budgets one and two.
- Use a second, previously unopened Cauchy feature family for at least 40 of
  those cases.
- Construct at least 60 same-row-count degenerate geometries; every one must
  fail before any transcript enumeration.
- Independently recompute all deletion/rank and punctured-distance claims with
  Fraction arithmetic and zero production imports.
- Preserve the existing transcript-level decision-identifiability behavior.
- Require full regression, deterministic evidence, Ruff, and hosted workflows.

## Scope

This is a worst-case finiteness and safe-selection result, not an efficient
large-list bound. It assumes exact rational features, trusted erasure labels,
externally certified budgets, and exact payoff-in-span structure.
