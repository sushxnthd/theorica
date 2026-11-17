# Frozen protocol: depth-d explicit-sentinel divergence quotient

## Objective

Generalize the depth-three two-class theorem to arbitrary depth.  Determine
whether the complete prefix-query system for two added words is classified
solely by the first suffix coordinate at which those words diverge.

## Parametric family and prediction

For alphabet size `q>=3` and depth `d>=2`, let the base be the binary cube
`B_d={0,1}^d`.  Add an unordered pair from

`F_{q,d}={2} x {0,...,q-1}^{d-1}`.

For a distinct pair, let `r` be the length of its common prefix after the fixed
leading symbol 2.  Thus `0<=r<=d-2`.

The frozen theorem prediction is:

1. the level-coloured active query system is determined exactly by `r`;
2. systems with different `r` are non-isomorphic because the first query level
   that separates the two added completions is an invariant;
3. there are exactly `d-1` policy-transport classes; and
4. the class with common-suffix-prefix length `r` contains

   `N_r = C(q,2) q^r q^{2(d-r-2)} = (q-1)q^{2d-r-3}/2`

   unordered pairs.

All unused prefix queries are constant outside-token rows and minimax-dominated.
Within one class, an edge-checked completion/query/response-cell bijection must
transport every policy for every positive level-cost vector under the fixed
fault, erasure, and copy semantics.

## Unseen complete test

Open the complete ternary depth-four universe only after this protocol is
pushed:

- base size: 16;
- fibre size: 27;
- unordered families: `C(27,2)=351`;
- predicted classes (`r=0,1,2`): 243, 81, and 27 families;
- predicted representative-solve reduction: `351/3=117`.

Use the complete 40-group ternary depth-four prefix library with explicit
outside response `-1`.  Classify every family by exhaustive level-coloured
graph isomorphism and validate every returned edge map.

Reserve one family per class as a prospective structural holdout:

- `r=0`: `{(2,1,2,1),(2,2,0,2)}`;
- `r=1`: `{(2,2,0,1),(2,2,2,2)}`;
- `r=2`: `{(2,1,2,0),(2,1,2,2)}`.

## Decision rule

The theorem passes only if:

- all 351 pairs appear exactly once;
- exactly three classes are found with sizes 243, 81, and 27;
- class membership equals the independently computed `r` value;
- representatives transport to every family with edge-checked maps;
- representatives from different classes are certified non-isomorphic;
- all three frozen holdouts transport from their predicted representatives;
- the class counts sum to `C(q^{d-1},2)` symbolically and numerically; and
- a zero-production-import audit reconstructs the universe, invariant, maps,
  counts, and 117-fold reduction.

Any extra class, count mismatch, failed map, or holdout mismatch is retained as
a falsification.  This is a structural theorem experiment; it does not open a
new numerical minimax sweep.  PR #13 remains draft and unmerged.
