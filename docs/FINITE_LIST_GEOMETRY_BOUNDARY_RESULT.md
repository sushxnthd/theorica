# Finite-list geometry boundary

## Exact theorem

Let the available queried feature rows define a rational evaluation code
\(C_A\) of feature rank \(r\), and permit up to \(t\) adversarial row errors.
The worst-case set of exact feature-span completions is finite if and only if

\[
d_{\min}(C_A)\ge t+1.
\]

Equivalently, deleting any \(t\) available query rows must preserve rank \(r\).
Known erasures are removed before applying this test.

## Proof

If every allowed deletion preserves rank, the correct rows left by any feasible
error placement contain a full-rank basis. Each completion is therefore fixed by
one of finitely many rational bases, so the union of candidates is finite.

Conversely, if some deletion of at most \(t\) rows drops rank, let the adversary
declare those rows corrupted. The remaining correct equations have a nonzero
coefficient-space null direction. Moving any rational distance along that
direction produces another feature-span completion with the same correct
transcript, hence infinitely many feasible completions. Finite enumeration is
unsound and the planner must abstain.

## Query-complexity consequence

For MDS feature geometry with \(s\) known erasures:

| Goal | Exact worst-case queries |
|---|---:|
| Finite completion list | \(r+t+s\) |
| Unique completion | \(r+2t+s\) |

Thus decision-identifiable list planning has a genuine intermediate regime. It
may save exactly \(t\) queries when all feasible completions agree on the robust
decision, while preserving the earlier unique-decoding boundary when the model
itself is required.

## Exact evidence

| Gate | Result |
|---|---:|
| Prior decision-identifiable MDS cases | 60/60 |
| New MDS cases with \(t\in\{1,2\}\) | 40/40 |
| Same-size degenerate rank-deletion attacks | 60/60 rejected before enumeration |
| Aggregate queries saved versus unique decoding | 140 |
| Independent Fraction-only audit | 100/100 positives, 60/60 attacks |
| Independent production imports | 0 |
| Primary digest | `641174f270c7502b4e3fb04e320f35e0aba3a82263e99fecd7616deac1abddd6` |
| Independent digest | `72046a749cdefc430b03ad19f46bf43dcf39e696e4f41fd0d6b9c0abb8e6d35d` |

The strongest simple baseline, row count \(r+t\) alone, failed on every one of
the 60 degenerate controls. Algebraic deletion resilience, not count, is the
operative condition.

## Product consequence

THEORICA now checks the finite-list distance before constructing any version
space. A certified transcript below the geometry boundary fails closed instead
of returning a policy from an incomplete candidate enumeration. Above the
boundary, the decision-identifiability criterion remains executable even when
unique decoding is impossible.

## Novelty and limits

The coding-theoretic distance/rank equivalence and list-decoding concept are
classical. The bounded contribution is their exact use as THEORICA's safety
boundary between finite algebraic version spaces and positive-dimensional
ambiguity, combined with the downstream robust-decision quotient. No novelty is
claimed for MDS codes or list decoding themselves.

This theorem concerns worst-case finiteness, not polynomial list-size bounds or
efficient large-scale list decoding. It assumes exact rational arithmetic,
externally certified features and budgets, and trusted erasure labels. It does
not cover approximate rank, stochastic noise, unknown features, or adversarial
resource exhaustion inside a finite but large list.
