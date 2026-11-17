# Frozen protocol: stacked ambiguity gap

Status: frozen before implementation and adversarial execution.

## Question

Can multi-action decision identifiability across a finite completion family be
reduced to one exact robust game, while returning a scalar ambiguity penalty and
a bounded scenario-level impossibility witness?

## Candidate law

For completion `theta`, let `v_theta` be its robust value. If all values equal
`v`, concatenate every scenario column from every completion into one stacked
game and call its value `v_stack`. Then `v_stack <= v`, and a common exact robust
policy exists iff `v_stack = v`. Define the exact ambiguity gap
`Delta = v - v_stack`.

If `Delta > 0`, Helly's theorem in the `(a-1)`-dimensional action simplex
predicts a witness containing at most `a` individual scenario columns, not just
`a` whole completions. The bound should be sharp for the `a` simplex-face
constraints with payoff `-1` on one action and `0` on the others.

## Frozen gates

- Preserve all 60 existing model-ambiguous positive cases with `Delta = 0`.
- Reject 20 equal-value disjoint-policy controls with positive exact gap.
- Open only after freezing: ten five-action simplex-face cases. Predict exact
  gap `1/5`, a five-column minimal witness, and intersection of every proper
  subfamily.
- Compare the stacked scalar criterion against direct common-polytope
  intersection on every case.
- Independent Fraction-only checker with zero production imports.
- Full regression, deterministic evidence, Ruff, diff check, and hosted CI.

## Kill conditions

Kill the kernel on any stacked/direct disagreement, any nonpositive attack gap,
any witness larger than the action count, any false positive under unequal
completion values, or any failed prospective five-action prediction.

## Smallest supported claim

The convexity, minimax and Helly ingredients are classical. A positive result
supports only an exact executable quotient for finite rational robust games: a
single stacked-game value computes whether model ambiguity changes the optimal
decision, its exact penalty, and a sharp bounded scenario-level abstention
witness. It does not cover approximate arithmetic, continuous action spaces,
infinite completion families, uncertain feature maps, or probabilistic noise.
