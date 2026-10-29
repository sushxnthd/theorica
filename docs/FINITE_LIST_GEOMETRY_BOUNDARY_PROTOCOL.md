# Finite-list geometry boundary protocol

Status: frozen before adversarial execution.

## Question

When is THEORICA's algebraic completion set guaranteed to be finite under up to
(t) corrupted available responses and known erasures, even when unique decoding
is impossible?

## Proposed law

Let (C_A) be the rational evaluation code on the available queried feature
rows, with feature rank (r). The worst-case completion list is finite if and
only if

[
d_{\min}(C_A) \ge t+1,
]

equivalently, deleting any (t) available rows preserves rank (r).

Sufficiency: every feasible error placement leaves at least one full-rank set of
correct rows, so each completion is determined by one of finitely many rational
bases.

Necessity: if deleting some (t) rows drops rank, an adversary may mark those
rows corrupted; the remaining correct equations have a nonzero null direction,
yielding infinitely many feature-span completions with the same transcript.

For MDS geometry this gives the tight finite-list query threshold (r+t+s),
strictly below unique decoding's (r+2t+s). Decision-identifiable planning may
operate only inside this intermediate finite-list regime.

## Frozen gates

- Verify the exact deletion/rank criterion by exhaustive row deletion.
- Preserve all existing 60 decision-identifiable positive cases at the
  (r+t) MDS threshold.
- Test at least 40 new MDS cases with corruption budgets one and two.
- Construct at least 60 matched degenerate geometries with the same row count
  but a rank drop after an allowed deletion; every case must abstain before
  version-space enumeration.
- Independent Fraction-only checker must reproduce the finite/infinite boundary
  without production imports.
- Require full regression, deterministic evidence, Ruff, and hosted workflows.

## Scope

The theorem concerns worst-case finiteness of exact feature-span completions,
not polynomial-time list-size bounds. Features, erasures, and corruption budgets
are externally certified; arithmetic is exact rational.
