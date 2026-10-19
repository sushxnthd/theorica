# Sparse orbit-mixture repair law

## Result

Let a finite group (G) act on a finite label set (X), with point-orbits
(O_1,ldots,O_r). Let (mathcal A) be a nonempty (G)-closed family of
admissible (k)-subset queries. For a query orbit (G S), define its
normalized composition vector

[
c(S)_j=rac{|Scap O_j|}{|O_j|}.
]

Then a (G)-invariant randomized plan supported on (mathcal A) has uniform
point-inclusion probability (k/|X|) **if and only if**

[
left(rac{k}{|X|},ldots,rac{k}{|X|}ight)
in operatorname{conv}{c(S):GSsubseteqmathcal A}.
]

If feasible, there is such a plan using at most (d+1le r) query-orbit
components, where (d) is the affine dimension of the accessible composition
vectors. Thus several individually non-minimax query orbits can repair one
another exactly even when arithmetic makes a single balanced orbit impossible.

## Proof

1. A (G)-invariant probability measure on (mathcal A) is constant on each
   query orbit, hence is a mixture of the uniform measures on those orbits.
2. Double-counting incidences between (O_j) and (GS) shows that every
   (xin O_j) is included with probability (c(S)_j) under the uniform
   measure on (GS).
3. Mixture linearity makes the resulting point-orbit inclusion vector exactly
   a convex combination of the accessible (c(S)).
4. Therefore exact uniform inclusion is equivalent to convex-hull membership.
5. All composition vectors lie in
   (sum_j |O_j|c_j=k), an affine space of dimension at most (r-1).
   Carathéodory's theorem gives a representation using at most (d+1le r)
   components.
6. Every (k)-query plan has inclusion coordinates summing to (k). The
   uniform prior is therefore an upper-bound witness of (k/|X|), while
   uniform inclusion gives payoff (k/|X|) against every prior. The
   convex-hull criterion is consequently the exact boundary for retaining the
   uniform-containing-ambiguity minimax guarantee.

## Frozen unseen prediction

For point-orbit sizes (3) and (4), (k=2), neither query type ((1,1))
nor ((0,2)) is individually balanced. The frozen prediction was that weights
(6/7) and (1/7), respectively, produce inclusion (2/7) on all seven
points. Exact execution confirmed that prediction.

## Exact verification

- 35 two-orbit action families.
- 1,293 admissible (G)-closed query families: 655 feasible and 638
  infeasible.
- 571 feasible families required genuine multi-orbit repair.
- 5,178 exact point-inclusion checks and 655 support-bound checks.
- 2,686 additional three-point-orbit cases: 824 feasible, including 763
  genuine repairs.
- An independent standard-library checker reproduced every two- and
  three-orbit feasibility count.
- Duplicate primary executions were byte-identical.
- 112/112 repository tests passed.

The smallest enumerated repair witness has point-orbit sizes (1,2), (k=1):
mixing compositions ((1,0)) and ((0,1/2)) with weights (1/3,2/3)
produces uniform inclusion (1/3).

## SCIENCE ledger

**True:** the single-orbit balance condition is not the end of the exact
boundary. The complete boundary for a restricted (G)-closed query family is
convex-hull membership, with an affine-dimension support bound. Integrality
obstructions to one-orbit balance can be repaired by sparse mixtures.

**Not claimed:** the convexity argument, group averaging, invariant designs, or
Carathéodory sparsification are historically new. Kiefer's optimal-design
framework, invariant block/design literature, and orbit-based cubature already
make the broad ingredients classical. The defensible contribution is the exact
coverage/minimax specialization, fail-closed certificate, and its integration
into THEORICA's query planner.

Priority-boundary sources:

- Jack Kiefer, *Optimum Experimental Designs*, JRSS B 21(2), 1959,
  pp. 272-319.
- Hiroshi Nozaki and Masanori Sawa, *Note on cubature formulae and designs
  obtained from group orbits*, 2011, https://arxiv.org/abs/1102.4891.
- Vahab Mirrokni et al., *Tight Bounds for Approximate Carathéodory and
  Beyond*, ICML 2017, https://proceedings.mlr.press/v70/mirrokni17a.html.

## CONSEQUENCE ledger

THEORICA now accepts a restricted set of admissible query-orbit
representatives, computes exact rational composition vectors, decides the
convex-hull criterion, and either:

- returns a certified minimax mixture using at most (d+1le r) orbit
  components plus a seed-bound exact sampler; or
- refuses the family with an explicit outside-polytope result.

This strictly extends the preceding single-orbit planner: it recovers exact
minimax guarantees in 1,334 enumerated repair cases that every individual
admissible orbit fails.

## Limitations

- The action and admissible orbit representatives must be explicitly
  enumerated and trusted.
- Exact synthesis is combinatorial in the number of accessible query orbits;
  it is intended for certificate construction, not unconstrained large-scale
  optimization.
- The theorem concerns inclusion/payoff guarantees. It does not imply higher
  strength (t)-design balance, independence between queries, or robustness
  to a false group/action certificate.
- This is an internally verified theorem and system result, not a
  peer-reviewed priority claim.
