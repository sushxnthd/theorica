"""Robust query frontiers for uncertain certified provenance priors."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from math import lcm

import numpy as np
from scipy.optimize import linprog


@dataclass(frozen=True)
class RobustProvenanceFrontier:
    carrier_size: int
    query_budget: int
    covered_labels: int
    tv_radius: Fraction
    deterministic_value: Fraction
    randomized_value: float
    randomized_minus_deterministic: float
    deterministic_plan_minimax: bool
    action: str


@dataclass(frozen=True)
class SubsetMixtureComponent:
    covered_labels: tuple[int, ...]
    probability: float


@dataclass(frozen=True)
class RobustRandomizedPlan:
    carrier_size: int
    query_budget: int
    covered_labels: int
    tv_radius: Fraction
    mixture: tuple[SubsetMixtureComponent, ...]
    inclusion_probabilities: tuple[float, ...]
    frontier_value: float
    certified_worst_case_payoff: float
    certificate_residual: float
    certificate_valid: bool
    solver_status: str


@dataclass(frozen=True)
class SampledRobustPlan:
    component_index: int
    covered_labels: tuple[int, ...]
    query_order: tuple[int, ...]
    terminal_guess: int
    seed_digest: str


def deterministic_tv_frontier(
    prior_weights: tuple[int, ...], query_budget: int, tv_radius: Fraction,
) -> Fraction:
    """Exact deterministic robust value, including the full-coverage boundary."""
    weights = tuple(int(value) for value in prior_weights)
    if len(weights) < 3 or any(value < 0 for value in weights) or sum(weights) <= 0:
        raise ValueError("prior_weights must be nonnegative with positive sum")
    q = int(query_budget)
    if not 0 <= q < len(weights):
        raise ValueError("query_budget must lie in [0,n-1]")
    delta = Fraction(tv_radius)
    if not 0 <= delta <= 1:
        raise ValueError("tv_radius must lie in [0,1]")
    if q + 1 == len(weights):
        return Fraction(1)
    nominal = Fraction(sum(sorted(weights, reverse=True)[: q + 1]), sum(weights))
    return max(Fraction(0), nominal - delta)


def _randomized_frontier_solution(
    prior_weights: tuple[int, ...], query_budget: int, tv_radius: Fraction,
) -> tuple[object, tuple[tuple[int, ...], ...]]:
    """Solve the adversarial epigraph LP and retain its subset ordering."""
    weights = tuple(int(value) for value in prior_weights)
    n = len(weights)
    _ = deterministic_tv_frontier(weights, query_budget, tv_radius)
    k = int(query_budget) + 1
    p = np.asarray(weights, dtype=float) / sum(weights)
    delta = float(Fraction(tv_radius))
    # Variables: adversarial pi[0:n], absolute deviations u[n:2n], epigraph v.
    objective = np.zeros(2 * n + 1); objective[-1] = 1.0
    aub, bub = [], []
    subsets = tuple(combinations(range(n), k))
    for subset in subsets:
        row = np.zeros(2 * n + 1); row[list(subset)] = 1.0; row[-1] = -1.0
        aub.append(row); bub.append(0.0)
    for index in range(n):
        row = np.zeros(2 * n + 1); row[index] = 1.0; row[n + index] = -1.0
        aub.append(row); bub.append(p[index])
        row = np.zeros(2 * n + 1); row[index] = -1.0; row[n + index] = -1.0
        aub.append(row); bub.append(-p[index])
    row = np.zeros(2 * n + 1); row[n:2 * n] = 1.0
    aub.append(row); bub.append(2.0 * delta)
    aeq = np.zeros((1, 2 * n + 1)); aeq[0, :n] = 1.0
    result = linprog(
        objective, A_ub=np.asarray(aub), b_ub=np.asarray(bub),
        A_eq=aeq, b_eq=np.asarray([1.0]), bounds=[(0.0, None)] * (2 * n + 1),
        method="highs",
    )
    if not result.success or result.fun is None:
        raise RuntimeError(f"robust frontier LP failed: {result.message}")
    return result, subsets


def randomized_tv_frontier_lp(
    prior_weights: tuple[int, ...], query_budget: int, tv_radius: Fraction,
) -> float:
    """Compute min_{TV(pi,p)<=delta} sum of the q+1 largest pi masses.

    Finite minimax duality makes this exactly the randomized robust value.
    The returned floating value is accepted only after HiGHS reports optimality.
    """
    result, _ = _randomized_frontier_solution(prior_weights, query_budget, tv_radius)
    return float(result.fun)


def _worst_case_inclusion_payoff(
    prior_weights: tuple[int, ...], tv_radius: Fraction,
    inclusion_probabilities: tuple[float, ...],
) -> float:
    """Independently minimize pi dot inclusion over the certified TV ball."""
    weights = tuple(int(value) for value in prior_weights)
    n = len(weights)
    if len(inclusion_probabilities) != n:
        raise ValueError("inclusion probability dimension mismatch")
    _ = deterministic_tv_frontier(weights, 0, tv_radius)
    p = np.asarray(weights, dtype=float) / sum(weights)
    objective = np.zeros(2 * n); objective[:n] = inclusion_probabilities
    aub, bub = [], []
    for index in range(n):
        row = np.zeros(2 * n); row[index] = 1.0; row[n + index] = -1.0
        aub.append(row); bub.append(p[index])
        row = np.zeros(2 * n); row[index] = -1.0; row[n + index] = -1.0
        aub.append(row); bub.append(-p[index])
    row = np.zeros(2 * n); row[n:] = 1.0
    aub.append(row); bub.append(2.0 * float(Fraction(tv_radius)))
    aeq = np.zeros((1, 2 * n)); aeq[0, :n] = 1.0
    result = linprog(
        objective, A_ub=np.asarray(aub), b_ub=np.asarray(bub),
        A_eq=aeq, b_eq=np.asarray([1.0]), bounds=[(0.0, None)] * (2 * n),
        method="highs",
    )
    if not result.success or result.fun is None:
        raise RuntimeError(f"mixture payoff LP failed: {result.message}")
    return float(result.fun)


def synthesize_robust_randomized_plan(
    prior_weights: tuple[int, ...], query_budget: int, tv_radius: Fraction,
    *, tolerance: float = 1e-8,
) -> RobustRandomizedPlan:
    """Recover and certify an executable minimax mixture from LP dual weights."""
    result, subsets = _randomized_frontier_solution(prior_weights, query_budget, tv_radius)
    raw = -np.asarray(result.ineqlin.marginals[:len(subsets)], dtype=float)
    raw[np.abs(raw) <= tolerance / 100] = 0.0
    if np.any(raw < -tolerance) or float(raw.sum()) <= 0:
        raise RuntimeError("frontier dual did not define a probability mixture")
    probabilities = np.maximum(raw, 0.0) / float(np.maximum(raw, 0.0).sum())
    mixture = tuple(
        SubsetMixtureComponent(tuple(subset), float(probability))
        for subset, probability in zip(subsets, probabilities, strict=True)
        if probability > 0.0
    )
    n = len(prior_weights)
    inclusion = tuple(
        float(sum(component.probability for component in mixture if label in component.covered_labels))
        for label in range(n)
    )
    payoff = _worst_case_inclusion_payoff(prior_weights, tv_radius, inclusion)
    frontier = float(result.fun)
    residual = abs(payoff - frontier)
    valid = (
        abs(sum(component.probability for component in mixture) - 1.0) <= tolerance
        and all(len(component.covered_labels) == int(query_budget) + 1 for component in mixture)
        and abs(sum(inclusion) - (int(query_budget) + 1)) <= tolerance
        and residual <= tolerance
    )
    return RobustRandomizedPlan(
        n, int(query_budget), int(query_budget) + 1, Fraction(tv_radius), mixture,
        inclusion, frontier, payoff, residual, valid, str(result.message),
    )


def sample_robust_randomized_plan(
    plan: RobustRandomizedPlan, seed: str | int,
) -> SampledRobustPlan:
    """Sample reproducibly from a certified mixture without global RNG state."""
    if not plan.certificate_valid or not plan.mixture:
        raise ValueError("a valid nonempty randomized-plan certificate is required")
    material = json.dumps({
        "seed": str(seed),
        "mixture": [[list(c.covered_labels), format(c.probability, ".17g")] for c in plan.mixture],
        "frontier": format(plan.frontier_value, ".17g"),
    }, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(material).hexdigest()
    draw = int(digest, 16) / 2**256
    cumulative = 0.0
    selected = len(plan.mixture) - 1
    for index, component in enumerate(plan.mixture):
        cumulative += component.probability
        if draw < cumulative:
            selected = index
            break
    covered = plan.mixture[selected].covered_labels
    return SampledRobustPlan(selected, covered, covered[:-1], covered[-1], digest)


def robust_provenance_frontier(
    prior_weights: tuple[int, ...], query_budget: int, tv_radius: Fraction,
    *, tolerance: float = 1e-9,
) -> RobustProvenanceFrontier:
    deterministic = deterministic_tv_frontier(prior_weights, query_budget, tv_radius)
    randomized = randomized_tv_frontier_lp(prior_weights, query_budget, tv_radius)
    gap = randomized - float(deterministic)
    minimax = gap <= tolerance
    action = "use_deterministic_top_mass"
    if not minimax:
        plan = synthesize_robust_randomized_plan(
            prior_weights, query_budget, tv_radius, tolerance=max(tolerance, 1e-8),
        )
        if not plan.certificate_valid:
            raise RuntimeError("randomized plan failed its payoff certificate")
        action = "use_certified_randomized_plan"
    return RobustProvenanceFrontier(
        len(prior_weights), int(query_budget), int(query_budget) + 1,
        Fraction(tv_radius), deterministic, randomized, gap, minimax,
        action,
    )



@dataclass(frozen=True)
class SymmetryRobustPlan:
    """Closed-form minimax plan when the certified ambiguity set contains uniform."""

    carrier_size: int
    query_budget: int
    covered_labels: int
    ambiguity_kind: str
    uniform_prior_in_set: bool
    inclusion_probability: Fraction
    minimax_value: Fraction
    synthesis_complexity: str
    certificate_valid: bool


def divergence_agnostic_symmetry_value(
    carrier_size: int, query_budget: int, *, uniform_prior_in_set: bool,
) -> Fraction:
    """Exact minimax value for any ambiguity set containing the uniform prior.

    A randomized k-coverage plan has inclusion vector a with sum(a)=k.
    Uniform is an adversarial upper-bound witness: u dot a = k/n.
    Uniform k-subset sampling realizes a_i=k/n and hence the same payoff
    against every probability vector.
    """
    n = int(carrier_size)
    q = int(query_budget)
    if n < 2:
        raise ValueError("carrier_size must be at least two")
    if not 0 <= q < n:
        raise ValueError("query_budget must lie in [0,n-1]")
    if not uniform_prior_in_set:
        raise ValueError("a certificate that uniform lies in the ambiguity set is required")
    return Fraction(q + 1, n)


def deterministic_strictly_dominated(
    deterministic_worst_case: Fraction, carrier_size: int, query_budget: int,
    *, uniform_prior_in_set: bool,
) -> bool:
    """Exact iff test once a deterministic worst-case value is certified."""
    value = Fraction(deterministic_worst_case)
    if not 0 <= value <= 1:
        raise ValueError("deterministic_worst_case must lie in [0,1]")
    return value < divergence_agnostic_symmetry_value(
        carrier_size, query_budget, uniform_prior_in_set=uniform_prior_in_set,
    )


def synthesize_uniform_ambiguity_plan(
    carrier_size: int, query_budget: int, *, ambiguity_kind: str,
    uniform_prior_in_set: bool,
) -> SymmetryRobustPlan:
    """Create an O(n)-space theorem certificate; no subset LP is constructed."""
    value = divergence_agnostic_symmetry_value(
        carrier_size, query_budget, uniform_prior_in_set=uniform_prior_in_set,
    )
    kind = str(ambiguity_kind).strip()
    if not kind:
        raise ValueError("ambiguity_kind must name the certified uncertainty model")
    return SymmetryRobustPlan(
        int(carrier_size), int(query_budget), int(query_budget) + 1, kind,
        True, value, value, "O(n) sampling space; O(k) selected labels", True,
    )


def unrank_uniform_k_subset(
    carrier_size: int, covered_labels: int, rank: int,
) -> tuple[int, ...]:
    """Lexicographically unrank one of C(n,k) subsets exactly."""
    from math import comb

    n, k, r = int(carrier_size), int(covered_labels), int(rank)
    if n < 1 or not 1 <= k <= n:
        raise ValueError("require 1 <= covered_labels <= carrier_size")
    total = comb(n, k)
    if not 0 <= r < total:
        raise ValueError("rank outside subset range")
    selected: list[int] = []
    start = 0
    remaining = k
    while remaining:
        for label in range(start, n):
            block = comb(n - label - 1, remaining - 1)
            if r < block:
                selected.append(label)
                start = label + 1
                remaining -= 1
                break
            r -= block
    return tuple(selected)


def sample_uniform_ambiguity_plan(
    plan: SymmetryRobustPlan, seed: str | int,
) -> SampledRobustPlan:
    """Seed-bound exact-uniform rank sampler using rejection to avoid modulo bias."""
    from math import comb

    if not plan.certificate_valid or not plan.uniform_prior_in_set:
        raise ValueError("a valid uniform-in-ambiguity certificate is required")
    total = comb(plan.carrier_size, plan.covered_labels)
    modulus = 1 << 256
    limit = modulus - modulus % total
    counter = 0
    while True:
        material = json.dumps({
            "seed": str(seed), "counter": counter, "n": plan.carrier_size,
            "k": plan.covered_labels, "ambiguity": plan.ambiguity_kind,
        }, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(material).hexdigest()
        draw = int(digest, 16)
        if draw < limit:
            rank = draw % total
            break
        counter += 1
    covered = unrank_uniform_k_subset(plan.carrier_size, plan.covered_labels, rank)
    return SampledRobustPlan(rank, covered, covered[:-1], covered[-1], digest)


@dataclass(frozen=True)
class OrbitBalancedPlan:
    """Exact orbit-mixture certificate for a finite permutation action."""

    carrier_size: int
    query_budget: int
    covered_labels: int
    ambiguity_kind: str
    uniform_prior_in_set: bool
    seed_subset: tuple[int, ...]
    action_size: int
    point_orbits: tuple[tuple[int, ...], ...]
    query_orbit: tuple[tuple[int, ...], ...]
    inclusion_probabilities: tuple[Fraction, ...]
    orbit_balance_ratios: tuple[Fraction, ...]
    balanced: bool
    universal_minimax_value: Fraction | None
    full_simplex_value: Fraction
    certificate_valid: bool


def _validate_finite_permutation_group(
    carrier_size: int, action_elements: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    """Validate an explicitly enumerated finite permutation group, fail closed."""
    n = int(carrier_size)
    identity = tuple(range(n))
    elements = tuple(sorted({tuple(int(x) for x in permutation) for permutation in action_elements}))
    if not elements:
        raise ValueError("action_elements must be nonempty")
    expected = set(range(n))
    if any(len(p) != n or set(p) != expected for p in elements):
        raise ValueError("every action element must be a permutation of the carrier")
    element_set = set(elements)
    if identity not in element_set:
        raise ValueError("action_elements must contain the identity")
    for left in elements:
        for right in elements:
            composition = tuple(left[right[i]] for i in range(n))
            if composition not in element_set:
                raise ValueError("action_elements are not closed under composition")
    return elements


def synthesize_orbit_balanced_plan(
    carrier_size: int,
    query_budget: int,
    seed_subset: tuple[int, ...],
    action_elements: tuple[tuple[int, ...], ...],
    *,
    ambiguity_kind: str,
    uniform_prior_in_set: bool,
) -> OrbitBalancedPlan:
    """Certify the sharp orbit-balance criterion and construct its query orbit.

    For point orbit O_j, uniform randomization over G.S includes every point
    with exact probability |S intersect O_j| / |O_j|. Thus the orbit mixture
    is prior-invariant with value k/n iff every point-orbit ratio equals k/n.
    """
    n, q = int(carrier_size), int(query_budget)
    if n < 2 or not 0 <= q < n:
        raise ValueError("require carrier_size >= 2 and query_budget in [0,n-1]")
    if not uniform_prior_in_set:
        raise ValueError("a certificate that uniform lies in the ambiguity set is required")
    kind = str(ambiguity_kind).strip()
    if not kind:
        raise ValueError("ambiguity_kind must name the certified uncertainty model")
    k = q + 1
    seed = tuple(sorted(int(x) for x in seed_subset))
    if len(seed) != k or len(set(seed)) != k or any(not 0 <= x < n for x in seed):
        raise ValueError("seed_subset must contain exactly q+1 distinct carrier labels")
    group = _validate_finite_permutation_group(n, action_elements)

    remaining = set(range(n))
    point_orbits: list[tuple[int, ...]] = []
    while remaining:
        representative = min(remaining)
        orbit = tuple(sorted({g[representative] for g in group}))
        point_orbits.append(orbit)
        remaining.difference_update(orbit)
    point_orbits.sort()

    query_orbit = tuple(sorted({tuple(sorted(g[x] for x in seed)) for g in group}))
    support = len(query_orbit)
    counts = tuple(sum(label in subset for subset in query_orbit) for label in range(n))
    inclusion = tuple(Fraction(count, support) for count in counts)
    ratios = tuple(Fraction(sum(x in set(seed) for x in orbit), len(orbit)) for orbit in point_orbits)
    target = Fraction(k, n)
    balanced = all(value == target for value in ratios)
    full_simplex = min(inclusion)
    valid = (
        len(point_orbits) >= 1
        and set().union(*(set(orbit) for orbit in point_orbits)) == set(range(n))
        and all(len(subset) == k for subset in query_orbit)
        and sum(inclusion) == k
        and all(all(inclusion[x] == ratios[j] for x in orbit) for j, orbit in enumerate(point_orbits))
        and (not balanced or all(value == target for value in inclusion))
        and full_simplex == min(ratios)
    )
    return OrbitBalancedPlan(
        n, q, k, kind, True, seed, len(group), tuple(point_orbits), query_orbit,
        inclusion, ratios, balanced, target if balanced else None, full_simplex, valid,
    )


def sample_orbit_balanced_plan(
    plan: OrbitBalancedPlan, seed: str | int,
) -> SampledRobustPlan:
    """Sample exactly uniformly from a certified balanced query orbit."""
    if not plan.certificate_valid or not plan.balanced or not plan.query_orbit:
        raise ValueError("a valid balanced orbit plan is required")
    total = len(plan.query_orbit)
    modulus = 1 << 256
    limit = modulus - modulus % total
    counter = 0
    while True:
        material = json.dumps({
            "seed": str(seed), "counter": counter, "carrier_size": plan.carrier_size,
            "query_budget": plan.query_budget, "seed_subset": list(plan.seed_subset),
            "query_orbit": [list(subset) for subset in plan.query_orbit],
            "ambiguity": plan.ambiguity_kind,
        }, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(material).hexdigest()
        draw = int(digest, 16)
        if draw < limit:
            rank = draw % total
            break
        counter += 1
    covered = plan.query_orbit[rank]
    return SampledRobustPlan(rank, covered, covered[:-1], covered[-1], digest)


@dataclass(frozen=True)
class OrbitMixtureComponent:
    """One uniform query-orbit component of an invariant mixture."""

    seed_subset: tuple[int, ...]
    query_orbit: tuple[tuple[int, ...], ...]
    orbit_composition: tuple[Fraction, ...]
    probability: Fraction


@dataclass(frozen=True)
class OrbitMixturePlan:
    """Exact sparse certificate for a mixture of admissible query orbits."""

    carrier_size: int
    query_budget: int
    covered_labels: int
    ambiguity_kind: str
    point_orbits: tuple[tuple[int, ...], ...]
    accessible_query_orbits: int
    affine_dimension: int
    components: tuple[OrbitMixtureComponent, ...]
    inclusion_probabilities: tuple[Fraction, ...]
    target_probability: Fraction
    feasible: bool
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class OrbitAmbiguityPlan:
    """Exact maximin certificate on the point-orbit ambiguity quotient."""

    carrier_size: int
    query_budget: int
    covered_labels: int
    ambiguity_kind: str
    point_orbits: tuple[tuple[int, ...], ...]
    ambiguity_vertices: tuple[tuple[Fraction, ...], ...]
    accessible_query_orbits: int
    components: tuple[OrbitMixtureComponent, ...]
    minimax_value: Fraction
    best_pure_value: Fraction
    randomized_gain: Fraction
    strict_randomization_advantage: bool
    certificate_valid: bool
    reason: str


def _point_orbits(
    carrier_size: int, group: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    remaining = set(range(carrier_size))
    result: list[tuple[int, ...]] = []
    while remaining:
        representative = min(remaining)
        orbit = tuple(sorted({g[representative] for g in group}))
        result.append(orbit)
        remaining.difference_update(orbit)
    return tuple(sorted(result))


def synthesize_orbit_mixture_plan(
    carrier_size: int,
    query_budget: int,
    admissible_seeds: tuple[tuple[int, ...], ...],
    action_elements: tuple[tuple[int, ...], ...],
    *,
    ambiguity_kind: str,
    uniform_prior_in_set: bool,
) -> OrbitMixturePlan:
    """Exactly synthesize a sparse invariant plan over admissible query orbits.

    The admissible family is the union of the G-orbits of ``admissible_seeds``.
    A feasible plan is returned exactly when the uniform inclusion vector lies
    in the convex hull of the normalized point-orbit composition vectors.
    Caratheodory's theorem bounds the returned number of orbit components by
    affine_dimension + 1, hence by the number of point orbits.
    """
    from sympy import Matrix, linsolve

    n, q = int(carrier_size), int(query_budget)
    if n < 2 or not 0 <= q < n:
        raise ValueError("require carrier_size >= 2 and query_budget in [0,n-1]")
    if not uniform_prior_in_set:
        raise ValueError("a certificate that uniform lies in the ambiguity set is required")
    kind = str(ambiguity_kind).strip()
    if not kind:
        raise ValueError("ambiguity_kind must name the certified uncertainty model")
    group = _validate_finite_permutation_group(n, action_elements)
    point_orbits = _point_orbits(n, group)
    k = q + 1
    if not admissible_seeds:
        raise ValueError("admissible_seeds must be nonempty")

    orbit_records: dict[tuple[tuple[int, ...], ...], tuple[tuple[int, ...], tuple[Fraction, ...]]] = {}
    for raw_seed in admissible_seeds:
        seed = tuple(sorted(int(x) for x in raw_seed))
        if len(seed) != k or len(set(seed)) != k or any(not 0 <= x < n for x in seed):
            raise ValueError("every admissible seed must contain exactly q+1 distinct labels")
        query_orbit = tuple(sorted({tuple(sorted(g[x] for x in seed)) for g in group}))
        canonical_seed = min(query_orbit)
        composition = tuple(
            Fraction(sum(x in set(canonical_seed) for x in orbit), len(orbit))
            for orbit in point_orbits
        )
        orbit_records[query_orbit] = (canonical_seed, composition)
    records = tuple(sorted((seed, orbit, comp) for orbit, (seed, comp) in orbit_records.items()))
    compositions = tuple(record[2] for record in records)
    target = Fraction(k, n)
    target_vector = tuple(target for _ in point_orbits)
    if len(compositions) == 1:
        affine_dimension = 0
    else:
        affine_dimension = int(Matrix([
            [value for value in (
                tuple(compositions[i][j] - compositions[0][j] for j in range(len(point_orbits)))
            )]
            for i in range(1, len(compositions))
        ]).rank())

    selected: tuple[int, ...] | None = None
    selected_weights: tuple[Fraction, ...] = ()
    max_support = min(len(records), affine_dimension + 1)
    for support_size in range(1, max_support + 1):
        for indices in combinations(range(len(records)), support_size):
            columns = [[compositions[index][row] for index in indices]
                       for row in range(len(point_orbits))]
            columns.append([Fraction(1) for _ in indices])
            rhs = list(target_vector) + [Fraction(1)]
            solutions = linsolve((Matrix(columns), Matrix(rhs)))
            if not solutions:
                continue
            solution = next(iter(solutions))
            if any(value.free_symbols for value in solution):
                continue
            weights = tuple(Fraction(int(value.p), int(value.q)) for value in solution)
            if all(value > 0 for value in weights) and sum(weights) == 1:
                selected, selected_weights = indices, weights
                break
        if selected is not None:
            break

    if selected is None:
        return OrbitMixturePlan(
            n, q, k, kind, point_orbits, len(records), affine_dimension, (),
            (), target, False, True, "uniform_target_outside_accessible_orbit_polytope",
        )

    components = tuple(
        OrbitMixtureComponent(records[index][0], records[index][1], records[index][2], weight)
        for index, weight in zip(selected, selected_weights, strict=True)
    )
    inclusion = tuple(
        sum((component.probability * Fraction(
            sum(label in subset for subset in component.query_orbit), len(component.query_orbit)
        ) for component in components), Fraction(0))
        for label in range(n)
    )
    valid = (
        sum((component.probability for component in components), Fraction(0)) == 1
        and len(components) <= affine_dimension + 1
        and len(components) <= len(point_orbits)
        and inclusion == (target,) * n
        and all(component.probability > 0 for component in components)
    )
    return OrbitMixturePlan(
        n, q, k, kind, point_orbits, len(records), affine_dimension, components,
        inclusion, target, True, valid, "sparse_orbit_mixture_certificate",
    )


def sample_orbit_mixture_plan(
    plan: OrbitMixturePlan, seed: str | int,
) -> SampledRobustPlan:
    """Sample exactly from both rational mixture weights and uniform query orbits."""
    if not plan.certificate_valid or not plan.feasible or not plan.components:
        raise ValueError("a valid feasible orbit-mixture certificate is required")
    denominator = lcm(*(component.probability.denominator for component in plan.components))
    masses = tuple(int(component.probability * denominator) for component in plan.components)

    def exact_rank(namespace: str, total: int) -> tuple[int, str]:
        modulus = 1 << 256
        limit = modulus - modulus % total
        counter = 0
        while True:
            material = json.dumps({
                "seed": str(seed), "namespace": namespace, "counter": counter,
                "n": plan.carrier_size, "k": plan.covered_labels,
                "components": [
                    [list(c.seed_subset), str(c.probability)] for c in plan.components
                ],
            }, sort_keys=True, separators=(",", ":")).encode()
            digest = hashlib.sha256(material).hexdigest()
            draw = int(digest, 16)
            if draw < limit:
                return draw % total, digest
            counter += 1

    mixture_rank, first_digest = exact_rank("mixture", denominator)
    cumulative = 0
    component_index = len(masses) - 1
    for index, mass in enumerate(masses):
        cumulative += mass
        if mixture_rank < cumulative:
            component_index = index
            break
    component = plan.components[component_index]
    orbit_rank, second_digest = exact_rank(f"orbit-{component_index}-{first_digest}", len(component.query_orbit))
    covered = component.query_orbit[orbit_rank]
    return SampledRobustPlan(component_index, covered, covered[:-1], covered[-1], second_digest)


def synthesize_orbit_ambiguity_plan(
    carrier_size: int,
    query_budget: int,
    admissible_seeds: tuple[tuple[int, ...], ...],
    action_elements: tuple[tuple[int, ...], ...],
    ambiguity_orbit_mass_vertices: tuple[tuple[Fraction, ...], ...],
    *,
    ambiguity_kind: str,
    ambiguity_invariant: bool,
) -> OrbitAmbiguityPlan:
    """Solve a certified invariant robust query game in its exact orbit quotient.

    The ambiguity vertices are masses on point orbits, not per-label masses.
    For a G-invariant ambiguity set, group averaging makes invariant query plans
    maximin-complete.  Their payoff depends only on the dot product between a
    query-orbit composition vector and an ambiguity orbit-mass vector.
    """
    from sympy import Matrix, linsolve

    n, q = int(carrier_size), int(query_budget)
    if n < 2 or not 0 <= q < n:
        raise ValueError("require carrier_size >= 2 and query_budget in [0,n-1]")
    if not ambiguity_invariant:
        raise ValueError("a certificate that the ambiguity set is action-invariant is required")
    kind = str(ambiguity_kind).strip()
    if not kind:
        raise ValueError("ambiguity_kind must name the certified uncertainty model")
    group = _validate_finite_permutation_group(n, action_elements)
    point_orbits = _point_orbits(n, group)
    r = len(point_orbits)
    k = q + 1
    if not admissible_seeds:
        raise ValueError("admissible_seeds must be nonempty")

    records_by_orbit: dict[
        tuple[tuple[int, ...], ...], tuple[tuple[int, ...], tuple[Fraction, ...]]
    ] = {}
    for raw_seed in admissible_seeds:
        seed = tuple(sorted(int(x) for x in raw_seed))
        if len(seed) != k or len(set(seed)) != k or any(not 0 <= x < n for x in seed):
            raise ValueError("every admissible seed must contain exactly q+1 distinct labels")
        query_orbit = tuple(sorted({tuple(sorted(g[x] for x in seed)) for g in group}))
        canonical_seed = min(query_orbit)
        composition = tuple(
            Fraction(sum(x in set(canonical_seed) for x in orbit), len(orbit))
            for orbit in point_orbits
        )
        records_by_orbit[query_orbit] = (canonical_seed, composition)
    records = tuple(sorted(
        (seed, orbit, composition)
        for orbit, (seed, composition) in records_by_orbit.items()
    ))

    vertices = tuple(sorted({
        tuple(Fraction(value) for value in raw) for raw in ambiguity_orbit_mass_vertices
    }))
    if not vertices:
        raise ValueError("ambiguity_orbit_mass_vertices must be nonempty")
    if any(len(vertex) != r for vertex in vertices):
        raise ValueError("each ambiguity vertex must have one mass per point orbit")
    if any(any(value < 0 for value in vertex) or sum(vertex) != 1 for vertex in vertices):
        raise ValueError("each ambiguity vertex must be a probability vector")

    payoff = tuple(tuple(
        sum((composition[j] * vertex[j] for j in range(r)), Fraction(0))
        for vertex in vertices
    ) for _, _, composition in records)
    pure_values = tuple(min(row) for row in payoff)
    best_pure = max(pure_values)

    best: tuple[Fraction, tuple[int, ...], tuple[Fraction, ...]] | None = None
    max_support = min(len(records), len(vertices), r)
    for support_size in range(1, max_support + 1):
        for support in combinations(range(len(records)), support_size):
            for active in combinations(range(len(vertices)), support_size):
                # Unknowns are support weights followed by the game value.
                rows = [[Fraction(1) for _ in support] + [Fraction(0)]]
                rhs = [Fraction(1)]
                for vertex_index in active:
                    rows.append([
                        payoff[action_index][vertex_index] for action_index in support
                    ] + [Fraction(-1)])
                    rhs.append(Fraction(0))
                solutions = linsolve((Matrix(rows), Matrix(rhs)))
                if not solutions:
                    continue
                solution = next(iter(solutions))
                if any(value.free_symbols for value in solution):
                    continue
                exact = tuple(Fraction(int(value.p), int(value.q)) for value in solution)
                weights, value = exact[:-1], exact[-1]
                if not all(weight > 0 for weight in weights):
                    continue
                realized = tuple(sum((
                    weights[pos] * payoff[action_index][vertex_index]
                    for pos, action_index in enumerate(support)
                ), Fraction(0)) for vertex_index in range(len(vertices)))
                if any(candidate < value for candidate in realized) or min(realized) != value:
                    continue
                candidate = (value, support, weights)
                if best is None or value > best[0] or (
                    value == best[0] and (support, weights) < (best[1], best[2])
                ):
                    best = candidate
    if best is None:
        raise RuntimeError("exact quotient game enumeration found no feasible vertex")

    value, support, weights = best
    components = tuple(
        OrbitMixtureComponent(records[index][0], records[index][1], records[index][2], weight)
        for index, weight in zip(support, weights, strict=True)
    )
    realized = tuple(sum((
        component.probability * sum((
            component.orbit_composition[j] * vertex[j] for j in range(r)
        ), Fraction(0)) for component in components
    ), Fraction(0)) for vertex in vertices)
    valid = (
        sum((component.probability for component in components), Fraction(0)) == 1
        and all(component.probability > 0 for component in components)
        and len(components) <= r
        and min(realized) == value
        and value >= best_pure
    )
    gain = value - best_pure
    return OrbitAmbiguityPlan(
        n, q, k, kind, point_orbits, vertices, len(records), components,
        value, best_pure, gain, gain > 0, valid,
        "exact_orbit_quotient_maximin_certificate",
    )


def sample_orbit_ambiguity_plan(
    plan: OrbitAmbiguityPlan, seed: str | int,
) -> SampledRobustPlan:
    """Sample exactly from a certified rational orbit-quotient plan."""
    if not plan.certificate_valid or not plan.components:
        raise ValueError("a valid nonempty orbit-ambiguity certificate is required")
    denominator = lcm(*(component.probability.denominator for component in plan.components))
    masses = tuple(int(component.probability * denominator) for component in plan.components)

    def exact_rank(namespace: str, total: int) -> tuple[int, str]:
        modulus = 1 << 256
        limit = modulus - modulus % total
        counter = 0
        while True:
            material = json.dumps({
                "seed": str(seed), "namespace": namespace, "counter": counter,
                "n": plan.carrier_size, "k": plan.covered_labels,
                "ambiguity": [[str(x) for x in v] for v in plan.ambiguity_vertices],
                "components": [
                    [list(c.seed_subset), str(c.probability)] for c in plan.components
                ],
            }, sort_keys=True, separators=(",", ":")).encode()
            digest = hashlib.sha256(material).hexdigest()
            draw = int(digest, 16)
            if draw < limit:
                return draw % total, digest
            counter += 1

    mixture_rank, first_digest = exact_rank("mixture", denominator)
    cumulative = 0
    component_index = len(masses) - 1
    for index, mass in enumerate(masses):
        cumulative += mass
        if mixture_rank < cumulative:
            component_index = index
            break
    component = plan.components[component_index]
    orbit_rank, digest = exact_rank(
        f"orbit-{component_index}-{first_digest}", len(component.query_orbit),
    )
    covered = component.query_orbit[orbit_rank]
    return SampledRobustPlan(component_index, covered, covered[:-1], covered[-1], digest)
