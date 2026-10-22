# Coupled-additive minimax correction

## Smallest supported claim

For any finite coupled ambiguity vertex set C and certified additive component payoff, THEORICA can solve the robust game exactly over component action marginals rather than joint actions:

V_C = max_(mu_t) min_(b in C) sum_t <mu_t, M_t(:,b_t)>.

The reduced primal has 1 + sum_t(|A_t|-1) variables, independent of the Cartesian joint-action count. An optimal executable joint policy is recovered by common-mass coupling with support at most 1 + sum_t(s_t-1).

Let v_t denote the rectangular component values. The coupled value obeys V_C >= sum_t v_t. Equality holds exactly when there is a probability distribution lambda supported on C such that every component marginal is nature-optimal:

E_lambda[M_t(a_t,b_t)] <= v_t for every component t and action a_t.

Failure of this rational feasibility system is equivalent to a strictly positive coupling bonus.

## Proof

For fixed b, additivity and linearity imply that a joint action distribution affects expected payoff only through its component marginals. Conversely, any tuple of marginals admits a joint coupling. Maximizing over joint distributions is therefore exactly the reduced marginal LP.

By finite minimax duality its dual is

min_(lambda in Delta(C)) sum_t max_(a_t) E_lambda M_t(a_t,b_t).

Each summand is at least v_t. The total equals sum_t v_t iff every summand equals its lower bound, which is precisely the displayed feasibility system. Otherwise at least one summand is strictly larger and the coupling bonus is positive.

The greedy coupling repeatedly emits the current positive component atoms with their minimum remaining mass. Each nonfinal emission exhausts at least one nonfinal marginal atom, proving support at most 1 + sum_t(s_t-1).

## Frozen evidence

- 98,415/98,415 exact matches against an independently expanded joint-game solver.
- Zero value mismatches and zero equality-criterion mismatches.
- 60,903 zero-bonus cases and 37,512 strict-bonus cases.
- Among proper nonrectangular sets: 54,342 equality cases and 37,512 strict cases, so cardinality/nonrectangularity alone does not explain the boundary.
- By coupled-vertex count: size 1 = 8,464 equality / 17,780 strict; size 2 = 23,830 / 15,536; size 3 = 22,048 / 4,196; full size 4 = 6,561 / 0.
- Maximum observed coupling bonus: 4. Maximum realized policy support: 3.
- 32/32 unopened three-factor cases from seed 20261026 matched the expanded exact solver: 13 equality and 19 strict-bonus cases.
- Independent Fraction-only checker, importing no THEORICA code, reproduced the full 60,903 / 37,512 digest.
- Six-factor scaling witness: 64 joint actions reduced to seven LP variables, value 6, one policy atom.

## Executable consequence

synthesize_coupled_additive_plan returns exact rational component marginals, a sparse joint policy, the rectangular baseline, coupling bonus, and (when equality holds) a coupled nature witness. It rejects missing additivity certificates, duplicate/out-of-domain vertices, unsupported component structure, and excessive exact active-set searches.

## Novelty audit

The ingredients are established: finite minimax/LP duality; rectangular uncertainty in robust dynamic programming (Iyengar, 2005; Nilim and El Ghaoui, 2005); and marginal-coupling/transportation-polytopes. Recent work also continues to characterize dynamic-programming-compatible nonrectangular uncertainty sets. The audit did not establish priority for this exact finite coupled-additive equality certificate or THEORICA implementation, but absence from the targeted search is not proof of novelty.

Primary/closest references:

- Iyengar, Robust Dynamic Programming, Mathematics of Operations Research 30 (2005), 257-280.
- Nilim and El Ghaoui, Robust Control of Markov Decision Processes with Uncertain Transition Matrices, Operations Research 53 (2005), 780-798.
- Kellerer, duality theorems for marginal problems (1984).
- Grand-Clément, Si, and Wang, Dynamic Programming-Compatible Uncertainty Sets in Robust Markov Decision Processes (2026), DOI 10.1287/moor.2024.0760.

Accordingly, describe this as a sharp applied decomposition/certificate law with exhaustive evidence, not as a wholly new minimax theorem.

## Limits

The implementation currently requires each component to have two actions or two ambiguity vertices, matching THEORICA's previously certified exact component solvers. Exact active-set enumeration is deliberately capped and may abstain on larger reduced LPs. The result assumes an explicitly enumerated finite C and exactly additive payoff; cross-component payoff terms invalidate it. It does not address sequential/adaptive games.
