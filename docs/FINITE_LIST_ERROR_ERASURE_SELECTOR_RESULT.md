# Finite-list error-erasure selector

## Exact theorem

Let selected rational feature rows define an evaluation code `C_Q` of rank
`r`. Under every placement of at most `s` known erasures and `t` adversarial
corruptions, the worst-case exact feature-span completion set is finite if and
only if

\[
d_{\min}(C_Q) \ge t+s+1.
\]

Equivalently, deleting any `t+s` selected rows preserves rank `r`.

## Proof

After a realized erasure set `E`, puncturing loses at most `|E|` units of
minimum distance, so the available code has distance at least `t+1`. The
existing finite-list theorem then guarantees that every feasible corruption
placement leaves a full-rank correct basis, making the union of completions
finite.

Conversely, suppose deleting at most `t+s` rows drops rank. Partition a
rank-dropping witness into at most `s` erased rows and at most `t` corrupted
rows, padding within the witness complement if necessary. The remaining
correct equations have a nonzero coefficient-space null direction. Moving any
rational distance along it yields another feasible completion, so no finite
enumeration is sound.

For an MDS geometry the smallest safe query set has size `r+t+s`. Unique
decoding still requires `r+2t+s`; the decision-list regime therefore saves
exactly `t` queries when the downstream robust decision is common.

## Exact evidence

| Gate | Result |
|---|---:|
| MDS selector cases | 80/80 |
| Prospective Cauchy-family cases | 40/40 |
| Exhausted erasure placements | 1,130/1,130 |
| Transcript-level finite-list checks | 1,130/1,130 |
| Same-row-count degenerate attacks | 60/60 rejected before transcript enumeration |
| Independent checker | 80/80 positives; 60/60 attacks |
| Independent production imports | 0 |
| Aggregate query saving versus unique decoding | 120 |
| Primary evidence digest | `e9db12fddf333bd01fb4eb6371cea97b3dc9185b2cd39f1eae56473bd13c96c9` |
| Independent digest | `4d1d19ac5b7c05647aec31993cba41f0a08a297e3bd1e7268bef336f238e81ff` |

The strongest count-only baseline, `r+t+s` rows, failed on every degenerate
control. The operative condition is deletion resilience, not row count.

## Product consequence

`select_finite_list_feature_queries` is outcome-independent and searches for
the smallest exact query subset meeting the `t+s+1` distance boundary. It
returns a checkable geometry certificate or fails before any scientific
transcript is interpreted. The realized transcript still passes through the
separate `t+1` punctured-code check, giving defense in depth against erasure
placement mistakes.

## Novelty and limits

Puncturing bounds, minimum-distance/rank equivalence, and MDS constructions are
classical. The bounded contribution is the exact pre-query error-erasure
selection law for THEORICA's finite algebraic decision quotient, its independent
adversarial validation on a second feature family, and fail-closed integration.

This result guarantees finiteness, not a polynomial list-size bound or scalable
enumeration. It assumes exact rational arithmetic, trusted erasure labels,
externally certified budgets and feature-span structure. It does not cover
approximate rank, unknown features, stochastic noise, malicious erasure labels,
or resource exhaustion inside a large finite list.
