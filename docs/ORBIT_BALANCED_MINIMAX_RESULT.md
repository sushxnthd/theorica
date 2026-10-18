# Orbit-Balanced Minimax Compression Law

Status: **exact system theorem passed; historical novelty not claimed**

## Theorem

Let a finite permutation group (G) act on (n) labels (X), with point orbits (O_1,ldots,O_r). Fix a seed query (Ssubseteq X) of size (k=q+1), and randomize uniformly over the distinct translated queries (GS).

For every label (xin O_j),

[
Pr_{Tsimoperatorname{Unif}(GS)}(xin T)
=rac{|Scap O_j|}{|O_j|}.
]

Therefore the orbit plan preserves the divergence-agnostic (k/n) minimax guarantee for every certified ambiguity set containing the uniform prior if and only if

[
oxed{rac{|Scap O_j|}{|O_j|}=rac{k}{n}quad	ext{for every point orbit }O_j.}
]

Against the full probability simplex, an unbalanced orbit plan has the exact value

[
oxed{min_jrac{|Scap O_j|}{|O_j|}<rac{k}{n}.}
]

A transitive action is automatically balanced for every seed query. Transitivity is not necessary: an intransitive seed is valid exactly when it occupies every point orbit in the global proportion (k/n).

The number of supported query plans is

[
|GS|=rac{|G|}{|operatorname{Stab}_G(S)|}.
]

## Proof

The inclusion probability is constant inside each point orbit because group elements transport any label in (O_j) to any other label in (O_j) while preserving the uniform measure on distinct translated blocks.

Summing inclusion probabilities over (O_j) gives the expected size of (Tcap O_j). Every translated seed has exactly (|Scap O_j|) points in that orbit, so

[
|O_j|,Pr(xin T)=|Scap O_j|.
]

This proves the inclusion formula.

If every ratio equals (k/n), the inclusion vector is constant. Hence every prior (pi) yields payoff

[
sum_xpi_xPr(xin T)=rac{k}{n}.
]

Because uniform belongs to the ambiguity set, the preceding divergence-agnostic theorem supplies the matching upper bound (k/n). Thus the orbit plan is minimax.

If the ratios are not equal, their weighted average is (k/n), so their minimum is strictly smaller. A point mass on a least-covered point orbit attains that minimum under the full simplex. This proves sharp failure. Orbit-stabilizer gives the support formula.

## Exact verification

- 52 finite-action families:
  - cyclic actions for (2le nle10);
  - dihedral actions for (3le nle9);
  - two-orbit direct-product cyclic actions through (n=9).
- 10,180 exact action/seed plans.
- 85,664 exact inclusion-probability checks.
- 10,180 orbit-stabilizer checks.
- 3,454 balanced certificates.
- 6,726 unbalanced sharp failures.
- 44 exact, reproducible sampler checks.
- Independent standard-library checker reproduced digest
  `e9b6c193785dfab8bdb74e4e0d6e432aec4b646d5ab0614aa71c400381e0c4a1`.
- Focused production tests and the full THEORICA suite passed.
- Duplicate theorem artifacts were byte-identical.
- Final workflow: https://github.com/sushxnthd/theorica/actions/runs/39163661690

The earlier missing-`pytest` workflow failures remain preserved. They were repaired by invoking the dependency explicitly, without changing theorem code or expected results.

## Support compression

For a cyclic action and a consecutive (k)-label seed with (1<k<n-1), the query orbit has exactly (n) plans instead of (inom nk).

The finite checker observed:

- (n=10,k=5): 252 plans → 10 plans (25.2×);
- (n=11,k=5) or (6): 462 → 11 (42×);
- (n=12,k=6): 924 → 12 (77×).

The theorem holds for all finite (n); these are implementation witnesses, not the proof.

## SCIENCE ledger

The earlier (k/n) law does not require uniform randomization over every (k)-subset. The exact requirement is a balanced inclusion vector. A single group orbit supplies that vector precisely at the point-orbit balance boundary above. The same formula identifies every failure and its exact full-simplex value.

## CONSEQUENCE ledger

THEORICA now has a fail-closed structured-query planner that:

1. validates an explicitly enumerated finite permutation group;
2. computes point orbits and the distinct query orbit;
3. certifies balance using exact rational arithmetic;
4. returns the exact universal minimax value (k/n), or refuses the universal certificate;
5. exposes the exact full-simplex failure value for unbalanced seeds;
6. samples exactly and reproducibly from the certified query orbit;
7. records support compression through orbit-stabilizer.

This expands the reasoning engine from unrestricted (k)-subset plans to algebraically constrained query families while retaining a sharp optimality certificate.

## Priority boundary

The transitive special case overlaps classical orbit/design theory: a block orbit under a point-transitive group is a 1-design. Group transitivity and homogeneous subset actions are established subjects. Relevant primary literature includes:

- Godsil and Praeger, *Completely Transitive Designs* (2014): https://arxiv.org/abs/1405.2176
- Martin and Sagan, *A new notion of transitivity for groups and sets of permutations* (2002): https://arxiv.org/abs/math/0206163

No new general design-theory, group-action, orbit-stabilizer, or minimax principle is claimed. The defensible contribution is the sharp point-orbit iff boundary coupled to the uniform-containing ambiguity contract, exact failure value, executable certificate, and support-compressed THEORICA planner.

## Limitations

- The implementation accepts explicitly enumerated finite groups; compact generator algorithms are future work.
- Uniform membership in the ambiguity set remains mandatory.
- Equal label value and fixed (k)-coverage are assumed.
- An unbalanced plan may still be optimal for a narrower ambiguity set that excludes its least-covered point masses; the iff statement is for the universal guarantee over all uniform-containing ambiguity sets.
