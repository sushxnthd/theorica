# Three-vertex additive arrangement protocol

## Frozen question

For a finite robust game with additive component payoffs and exactly three
coupled ambiguity vertices, can THEORICA recover the exact minimax value and an
executable optimal policy without enumerating the Cartesian joint-action space?

## Proposed law

Write nature's distribution as `(x,y,1-x-y)`. Each component contributes the
upper envelope of its action planes. The sum is convex and piecewise affine,
so its minimum over the probability triangle occurs at a vertex of the
arrangement formed by component-local action-tie lines and the triangle
boundary. It is therefore sufficient to inspect boundary intersections and
pairwise tie-line intersections. If `L = sum_t binom(|A_t|,2)`, the value gate
uses `O(L^2)` exact candidates rather than `product_t |A_t|` joint actions.

An optimal row policy should require at most three tied joint responses. A
deterministic optimum exists exactly when one tied joint response guarantees
the dual value at all three vertices; otherwise randomization is necessary.

## Decisive falsification

Kill the kernel on any exact mismatch against an independently expanded
rational three-column solver, any returned policy whose worst-case payoff is
below the claimed value, or any instance requiring support greater than three.

## Frozen evaluation

- Exhaust every two-component/two-action game with payoffs in `{0,1,2}`.
- Then generate 36 untouched mixed-dimension holdouts from seed `20261028`:
  18 predicted pure-optimal and 18 predicted strict-randomization cases.
- Compare with the expanded exact solver, report value, strictness, support,
  candidate counts, and evidence digest.
- Run a separate Fraction-only audit which must not call the production
  synthesizer.

## Limits fixed in advance

The claim covers finite additive payoffs and exactly three ambiguity vertices.
It does not cover cross-component payoff terms, sequential/adaptive games,
continuous ambiguity, floating-point certificates, or an unbounded number of
vertices. Policy recovery may fail closed when the tied Cartesian active set
exceeds its configured cap; the product-free value certificate remains valid.
