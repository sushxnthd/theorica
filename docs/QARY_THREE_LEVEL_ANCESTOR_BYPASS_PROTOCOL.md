# Frozen protocol: conditioned ancestor-bypass profile

Status: frozen before opening any conditioned exact solve below.

## Question

The corrected binary six-face expression has survived 228 exact cost triples,
but that scalar agreement does not reveal whether querying below the root can
strictly improve the optimum. Measure four exact values on unseen primitive
cost rays:

- `U`: unrestricted first query;
- `R`: first query restricted to the root level;
- `M`: first query restricted to the middle level; and
- `L`: first query restricted to the leaf level.

A strict inequality `U < R` is an executable ancestor-bypass counterexample to
the root-respecting candidate. Equality `U = R` is only finite dominance
evidence. Values `M = U` or `L = U` show that non-root-first optimal trees
exist, but do not by themselves refute the six-face cost law.

## Frozen holdouts

The following primitive triples were selected without exact conditioned
search. The first six uniquely activate the six corrected faces at 97:1 scale;
the remaining six probe asymmetric interior rays outside the prior
`{1,...,6}^3` box.

```text
(1,1,97)   (1,97,49)  (1,97,1)
(97,1,48)  (97,49,1)  (97,1,1)
(7,31,53)  (53,31,7)  (11,47,29)
(47,11,29) (29,47,11) (29,11,47)
```

## Implementation constraint

Extend the production exact solver with an optional, validated set of allowed
initial physical query indices. The restriction must apply only at the initial
state; all later actions remain unrestricted. The default path must remain
byte-for-byte behaviorally compatible. Report the actual root query level and
reject empty, duplicate, Boolean, non-integer, or out-of-range restrictions.

## Acceptance criteria

1. All 12 unrestricted optima equal the corrected six-face prediction.
2. All 12 root-first conditioned optima equal the unrestricted optimum.
3. The implementation reports all four conditioned optima and first-query
   witnesses without substituting a heuristic policy.
4. A separate standard-library implementation reproduces every conditioned
   optimum with zero THEORICA imports.
5. A necessary-copy deletion still causes conservative abstention.
6. Evidence is deterministic; full tests, Ruff, diff checks, and hosted
   workflows pass.

## Kill criteria

- any `U < R`, which isolates a strict ancestor-bypass improvement;
- any unrestricted optimum below or above the feasible six-face value;
- disagreement between production and independent conditioned solvers; or
- a finite certificate after the missing-copy attack.

## Claim boundary

Passing establishes exact first-action dominance only on these twelve binary
instances. It does not prove a universal exchange lemma, exclude bypass on
other positive costs, or establish results for larger arities, depths, fault
budgets, or reduced query multiplicity.
