# An explicit outside-prefix token restores alphabet covariance

## Central theorem

Let a depth-`d`, arity-`q` prefix query at level `l` and prefix `p` return
the next symbol when a word lies below `p`, and a distinguished token `⊥`
otherwise.  If query costs depend only on level, then any tuple of coordinate
alphabet permutations acts by conjugacy on the complete prefix-query game,
provided `⊥` is fixed separately from the alphabet.

**Proof.** For coordinate maps `pi_0,...,pi_{d-1}`, map each completion
`w` to `(pi_0(w_0),...,pi_{d-1}(w_{d-1}))`.  Map the query `(l,p)` to
`(l,pi_{<l}(p))`.  Inside the prefix its response `w_l` maps to `pi_l(w_l)`;
outside it, `⊥` maps to `⊥`.  This is a bijection on completions, queries, and
response cells and preserves query levels.  Substitution counts, erasure
counts, remaining query multiplicities, terminal compatibility, and level
costs are invariant under this relabelling.  Induction over the finite Bellman
recursion therefore preserves every state value and transports every optimal
policy.  ∎

The old encoding violates the premise because it identifies `⊥` with alphabet
symbol `0`.  The previous zero-moving counterexample is therefore explained by
an exact semantic collision, not by a failure of alphabet symmetry itself.

## Prospective unseen test

The frozen test changed outside-prefix responses from `0` to `-1` and applied
`0 <-> 1` in every coordinate to P0.  Three refinement rounds produced
matching color multiplicities, and exhaustive backtracking found a
level-preserving incidence isomorphism.  All mapped edges were checked.

At both preregistered costs, source and unseen target agreed exactly:

| leaf cost | exact value | unique root | ordered root children | states | actions | compatibility states |
| ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 18 | 37 | 0 | `[29,29,33]` | 20,085 | 15,794 | 95 |
| 19 | 37 | 0 | `[30,30,33]` | 20,085 | 15,794 | 95 |

The source and target counts are identical at each endpoint, as conjugacy
predicts.  The certificate maps all ten completions, all thirteen queries, and
every response cell while fixing `-1`.

## Preserved falsification

The structural prediction passed, but the frozen numerical prediction did
not.  The old overloaded encoding had value 38 and children `[34,34,33]` at
`c=19`; the explicit-sentinel game instead has value 37 and children
`[30,30,33]`.  Thus changing the observation alphabet is not merely a proof
repair.  It changes the planning problem and removes the previously observed
first breakpoint at 19.

This yields an executable design rule:

- use a distinguished outside token when policies or certificates must be
  transported across alphabet relabellings;
- do not reuse values calibrated under an encoding that aliases outside with
  a real symbol, because even a nearby cost boundary can move.

## Independent check and limits

The zero-production-import audit independently replayed all four root minima,
verified exact lower/upper-bound equality, compared source and target ordered
signatures, checked identical search counts, and required the edge-checked
structural certificate.

The theorem assumes the complete prefix-query library, level-only costs, a
separate fixed outside token, and relabelled states.  It does not cover query
subsets that are not closed under the permutation, symbol-dependent costs,
or encodings that merge `⊥` with an alphabet value.  The experiment does not
locate the explicit-sentinel game's new first breakpoint.
