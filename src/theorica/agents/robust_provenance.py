"""Robust query frontiers for uncertain certified provenance priors."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from math import comb, lcm

import numpy as np
from scipy.optimize import linprog
from scipy.spatial import ConvexHull, QhullError


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


@dataclass(frozen=True)
class TwoByTwoRobustGame:
    """Exact structural certificate for a two-action, two-vertex game."""

    payoff_matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]
    action_probabilities: tuple[Fraction, Fraction]
    minimax_value: Fraction
    best_pure_value: Fraction
    randomized_gain: Fraction
    strict_randomization_advantage: bool
    protected_pairing: str
    certificate_valid: bool


@dataclass(frozen=True)
class TwoActionRobustGame:
    """Exact supported-crossing certificate for two actions and many vertices."""

    payoff_matrix: tuple[tuple[Fraction, ...], tuple[Fraction, ...]]
    action_probabilities: tuple[Fraction, Fraction]
    minimax_value: Fraction
    best_pure_value: Fraction
    randomized_gain: Fraction
    strict_randomization_advantage: bool
    supported_vertices: tuple[int, ...]
    active_vertices: tuple[int, ...]
    certificate_valid: bool


@dataclass(frozen=True)
class TwoVertexRobustGame:
    """Exact sparse-support certificate for many actions and two vertices."""

    payoff_matrix: tuple[tuple[Fraction, Fraction], ...]
    action_probabilities: tuple[Fraction, ...]
    ambiguity_probabilities: tuple[Fraction, Fraction]
    minimax_value: Fraction
    best_pure_value: Fraction
    randomized_gain: Fraction
    strict_randomization_advantage: bool
    supported_actions: tuple[int, ...]
    active_vertices: tuple[int, ...]
    certificate_valid: bool


@dataclass(frozen=True)
class AdditiveProductRobustPlan:
    """Exact sparse coupling certificate for an additive rectangular product."""

    component_payoff_matrices: tuple[tuple[tuple[Fraction, ...], ...], ...]
    component_action_probabilities: tuple[tuple[Fraction, ...], ...]
    joint_components: tuple[tuple[tuple[int, ...], Fraction], ...]
    component_values: tuple[Fraction, ...]
    component_best_pure_values: tuple[Fraction, ...]
    minimax_value: Fraction
    best_pure_value: Fraction
    randomized_gain: Fraction
    strict_randomization_advantage: bool
    expanded_action_count: int
    expanded_vertex_count: int
    support_bound: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class CoupledAdditiveRobustPlan:
    """Exact marginal-LP certificate for additive, finitely coupled ambiguity."""
    component_payoff_matrices: tuple[tuple[tuple[Fraction, ...], ...], ...]
    ambiguity_vertices: tuple[tuple[int, ...], ...]
    component_action_probabilities: tuple[tuple[Fraction, ...], ...]
    joint_components: tuple[tuple[tuple[int, ...], Fraction], ...]
    minimax_value: Fraction
    rectangular_baseline_value: Fraction
    coupling_bonus: Fraction
    rectangular_value_survives: bool
    zero_bonus_nature_witness: tuple[Fraction, ...]
    expanded_action_count: int
    reduced_variable_count: int
    support_bound: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class TwoVertexAdditiveRobustPlan:
    """Exact product-free certificate for additive games with two scenarios."""
    component_payoff_pairs: tuple[tuple[tuple[Fraction, Fraction], ...], ...]
    joint_actions: tuple[tuple[tuple[int, ...], Fraction], ...]
    minimax_value: Fraction
    nature_probability: Fraction
    strict_randomization_necessary: bool
    pure_optimal_witness: tuple[int, ...]
    expanded_action_count: int
    breakpoint_count: int
    support_bound: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class ThreeVertexAdditiveRobustPlan:
    """Exact arrangement certificate for additive games with three scenarios."""
    component_payoff_triples: tuple[tuple[tuple[Fraction, Fraction, Fraction], ...], ...]
    joint_actions: tuple[tuple[tuple[int, ...], Fraction], ...]
    minimax_value: Fraction
    nature_probabilities: tuple[Fraction, Fraction, Fraction]
    strict_randomization_necessary: bool
    expanded_action_count: int
    tie_line_count: int
    arrangement_candidate_count: int
    support_bound: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class FourVertexAdditiveRobustPlan:
    """Exact arrangement certificate for additive games with four scenarios."""
    component_payoff_vectors: tuple[tuple[tuple[Fraction, ...], ...], ...]
    joint_actions: tuple[tuple[tuple[int, ...], Fraction], ...]
    minimax_value: Fraction
    nature_probabilities: tuple[Fraction, Fraction, Fraction, Fraction]
    strict_randomization_necessary: bool
    expanded_action_count: int
    tie_hyperplane_count: int
    arrangement_candidate_count: int
    candidate_upper_bound: int
    support_bound: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class FixedScenarioAdditiveRobustPlan:
    """Exact arrangement certificate for a bounded fixed scenario count."""
    component_payoff_vectors: tuple[tuple[tuple[Fraction, ...], ...], ...]
    joint_actions: tuple[tuple[tuple[int, ...], Fraction], ...]
    minimax_value: Fraction
    nature_probabilities: tuple[Fraction, ...]
    strict_randomization_necessary: bool
    scenario_count: int
    expanded_action_count: int
    tie_hyperplane_count: int
    arrangement_candidate_count: int
    candidate_upper_bound: int
    support_bound: int
    tied_joint_action_count: int
    marginal_variable_count: int
    pure_payoff_state_count: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class RankOneScenarioQuotientPlan:
    """Exact two-endpoint quotient for affine-rank-one scenario profiles."""
    component_payoff_vectors: tuple[tuple[tuple[Fraction, ...], ...], ...]
    scenario_coordinates: tuple[Fraction, ...]
    endpoint_indices: tuple[int, int]
    affine_dimension: int
    effective_scenario_count: int
    joint_actions: tuple[tuple[tuple[int, ...], Fraction], ...]
    minimax_value: Fraction
    nature_probabilities: tuple[Fraction, ...]
    strict_randomization_necessary: bool
    scenario_count: int
    expanded_action_count: int
    support_bound: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class RankTwoScenarioHullPlan:
    """Exact convex-hull quotient for affine-rank-two scenario columns."""
    component_payoff_vectors: tuple[tuple[tuple[Fraction, ...], ...], ...]
    projected_coordinates: tuple[tuple[Fraction, Fraction], ...]
    extreme_indices: tuple[int, ...]
    affine_dimension: int
    effective_scenario_count: int
    joint_actions: tuple[tuple[tuple[int, ...], Fraction], ...]
    minimax_value: Fraction
    nature_probabilities: tuple[Fraction, ...]
    strict_randomization_necessary: bool
    scenario_count: int
    expanded_action_count: int
    support_bound: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class RankThreeScenarioPolytopePlan:
    """Exact convex-hull quotient for affine-rank-three scenario columns."""
    component_payoff_vectors: tuple[tuple[tuple[Fraction, ...], ...], ...]
    projected_coordinates: tuple[tuple[Fraction, Fraction, Fraction], ...]
    extreme_indices: tuple[int, ...]
    affine_dimension: int
    effective_scenario_count: int
    joint_actions: tuple[tuple[tuple[int, ...], Fraction], ...]
    minimax_value: Fraction
    nature_probabilities: tuple[Fraction, ...]
    strict_randomization_necessary: bool
    scenario_count: int
    expanded_action_count: int
    support_bound: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class AffineScenarioReconstruction:
    """Exact payoff-table reconstruction from an affine scenario basis."""
    component_payoff_vectors: tuple[tuple[tuple[Fraction, ...], ...], ...]
    scenario_coordinates: tuple[tuple[Fraction, ...], ...]
    query_indices: tuple[int, ...]
    descriptor_dimension: int
    scenario_count: int
    query_count: int
    certificate_valid: bool
    reason: str


@dataclass(frozen=True)
class FeatureSpanScenarioReconstruction:
    """Exact payoff reconstruction from a rational feature-row basis."""
    component_payoff_vectors: tuple[tuple[tuple[Fraction, ...], ...], ...]
    feature_rows: tuple[tuple[Fraction, ...], ...]
    query_indices: tuple[int, ...]
    pivot_columns: tuple[int, ...]
    feature_rank: int
    feature_width: int
    scenario_count: int
    query_count: int
    certificate_valid: bool
    reason: str


def _solve_fraction_system(rows, rhs):
    """Solve a square rational system; return None when singular."""
    n = len(rows)
    if n == 0:
        return ()
    a = [list(rows[i]) + [rhs[i]] for i in range(n)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col] != 0), None)
        if pivot is None:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        a[col] = [x / scale for x in a[col]]
        for row in range(n):
            if row == col or a[row][col] == 0:
                continue
            scale = a[row][col]
            a[row] = [a[row][j] - scale * a[col][j] for j in range(n + 1)]
    return tuple(a[row][-1] for row in range(n))


def _greedy_common_mass_coupling(marginals):
    active = [[[i, p] for i, p in enumerate(m) if p > 0] for m in marginals]
    pos = [0] * len(active)
    joint = []
    while all(pos[t] < len(active[t]) for t in range(len(active))):
        actions = tuple(active[t][pos[t]][0] for t in range(len(active)))
        mass = min(active[t][pos[t]][1] for t in range(len(active)))
        joint.append((actions, mass))
        for t in range(len(active)):
            active[t][pos[t]][1] -= mass
            if active[t][pos[t]][1] == 0:
                pos[t] += 1
    return tuple(joint)


def _component_exact_solution(matrix):
    if len(matrix[0]) == 2:
        solved = solve_two_vertex_robust_game(matrix)
    elif len(matrix) == 2:
        solved = solve_two_action_robust_game((matrix[0], matrix[1]))
    else:
        raise ValueError("each component must have two actions or two vertices")
    if not solved.certificate_valid:
        raise RuntimeError("component exact certificate failed")
    return solved.action_probabilities, solved.minimax_value


def synthesize_two_vertex_additive_plan(
    component_payoff_pairs,
    *,
    payoff_additive_certified: bool,
    max_delta_states: int = 2_000_000,
) -> TwoVertexAdditiveRobustPlan:
    """Solve an additive two-scenario game without Cartesian action expansion.

    The nature dual is the sum of component upper envelopes. Its minimizer is
    therefore an endpoint or a breakpoint of one component envelope. At an
    interior minimizer, a deterministic optimum exists exactly when zero is a
    reachable sum of payoff differences among the tied component actions.
    """
    if not payoff_additive_certified:
        raise ValueError("a certificate that payoff is additive is required")
    if not component_payoff_pairs:
        raise ValueError("at least one component is required")
    pairs = tuple(
        tuple(tuple(Fraction(value) for value in action) for action in component)
        for component in component_payoff_pairs
    )
    if any(not component or any(len(action) != 2 for action in component)
           for component in pairs):
        raise ValueError("each component action must have two scenario payoffs")

    candidates = {Fraction(0), Fraction(1)}
    for component in pairs:
        for left, right in combinations(component, 2):
            left_slope = left[0] - left[1]
            right_slope = right[0] - right[1]
            denominator = left_slope - right_slope
            if denominator == 0:
                continue
            crossing = (right[1] - left[1]) / denominator
            if 0 <= crossing <= 1:
                candidates.add(crossing)

    def line(action, probability):
        return probability * action[0] + (1 - probability) * action[1]

    def dual(probability):
        return sum((max(line(action, probability) for action in component)
                    for component in pairs), Fraction(0))

    nature_probability = min(candidates, key=lambda p: (dual(p), p))
    value = dual(nature_probability)
    tied = tuple(
        tuple(i for i, action in enumerate(component)
              if line(action, nature_probability)
              == max(line(candidate, nature_probability) for candidate in component))
        for component in pairs
    )

    reachable = {Fraction(0): ()}
    for t, actions in enumerate(tied):
        updated = {}
        for total, prefix in reachable.items():
            for action in actions:
                delta = pairs[t][action][0] - pairs[t][action][1]
                updated.setdefault(total + delta, prefix + (action,))
        if len(updated) > int(max_delta_states):
            raise ValueError("exact tied-delta state limit exceeded")
        reachable = updated

    pure = reachable.get(Fraction(0), ()) if 0 < nature_probability < 1 else ()
    if pure:
        joint = ((pure, Fraction(1)),)
        strict = False
    else:
        low_delta = min(reachable)
        high_delta = max(reachable)
        low = reachable[low_delta]
        high = reachable[high_delta]
        if nature_probability == 0:
            if high_delta < 0:
                raise RuntimeError("invalid left-boundary dual certificate")
            joint = ((high, Fraction(1)),)
            pure = high
            strict = False
        elif nature_probability == 1:
            if low_delta > 0:
                raise RuntimeError("invalid right-boundary dual certificate")
            joint = ((low, Fraction(1)),)
            pure = low
            strict = False
        else:
            if not low_delta < 0 < high_delta:
                raise RuntimeError("interior dual minimizer lacks bracketing responses")
            low_mass = high_delta / (high_delta - low_delta)
            joint = ((low, low_mass), (high, 1 - low_mass))
            strict = True

    realized = tuple(
        sum((mass * sum((pairs[t][actions[t]][scenario]
                         for t in range(len(pairs))), Fraction(0))
             for actions, mass in joint), Fraction(0))
        for scenario in range(2)
    )
    expanded = 1
    for component in pairs:
        expanded *= len(component)
    valid = (
        sum((mass for _, mass in joint), Fraction(0)) == 1
        and all(mass > 0 for _, mass in joint)
        and min(realized) == value
        and len(joint) <= 2
        and strict == (0 < nature_probability < 1 and not pure)
    )
    return TwoVertexAdditiveRobustPlan(
        pairs, joint, value, nature_probability, strict, pure, expanded,
        len(candidates), 2, valid,
        "two_vertex_additive_envelope_certificate",
    )


def _three_vertex_policy(active, value):
    """Find an exact support-at-most-three policy over active joint responses."""
    for actions, payoff in active:
        if min(payoff) >= value:
            return ((actions, Fraction(1)),)

    for left, right in combinations(active, 2):
        low, high = Fraction(0), Fraction(1)
        feasible = True
        for scenario in range(3):
            delta = left[1][scenario] - right[1][scenario]
            rhs = value - right[1][scenario]
            if delta > 0:
                low = max(low, rhs / delta)
            elif delta < 0:
                high = min(high, rhs / delta)
            elif rhs > 0:
                feasible = False
        if feasible and low <= high and high >= 0 and low <= 1:
            weight = max(Fraction(0), low)
            if weight <= min(Fraction(1), high):
                result = []
                if weight:
                    result.append((left[0], weight))
                if weight < 1:
                    result.append((right[0], 1 - weight))
                if result:
                    return tuple(result)

    for first, second, third in combinations(active, 3):
        inequalities = [
            ((Fraction(-1), Fraction(0)), Fraction(0)),
            ((Fraction(0), Fraction(-1)), Fraction(0)),
            ((Fraction(1), Fraction(1)), Fraction(1)),
        ]
        for scenario in range(3):
            a = first[1][scenario] - third[1][scenario]
            b = second[1][scenario] - third[1][scenario]
            inequalities.append(((-a, -b), third[1][scenario] - value))
        for i, j in combinations(range(len(inequalities)), 2):
            point = _solve_fraction_system(
                (inequalities[i][0], inequalities[j][0]),
                (inequalities[i][1], inequalities[j][1]),
            )
            if point is None or any(
                row[0] * point[0] + row[1] * point[1] > rhs
                for row, rhs in inequalities
            ):
                continue
            weights = (point[0], point[1], 1 - point[0] - point[1])
            result = tuple(
                (entry[0], weight)
                for entry, weight in zip((first, second, third), weights)
                if weight > 0
            )
            if result:
                return result
    raise RuntimeError("dual optimum lacks a support-at-most-three primal witness")


def synthesize_three_vertex_additive_plan(
    component_payoff_triples,
    *,
    payoff_additive_certified: bool,
    max_active_joint_actions: int = 500_000,
) -> ThreeVertexAdditiveRobustPlan:
    """Solve an additive three-scenario game by an exact line arrangement.

    Nature's dual is a convex piecewise-affine function on a triangle. Its
    minimum is attained at a triangle/arrangement vertex generated solely by
    component-local action ties. Policy recovery enumerates only actions tied
    at the minimizing point and fails closed above the configured cap.
    """
    if not payoff_additive_certified:
        raise ValueError("a certificate that payoff is additive is required")
    if not component_payoff_triples:
        raise ValueError("at least one component is required")
    triples = tuple(
        tuple(tuple(Fraction(value) for value in action) for action in component)
        for component in component_payoff_triples
    )
    if any(not component or any(len(action) != 3 for action in component)
           for component in triples):
        raise ValueError("each component action must have three scenario payoffs")

    lines = set()
    for component in triples:
        for left, right in combinations(component, 2):
            alpha = (left[0] - left[2]) - (right[0] - right[2])
            beta = (left[1] - left[2]) - (right[1] - right[2])
            gamma = right[2] - left[2]
            if alpha or beta:
                lines.add((alpha, beta, gamma))

    def inside(point):
        return point[0] >= 0 and point[1] >= 0 and sum(point) <= 1

    candidates = {(Fraction(0), Fraction(0)),
                  (Fraction(1), Fraction(0)),
                  (Fraction(0), Fraction(1))}
    for alpha, beta, gamma in lines:
        if beta:
            point = (Fraction(0), gamma / beta)
            if inside(point):
                candidates.add(point)
        if alpha:
            point = (gamma / alpha, Fraction(0))
            if inside(point):
                candidates.add(point)
        if alpha != beta:
            x = (gamma - beta) / (alpha - beta)
            point = (x, 1 - x)
            if inside(point):
                candidates.add(point)
    for left, right in combinations(lines, 2):
        point = _solve_fraction_system(
            ((left[0], left[1]), (right[0], right[1])),
            (left[2], right[2]),
        )
        if point is not None and inside(point):
            candidates.add(point)

    def plane(action, point):
        x, y = point
        return x * action[0] + y * action[1] + (1 - x - y) * action[2]

    def dual(point):
        return sum((max(plane(action, point) for action in component)
                    for component in triples), Fraction(0))

    nature_point = min(candidates, key=lambda point: (dual(point), point))
    value = dual(nature_point)
    tied = tuple(
        tuple(i for i, action in enumerate(component)
              if plane(action, nature_point)
              == max(plane(candidate, nature_point) for candidate in component))
        for component in triples
    )
    active_count = 1
    for actions in tied:
        active_count *= len(actions)
    if active_count > int(max_active_joint_actions):
        raise ValueError("exact tied joint-action limit exceeded")

    active = []
    for actions in product(*tied):
        payoff = tuple(
            sum((triples[t][actions[t]][scenario] for t in range(len(triples))),
                Fraction(0))
            for scenario in range(3)
        )
        active.append((tuple(actions), payoff))
    joint = _three_vertex_policy(tuple(active), value)
    realized = tuple(
        sum((mass * sum((triples[t][actions[t]][scenario]
                         for t in range(len(triples))), Fraction(0))
             for actions, mass in joint), Fraction(0))
        for scenario in range(3)
    )
    expanded = 1
    for component in triples:
        expanded *= len(component)
    nature = (nature_point[0], nature_point[1], 1 - sum(nature_point))
    valid = (
        sum((mass for _, mass in joint), Fraction(0)) == 1
        and all(mass > 0 for _, mass in joint)
        and min(realized) == value
        and len(joint) <= 3
        and sum(nature) == 1
        and all(probability >= 0 for probability in nature)
    )
    return ThreeVertexAdditiveRobustPlan(
        triples, joint, value, nature, len(joint) > 1, expanded, len(lines),
        len(candidates), 3, valid,
        "three_vertex_additive_arrangement_certificate",
    )


def _fixed_scenario_policy(active, value, scenario_count):
    """Return an exact primal witness with support at most scenario_count."""
    for support_size in range(1, scenario_count + 1):
        for selected in combinations(active, support_size):
            if support_size == 1:
                if min(selected[0][1]) >= value:
                    return ((selected[0][0], Fraction(1)),)
                continue
            dimension = support_size - 1
            last = selected[-1][1]
            inequalities = []
            for i in range(dimension):
                row = [Fraction(0)] * dimension
                row[i] = -1
                inequalities.append((tuple(row), Fraction(0)))
            inequalities.append((tuple(Fraction(1) for _ in range(dimension)),
                                  Fraction(1)))
            for scenario in range(scenario_count):
                row = tuple(
                    -(selected[i][1][scenario] - last[scenario])
                    for i in range(dimension)
                )
                inequalities.append((row, last[scenario] - value))
            for boundary in combinations(range(len(inequalities)), dimension):
                point = _solve_fraction_system(
                    tuple(inequalities[i][0] for i in boundary),
                    tuple(inequalities[i][1] for i in boundary),
                )
                if point is None or any(
                    sum((row[i] * point[i] for i in range(dimension)),
                        Fraction(0)) > rhs
                    for row, rhs in inequalities
                ):
                    continue
                weights = tuple(point) + (Fraction(1) - sum(point, Fraction(0)),)
                result = tuple(
                    (entry[0], weight)
                    for entry, weight in zip(selected, weights)
                    if weight > 0
                )
                if result:
                    return result
    raise RuntimeError("dual optimum lacks a sparse primal witness")


def _fixed_scenario_marginal_policy(
    vectors, tied, value, scenario_count, max_marginal_variables,
):
    """Recover an exact policy from a numerically proposed marginal LP basis.

    HiGHS is used only to propose a sparse basis.  Every returned probability
    is reconstructed by ``_solve_fraction_system`` and accepted only after an
    exact rational replay of all simplex and scenario inequalities.
    """
    flat = tuple(
        (component, action, vectors[component][action])
        for component, actions in enumerate(tied)
        for action in actions
    )
    variable_count = len(flat)
    if variable_count > int(max_marginal_variables):
        raise ValueError("exact marginal variable limit exceeded")

    objective = np.arange(1, variable_count + 1, dtype=float)
    scenario_rows = np.asarray([
        [-float(payoff[scenario]) for _, _, payoff in flat]
        for scenario in range(scenario_count)
    ])
    component_rows = np.asarray([
        [float(component == target) for component, _, _ in flat]
        for target in range(len(vectors))
    ])
    proposed = linprog(
        objective,
        A_ub=scenario_rows,
        b_ub=np.full(scenario_count, -float(value)),
        A_eq=component_rows,
        b_eq=np.ones(len(vectors)),
        bounds=(0, None),
        method="highs-ds",
    )
    if not proposed.success:
        raise RuntimeError("marginal policy basis proposal failed")

    supports = []
    for tolerance in (1e-7, 1e-9, 1e-11, 1e-13):
        support = tuple(i for i, probability in enumerate(proposed.x)
                        if probability > tolerance)
        if support not in supports:
            supports.append(support)

    component_count = len(vectors)
    for support in supports:
        active_scenarios = len(support) - component_count
        if active_scenarios < 0 or active_scenarios > scenario_count - 1:
            continue
        for scenarios in combinations(range(scenario_count), active_scenarios):
            rows = []
            rhs = []
            for target in range(component_count):
                rows.append(tuple(
                    Fraction(int(flat[index][0] == target)) for index in support
                ))
                rhs.append(Fraction(1))
            for scenario in scenarios:
                rows.append(tuple(flat[index][2][scenario] for index in support))
                rhs.append(value)
            probabilities = _solve_fraction_system(tuple(rows), tuple(rhs))
            if probabilities is None or any(probability < 0 for probability in probabilities):
                continue

            marginals = [[Fraction(0) for _ in component]
                         for component in vectors]
            for index, probability in zip(support, probabilities):
                component, action, _ = flat[index]
                marginals[component][action] = probability
            marginals = tuple(tuple(marginal) for marginal in marginals)
            if any(sum(marginal, Fraction(0)) != 1 for marginal in marginals):
                continue
            realized = tuple(
                sum((marginals[t][action] * vectors[t][action][scenario]
                     for t in range(component_count)
                     for action in range(len(vectors[t]))), Fraction(0))
                for scenario in range(scenario_count)
            )
            if min(realized) < value:
                continue

            joint = _greedy_common_mass_coupling(marginals)
            support_bound = 1 + sum(
                sum(probability > 0 for probability in marginal) - 1
                for marginal in marginals
            )
            if support_bound > scenario_count or len(joint) > support_bound:
                continue
            return marginals, joint, variable_count, support_bound
    raise RuntimeError("numerical marginal basis lacked an exact rational certificate")


def _fixed_scenario_pure_witness(vectors, tied, value, max_states):
    """Decide pure optimality by exact distinct cumulative-payoff states."""
    zero = (Fraction(0),) * len(vectors[0][0])
    states = {zero}
    peak = 1
    for component, actions in enumerate(tied):
        states = {
            tuple(state[scenario] + vectors[component][action][scenario]
                  for scenario in range(len(zero)))
            for state in states for action in actions
        }
        peak = max(peak, len(states))
        if len(states) > int(max_states):
            raise ValueError("exact pure-payoff state limit exceeded")
    return any(min(state) >= value for state in states), peak


def _fraction_matrix_rank(rows):
    """Return exact row rank for a rectangular rational matrix."""
    matrix = [[Fraction(value) for value in row] for row in rows]
    if not matrix:
        return 0
    width = len(matrix[0])
    rank = 0
    for column in range(width):
        pivot = next((row for row in range(rank, len(matrix))
                      if matrix[row][column] != 0), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][column]
        matrix[rank] = [value / scale for value in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank or matrix[row][column] == 0:
                continue
            scale = matrix[row][column]
            matrix[row] = [matrix[row][item] - scale * matrix[rank][item]
                           for item in range(width)]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def reconstruct_feature_span_scenario_payoffs(
    feature_rows,
    scenario_oracle,
    *,
    payoff_in_feature_span_certified: bool,
) -> FeatureSpanScenarioReconstruction:
    """Recover all payoffs using one query per independent feature row."""
    if not payoff_in_feature_span_certified:
        raise ValueError("a certificate that payoffs lie in the feature span is required")
    features = tuple(
        tuple(Fraction(value) for value in row)
        for row in feature_rows
    )
    if not features or not features[0]:
        raise ValueError("at least one nonempty feature row is required")
    width = len(features[0])
    if any(len(row) != width for row in features):
        raise ValueError("feature rows must share one width")

    query_indices = []
    basis = []
    for index, row in enumerate(features):
        if _fraction_matrix_rank(tuple(basis) + (row,)) > len(basis):
            query_indices.append(index)
            basis.append(row)
    rank = len(basis)
    if rank == 0:
        raise ValueError("feature rows have zero rank")
    pivots = next((columns for columns in combinations(range(width), rank)
                   if _solve_fraction_system(
                       tuple(tuple(basis[row][column] for column in columns)
                             for row in range(rank)),
                       (Fraction(0),) * rank,
                   ) is not None), None)
    if pivots is None:
        raise RuntimeError("feature-row basis lacks exact pivot columns")
    pivot_matrix = tuple(
        tuple(basis[row][column] for row in range(rank))
        for column in pivots
    )
    row_weights = []
    for feature in features:
        weights = _solve_fraction_system(
            pivot_matrix,
            tuple(feature[column] for column in pivots),
        )
        if weights is None or any(
            sum((weights[row] * basis[row][column] for row in range(rank)),
                Fraction(0)) != feature[column]
            for column in range(width)
        ):
            raise RuntimeError("feature row failed exact span reconstruction")
        row_weights.append(weights)

    queried = []
    for index in query_indices:
        response = tuple(
            tuple(Fraction(value) for value in component)
            for component in scenario_oracle(index)
        )
        if not response or any(not component for component in response):
            raise ValueError("the scenario oracle returned an empty payoff shape")
        queried.append(response)
    shape = tuple(len(component) for component in queried[0])
    if any(tuple(len(component) for component in response) != shape
           for response in queried):
        raise ValueError("the scenario oracle returned inconsistent payoff shapes")

    reconstructed = tuple(
        tuple(tuple(
            sum((weights[position] * queried[position][component][action]
                 for position in range(rank)), Fraction(0))
            for weights in row_weights
        ) for action in range(action_count))
        for component, action_count in enumerate(shape)
    )
    valid = (
        len(query_indices) == rank
        and all(
            reconstructed[component][action][scenario]
            == queried[position][component][action]
            for position, scenario in enumerate(query_indices)
            for component in range(len(shape))
            for action in range(shape[component])
        )
    )
    return FeatureSpanScenarioReconstruction(
        component_payoff_vectors=reconstructed,
        feature_rows=features,
        query_indices=tuple(query_indices),
        pivot_columns=tuple(pivots),
        feature_rank=rank,
        feature_width=width,
        scenario_count=len(features),
        query_count=len(query_indices),
        certificate_valid=valid,
        reason="exact_feature_row_span_reconstruction_certificate",
    )


def reconstruct_affine_scenario_payoffs(
    scenario_coordinates,
    scenario_oracle,
    *,
    payoff_affine_certified: bool,
    max_dimension: int = 3,
) -> AffineScenarioReconstruction:
    """Reconstruct every local payoff using exactly d+1 scenario queries.

    The certificate is semantic and external: observations at d+1 points
    cannot themselves prove affinity elsewhere. Given that certificate and
    known rational descriptors spanning Q^d, exact interpolation is sufficient.
    """
    if not payoff_affine_certified:
        raise ValueError("a certificate that payoffs are affine is required")
    coordinates = tuple(
        tuple(Fraction(value) for value in point)
        for point in scenario_coordinates
    )
    if not coordinates:
        raise ValueError("at least one scenario descriptor is required")
    dimension = len(coordinates[0])
    if not 1 <= dimension <= int(max_dimension):
        raise ValueError("descriptor dimension exceeds the certified range")
    if any(len(point) != dimension for point in coordinates):
        raise ValueError("scenario descriptors must share one dimension")
    if len(coordinates) < dimension + 1:
        raise ValueError("too few scenarios to span the descriptor dimension")

    augmented = tuple((Fraction(1),) + point for point in coordinates)
    query_indices = None
    for indices in combinations(range(len(coordinates)), dimension + 1):
        matrix = tuple(augmented[index] for index in indices)
        if _solve_fraction_system(
            matrix,
            (Fraction(0),) * (dimension + 1),
        ) is not None:
            query_indices = tuple(indices)
            break
    if query_indices is None:
        raise ValueError("scenario descriptors do not affinely span their dimension")

    queried = []
    for index in query_indices:
        response = tuple(
            tuple(Fraction(value) for value in component)
            for component in scenario_oracle(index)
        )
        if not response or any(not component for component in response):
            raise ValueError("the scenario oracle returned an empty payoff shape")
        queried.append(response)
    shape = tuple(len(component) for component in queried[0])
    if any(tuple(len(component) for component in response) != shape
           for response in queried):
        raise ValueError("the scenario oracle returned inconsistent payoff shapes")

    basis_matrix = tuple(augmented[index] for index in query_indices)
    components = []
    for component_index, action_count in enumerate(shape):
        actions = []
        for action_index in range(action_count):
            observations = tuple(
                response[component_index][action_index]
                for response in queried
            )
            coefficients = _solve_fraction_system(basis_matrix, observations)
            if coefficients is None:
                raise RuntimeError("affine interpolation basis became singular")
            actions.append(tuple(
                sum((coefficients[position] * row[position]
                     for position in range(dimension + 1)), Fraction(0))
                for row in augmented
            ))
        components.append(tuple(actions))
    reconstructed = tuple(components)
    valid = (
        len(query_indices) == dimension + 1
        and all(
            reconstructed[component][action][scenario]
            == queried[position][component][action]
            for position, scenario in enumerate(query_indices)
            for component in range(len(shape))
            for action in range(shape[component])
        )
    )
    return AffineScenarioReconstruction(
        component_payoff_vectors=reconstructed,
        scenario_coordinates=coordinates,
        query_indices=query_indices,
        descriptor_dimension=dimension,
        scenario_count=len(coordinates),
        query_count=len(query_indices),
        certificate_valid=valid,
        reason="exact_affine_scenario_interpolation_certificate",
    )


def synthesize_rank_one_scenario_quotient_plan(
    component_payoff_vectors,
    *,
    payoff_additive_certified: bool,
) -> RankOneScenarioQuotientPlan:
    """Collapse arbitrarily many affine-rank-one scenarios to two endpoints.

    If every component-local payoff profile is affine in one shared scenario
    coordinate, every additive joint payoff is affine in that coordinate too.
    Nature mixtures therefore range over an interval, whose two endpoints are
    sufficient and necessary for exact minimax planning.
    """
    if not payoff_additive_certified:
        raise ValueError("a certificate that payoff is additive is required")
    if not component_payoff_vectors:
        raise ValueError("at least one component is required")
    vectors = tuple(
        tuple(tuple(Fraction(value) for value in action) for action in component)
        for component in component_payoff_vectors
    )
    if any(not component or not component[0] for component in vectors):
        raise ValueError("every component needs at least one nonempty action")
    scenario_count = len(vectors[0][0])
    if scenario_count < 2:
        raise ValueError("at least two scenarios are required")
    if any(len(action) != scenario_count
           for component in vectors for action in component):
        raise ValueError("all component actions must share one scenario count")

    profiles = tuple(action for component in vectors for action in component)
    anchor = next((profile for profile in profiles
                   if any(value != profile[0] for value in profile[1:])), None)
    if anchor is None:
        coordinates = (Fraction(0),) * scenario_count
        affine_dimension = 0
        lower = upper = 0
    else:
        coordinates = anchor
        affine_dimension = 1
        base = 0
        witness = next(i for i in range(1, scenario_count)
                       if coordinates[i] != coordinates[base])
        denominator = coordinates[witness] - coordinates[base]
        for profile in profiles:
            slope = (profile[witness] - profile[base]) / denominator
            intercept = profile[base] - slope * coordinates[base]
            if any(intercept + slope * coordinates[i] != profile[i]
                   for i in range(scenario_count)):
                raise ValueError("scenario payoff columns have affine dimension above one")
        lower = min(range(scenario_count), key=lambda i: (coordinates[i], i))
        upper = min(range(scenario_count), key=lambda i: (-coordinates[i], i))

    pairs = tuple(
        tuple((action[lower], action[upper]) for action in component)
        for component in vectors
    )
    reduced = synthesize_two_vertex_additive_plan(
        pairs,
        payoff_additive_certified=True,
    )
    nature = [Fraction(0)] * scenario_count
    if lower == upper:
        nature[lower] = 1
        effective_scenarios = 1
    else:
        nature[lower] = reduced.nature_probability
        nature[upper] = 1 - reduced.nature_probability
        effective_scenarios = 2
    realized = tuple(
        sum((mass * sum((vectors[t][actions[t]][scenario]
                         for t in range(len(vectors))), Fraction(0))
             for actions, mass in reduced.joint_actions), Fraction(0))
        for scenario in range(scenario_count)
    )
    expanded = 1
    for component in vectors:
        expanded *= len(component)
    valid = (
        reduced.certificate_valid
        and sum(nature, Fraction(0)) == 1
        and min(realized) == reduced.minimax_value
        and len(reduced.joint_actions) <= 2
        and all(mass > 0 for _, mass in reduced.joint_actions)
    )
    return RankOneScenarioQuotientPlan(
        component_payoff_vectors=vectors,
        scenario_coordinates=tuple(coordinates),
        endpoint_indices=(lower, upper),
        affine_dimension=affine_dimension,
        effective_scenario_count=effective_scenarios,
        joint_actions=reduced.joint_actions,
        minimax_value=reduced.minimax_value,
        nature_probabilities=tuple(nature),
        strict_randomization_necessary=reduced.strict_randomization_necessary,
        scenario_count=scenario_count,
        expanded_action_count=expanded,
        support_bound=2,
        certificate_valid=valid,
        reason="rank_one_scenario_quotient_certificate",
    )


def synthesize_rank_two_scenario_hull_plan(
    component_payoff_vectors,
    *,
    payoff_additive_certified: bool,
    max_extreme_scenarios: int = 8,
) -> RankTwoScenarioHullPlan:
    """Delete non-extreme columns from an exact affine-rank-two scenario set."""
    if not payoff_additive_certified:
        raise ValueError("a certificate that payoff is additive is required")
    if not component_payoff_vectors:
        raise ValueError("at least one component is required")
    vectors = tuple(
        tuple(tuple(Fraction(value) for value in action) for action in component)
        for component in component_payoff_vectors
    )
    if any(not component or not component[0] for component in vectors):
        raise ValueError("every component needs at least one nonempty action")
    scenario_count = len(vectors[0][0])
    if scenario_count < 3:
        raise ValueError("affine rank two requires at least three scenarios")
    if any(len(action) != scenario_count
           for component in vectors for action in component):
        raise ValueError("all component actions must share one scenario count")

    profiles = tuple(action for component in vectors for action in component)
    columns = tuple(
        tuple(profile[scenario] for profile in profiles)
        for scenario in range(scenario_count)
    )
    origin = columns[0]
    differences = tuple(
        tuple(column[row] - origin[row] for row in range(len(origin)))
        for column in columns
    )
    first = next((difference for difference in differences if any(difference)), None)
    if first is None:
        raise ValueError("scenario payoff columns have affine dimension below two")
    second = None
    pivots = None
    for candidate in differences:
        for left in range(len(first)):
            for right in range(left + 1, len(first)):
                determinant = (
                    first[left] * candidate[right]
                    - first[right] * candidate[left]
                )
                if determinant:
                    second = candidate
                    pivots = (left, right)
                    break
            if second is not None:
                break
        if second is not None:
            break
    if second is None or pivots is None:
        raise ValueError("scenario payoff columns have affine dimension below two")

    left, right = pivots
    determinant = first[left] * second[right] - first[right] * second[left]
    for difference in differences:
        alpha = (difference[left] * second[right]
                 - difference[right] * second[left]) / determinant
        beta = (first[left] * difference[right]
                - first[right] * difference[left]) / determinant
        if any(alpha * first[row] + beta * second[row] != difference[row]
               for row in range(len(first))):
            raise ValueError("scenario payoff columns have affine dimension above two")

    coordinates = tuple((difference[left], difference[right])
                        for difference in differences)
    unique = {}
    for index, coordinate in enumerate(coordinates):
        unique.setdefault(coordinate, index)
    points = tuple(sorted((x, y, index) for (x, y), index in unique.items()))

    def cross(origin_point, left_point, right_point):
        return ((left_point[0] - origin_point[0])
                * (right_point[1] - origin_point[1])
                - (left_point[1] - origin_point[1])
                * (right_point[0] - origin_point[0]))

    lower = []
    for point in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper = []
    for point in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    hull = tuple(lower[:-1] + upper[:-1])
    extreme_indices = tuple(point[2] for point in hull)
    if len(extreme_indices) < 3:
        raise RuntimeError("rank-two coordinates produced a degenerate hull")
    if len(extreme_indices) > int(max_extreme_scenarios):
        raise ValueError("rank-two hull exceeds the certified scenario cap")

    reduced_vectors = tuple(
        tuple(tuple(action[index] for index in extreme_indices)
              for action in component)
        for component in vectors
    )
    reduced = synthesize_fixed_scenario_additive_plan(
        reduced_vectors,
        payoff_additive_certified=True,
        max_scenarios=max_extreme_scenarios,
    )
    nature = [Fraction(0)] * scenario_count
    for position, index in enumerate(extreme_indices):
        nature[index] = reduced.nature_probabilities[position]
    realized = tuple(
        sum((mass * sum((vectors[t][actions[t]][scenario]
                         for t in range(len(vectors))), Fraction(0))
             for actions, mass in reduced.joint_actions), Fraction(0))
        for scenario in range(scenario_count)
    )
    expanded = 1
    for component in vectors:
        expanded *= len(component)
    valid = (
        reduced.certificate_valid
        and sum(nature, Fraction(0)) == 1
        and min(realized) == reduced.minimax_value
        and len(reduced.joint_actions) <= len(extreme_indices)
        and all(mass > 0 for _, mass in reduced.joint_actions)
    )
    return RankTwoScenarioHullPlan(
        component_payoff_vectors=vectors,
        projected_coordinates=coordinates,
        extreme_indices=extreme_indices,
        affine_dimension=2,
        effective_scenario_count=len(extreme_indices),
        joint_actions=reduced.joint_actions,
        minimax_value=reduced.minimax_value,
        nature_probabilities=tuple(nature),
        strict_randomization_necessary=reduced.strict_randomization_necessary,
        scenario_count=scenario_count,
        expanded_action_count=expanded,
        support_bound=len(extreme_indices),
        certificate_valid=valid,
        reason="rank_two_scenario_convex_hull_certificate",
    )


def _rational_3d_hull_weights(point, candidates):
    """Return exact Carathéodory weights on at most four candidates."""
    target = tuple(Fraction(value) for value in point)
    others = tuple(tuple(Fraction(value) for value in item)
                   for item in candidates)
    equations_rhs = target + (Fraction(1),)
    for support_size in range(1, min(4, len(others)) + 1):
        for indices in combinations(range(len(others)), support_size):
            support = tuple(others[index] for index in indices)
            equations = tuple(
                tuple(vertex[coordinate] for vertex in support)
                for coordinate in range(3)
            ) + ((Fraction(1),) * support_size,)
            for selected in combinations(range(4), support_size):
                weights = _solve_fraction_system(
                    tuple(equations[index] for index in selected),
                    tuple(equations_rhs[index] for index in selected),
                )
                if weights is None or any(weight < 0 for weight in weights):
                    continue
                if all(
                    sum((equations[row][column] * weights[column]
                         for column in range(support_size)), Fraction(0))
                    == equations_rhs[row]
                    for row in range(4)
                ):
                    result = [Fraction(0)] * len(others)
                    for index, weight in zip(indices, weights, strict=True):
                        result[index] = weight
                    return tuple(result)
    return None


def _point_in_rational_3d_hull(point, candidates):
    """Exact Carathéodory membership using supports of size at most four."""
    return _rational_3d_hull_weights(point, candidates) is not None


def compress_rank_three_nature_certificate(
    projected_coordinates,
    nature_probabilities,
):
    """Preserve an exact rank-three barycenter on at most four scenarios."""
    points = tuple(
        tuple(Fraction(value) for value in point)
        for point in projected_coordinates
    )
    weights = tuple(Fraction(value) for value in nature_probabilities)
    if not points or len(points) != len(weights):
        raise ValueError("coordinates and nature weights must have equal nonzero length")
    if any(len(point) != 3 for point in points):
        raise ValueError("rank-three coordinates must have exactly three entries")
    if any(weight < 0 for weight in weights) \
            or sum(weights, Fraction(0)) != 1:
        raise ValueError("nature weights must be a probability distribution")
    barycenter = tuple(
        sum((weights[index] * point[coordinate]
             for index, point in enumerate(points)), Fraction(0))
        for coordinate in range(3)
    )
    compressed = _rational_3d_hull_weights(barycenter, points)
    if compressed is None:
        raise RuntimeError("rank-three nature certificate compression failed")
    compressed_barycenter = tuple(
        sum((compressed[index] * point[coordinate]
             for index, point in enumerate(points)), Fraction(0))
        for coordinate in range(3)
    )
    if sum(compressed, Fraction(0)) != 1 \
            or any(weight < 0 for weight in compressed) \
            or sum(weight > 0 for weight in compressed) > 4 \
            or compressed_barycenter != barycenter:
        raise RuntimeError("invalid rank-three nature compression certificate")
    return compressed


def synthesize_rank_three_scenario_polytope_plan(
    component_payoff_vectors,
    *,
    payoff_additive_certified: bool,
    max_extreme_scenarios: int = 8,
) -> RankThreeScenarioPolytopePlan:
    """Delete non-vertex columns from an exact affine-rank-three scenario set."""
    if not payoff_additive_certified:
        raise ValueError("a certificate that payoff is additive is required")
    if not component_payoff_vectors:
        raise ValueError("at least one component is required")
    vectors = tuple(
        tuple(tuple(Fraction(value) for value in action) for action in component)
        for component in component_payoff_vectors
    )
    if any(not component or not component[0] for component in vectors):
        raise ValueError("every component needs at least one nonempty action")
    scenario_count = len(vectors[0][0])
    if scenario_count < 4:
        raise ValueError("affine rank three requires at least four scenarios")
    if any(len(action) != scenario_count
           for component in vectors for action in component):
        raise ValueError("all component actions must share one scenario count")

    profiles = tuple(action for component in vectors for action in component)
    columns = tuple(
        tuple(profile[scenario] for profile in profiles)
        for scenario in range(scenario_count)
    )
    origin = columns[0]
    differences = tuple(
        tuple(column[row] - origin[row] for row in range(len(origin)))
        for column in columns
    )

    basis = None
    pivots = None
    for candidate_basis in combinations(differences[1:], 3):
        for candidate_pivots in combinations(range(len(origin)), 3):
            matrix = tuple(
                tuple(candidate_basis[column][row] for column in range(3))
                for row in candidate_pivots
            )
            if _solve_fraction_system(matrix, (Fraction(0),) * 3) is not None:
                basis = candidate_basis
                pivots = candidate_pivots
                break
        if basis is not None:
            break
    if basis is None or pivots is None:
        raise ValueError("scenario payoff columns have affine dimension below three")

    pivot_matrix = tuple(
        tuple(basis[column][row] for column in range(3))
        for row in pivots
    )
    coordinates = []
    for difference in differences:
        coefficients = _solve_fraction_system(
            pivot_matrix,
            tuple(difference[row] for row in pivots),
        )
        if coefficients is None or any(
            sum((coefficients[column] * basis[column][row]
                 for column in range(3)), Fraction(0)) != difference[row]
            for row in range(len(origin))
        ):
            raise ValueError("scenario payoff columns have affine dimension above three")
        coordinates.append(tuple(coefficients))
    projected = tuple(coordinates)

    unique: dict[tuple[Fraction, Fraction, Fraction], int] = {}
    for index, coordinate in enumerate(projected):
        unique.setdefault(coordinate, index)
    unique_points = tuple(unique)
    try:
        proposal = ConvexHull(np.asarray(unique_points, dtype=float))
    except QhullError as error:
        raise ValueError("rank-three polytope proposal failed safely") from error
    proposed = tuple(unique_points[index] for index in proposal.vertices)
    extreme_coordinates = tuple(
        point for point in proposed
        if not _point_in_rational_3d_hull(
            point,
            tuple(candidate for candidate in proposed if candidate != point),
        )
    )
    if any(
        not _point_in_rational_3d_hull(point, extreme_coordinates)
        for point in unique_points if point not in extreme_coordinates
    ):
        raise RuntimeError("floating hull proposal failed exact coverage certification")
    extreme_indices = tuple(unique[point] for point in extreme_coordinates)
    if len(extreme_indices) < 4:
        raise RuntimeError("rank-three coordinates produced a degenerate polytope")
    if len(extreme_indices) > int(max_extreme_scenarios):
        raise ValueError("rank-three polytope exceeds the certified scenario cap")

    reduced_vectors = tuple(
        tuple(tuple(action[index] for index in extreme_indices)
              for action in component)
        for component in vectors
    )
    reduced = synthesize_fixed_scenario_additive_plan(
        reduced_vectors,
        payoff_additive_certified=True,
        max_scenarios=max_extreme_scenarios,
    )
    reduced_nature = tuple(reduced.nature_probabilities)
    compressed_nature = compress_rank_three_nature_certificate(
        extreme_coordinates,
        reduced_nature,
    )
    nature = [Fraction(0)] * scenario_count
    for position, index in enumerate(extreme_indices):
        nature[index] = compressed_nature[position]
    original_expectations = tuple(
        sum((reduced_nature[position] * profile[index]
             for position, index in enumerate(extreme_indices)), Fraction(0))
        for profile in profiles
    )
    compressed_expectations = tuple(
        sum((nature[index] * profile[index] for index in range(scenario_count)),
            Fraction(0))
        for profile in profiles
    )
    realized = tuple(
        sum((mass * sum((vectors[t][actions[t]][scenario]
                         for t in range(len(vectors))), Fraction(0))
             for actions, mass in reduced.joint_actions), Fraction(0))
        for scenario in range(scenario_count)
    )
    expanded = 1
    for component in vectors:
        expanded *= len(component)
    valid = (
        reduced.certificate_valid
        and sum(nature, Fraction(0)) == 1
        and min(realized) == reduced.minimax_value
        and len(reduced.joint_actions) <= len(extreme_indices)
        and all(mass > 0 for _, mass in reduced.joint_actions)
        and sum(weight > 0 for weight in nature) <= 4
        and original_expectations == compressed_expectations
        and all(nature[index] == 0
                for index in range(scenario_count)
                if index not in extreme_indices)
    )
    return RankThreeScenarioPolytopePlan(
        component_payoff_vectors=vectors,
        projected_coordinates=projected,
        extreme_indices=extreme_indices,
        affine_dimension=3,
        effective_scenario_count=len(extreme_indices),
        joint_actions=reduced.joint_actions,
        minimax_value=reduced.minimax_value,
        nature_probabilities=tuple(nature),
        strict_randomization_necessary=reduced.strict_randomization_necessary,
        scenario_count=scenario_count,
        expanded_action_count=expanded,
        support_bound=4,
        certificate_valid=valid,
        reason="rank_three_scenario_convex_polytope_certificate",
    )


def synthesize_fixed_scenario_additive_plan(
    component_payoff_vectors,
    *,
    payoff_additive_certified: bool,
    max_scenarios: int = 8,
    max_boundary_combinations: int = 2_000_000,
    max_active_joint_actions: int | None = None,
    max_marginal_variables: int = 500_000,
    max_pure_payoff_states: int = 500_000,
) -> FixedScenarioAdditiveRobustPlan:
    """Solve a certified additive game at any bounded fixed scenario count.

    Value computation enumerates vertices of the component-local tie
    arrangement in the nature simplex.  It never expands Cartesian joint
    actions.  Policy recovery solves over component marginals among actions
    tied at the exact minimizing nature distribution, then couples the exact
    marginals.  ``max_active_joint_actions`` is retained as an ignored legacy
    keyword: the recovery path never enumerates that Cartesian product.
    """
    if not payoff_additive_certified:
        raise ValueError("a certificate that payoff is additive is required")
    if not component_payoff_vectors:
        raise ValueError("at least one component is required")
    vectors = tuple(
        tuple(tuple(Fraction(value) for value in action) for action in component)
        for component in component_payoff_vectors
    )
    if any(not component or not component[0] for component in vectors):
        raise ValueError("every component needs at least one nonempty action")
    scenario_count = len(vectors[0][0])
    if scenario_count < 2 or scenario_count > int(max_scenarios):
        raise ValueError("scenario count is outside the certified fixed-dimensional cap")
    if any(len(action) != scenario_count
           for component in vectors for action in component):
        raise ValueError("all component actions must share one scenario count")

    dimension = scenario_count - 1
    ties = set()
    for component in vectors:
        for left, right in combinations(component, 2):
            row = tuple(
                (left[i] - left[-1]) - (right[i] - right[-1])
                for i in range(dimension)
            )
            rhs = right[-1] - left[-1]
            if any(row):
                ties.add((row, rhs))

    facets = tuple(
        (tuple(Fraction(int(i == j)) for i in range(dimension)), Fraction(0))
        for j in range(dimension)
    ) + ((tuple(Fraction(1) for _ in range(dimension)), Fraction(1)),)
    boundaries = tuple(sorted(ties)) + facets
    boundary_combinations = comb(len(boundaries), dimension)
    if boundary_combinations > int(max_boundary_combinations):
        raise ValueError("exact arrangement boundary-combination limit exceeded")

    def inside(point):
        return all(value >= 0 for value in point) and sum(point) <= 1

    candidates = set()
    for selected in combinations(boundaries, dimension):
        point = _solve_fraction_system(
            tuple(item[0] for item in selected),
            tuple(item[1] for item in selected),
        )
        if point is not None and inside(point):
            candidates.add(point)
    if not candidates:
        raise RuntimeError("fixed-scenario arrangement has no feasible vertex")

    def affine(action, point):
        return sum((point[i] * action[i] for i in range(dimension)), Fraction(0)) \
            + (1 - sum(point, Fraction(0))) * action[-1]

    def dual(point):
        return sum((max(affine(action, point) for action in component)
                    for component in vectors), Fraction(0))

    nature_point = min(candidates, key=lambda point: (dual(point), point))
    value = dual(nature_point)
    tied = tuple(
        tuple(i for i, action in enumerate(component)
              if affine(action, nature_point)
              == max(affine(candidate, nature_point) for candidate in component))
        for component in vectors
    )
    active_count = 1
    for actions in tied:
        active_count *= len(actions)
    _, joint, marginal_variable_count, marginal_support_bound = \
        _fixed_scenario_marginal_policy(
            vectors, tied, value, scenario_count, max_marginal_variables,
        )
    pure_optimal, pure_payoff_state_count = _fixed_scenario_pure_witness(
        vectors, tied, value, max_pure_payoff_states,
    )
    realized = tuple(
        sum((mass * sum((vectors[t][actions[t]][scenario]
                         for t in range(len(vectors))), Fraction(0))
             for actions, mass in joint), Fraction(0))
        for scenario in range(scenario_count)
    )
    expanded = 1
    for component in vectors:
        expanded *= len(component)
    nature = tuple(nature_point) + (1 - sum(nature_point, Fraction(0)),)
    upper_bound = comb(len(ties) + scenario_count, dimension)
    valid = (
        sum((mass for _, mass in joint), Fraction(0)) == 1
        and all(mass > 0 for _, mass in joint)
        and min(realized) == value
        and len(joint) <= marginal_support_bound <= scenario_count
        and sum(nature) == 1
        and all(probability >= 0 for probability in nature)
        and len(candidates) <= upper_bound
    )
    return FixedScenarioAdditiveRobustPlan(
        component_payoff_vectors=vectors,
        joint_actions=joint,
        minimax_value=value,
        nature_probabilities=nature,
        strict_randomization_necessary=not pure_optimal,
        scenario_count=scenario_count,
        expanded_action_count=expanded,
        tie_hyperplane_count=len(ties),
        arrangement_candidate_count=len(candidates),
        candidate_upper_bound=upper_bound,
        support_bound=scenario_count,
        tied_joint_action_count=active_count,
        marginal_variable_count=marginal_variable_count,
        pure_payoff_state_count=pure_payoff_state_count,
        certificate_valid=valid,
        reason="fixed_scenario_additive_arrangement_marginal_certificate",
    )


def synthesize_four_vertex_additive_plan(
    component_payoff_vectors,
    *,
    payoff_additive_certified: bool,
    max_active_joint_actions: int = 500_000,
) -> FourVertexAdditiveRobustPlan:
    """Solve an additive four-scenario game by a tetrahedral arrangement.

    The dual is convex piecewise affine on a three-dimensional simplex.  A
    minimum is attained at an intersection of three component-local tie or
    simplex-facet hyperplanes, so Cartesian joint actions are unnecessary for
    value computation.
    """
    if not payoff_additive_certified:
        raise ValueError("a certificate that payoff is additive is required")
    if not component_payoff_vectors:
        raise ValueError("at least one component is required")
    vectors = tuple(
        tuple(tuple(Fraction(value) for value in action) for action in component)
        for component in component_payoff_vectors
    )
    if any(not component or any(len(action) != 4 for action in component)
           for component in vectors):
        raise ValueError("each component action must have four scenario payoffs")

    ties = set()
    for component in vectors:
        for left, right in combinations(component, 2):
            row = tuple(
                (left[i] - left[3]) - (right[i] - right[3])
                for i in range(3)
            )
            rhs = right[3] - left[3]
            if any(row):
                ties.add((row, rhs))

    facets = tuple(
        (tuple(Fraction(int(i == j)) for i in range(3)), Fraction(0))
        for j in range(3)
    ) + (
        ((Fraction(1), Fraction(1), Fraction(1)), Fraction(1)),
    )
    boundaries = tuple(sorted(ties)) + facets

    def inside(point):
        return all(value >= 0 for value in point) and sum(point) <= 1

    candidates = set()
    for selected in combinations(boundaries, 3):
        point = _solve_fraction_system(
            tuple(item[0] for item in selected),
            tuple(item[1] for item in selected),
        )
        if point is not None and inside(point):
            candidates.add(point)
    if not candidates:
        raise RuntimeError("tetrahedral arrangement has no feasible vertex")

    def affine(action, point):
        return sum((point[i] * action[i] for i in range(3)), Fraction(0)) \
            + (1 - sum(point, Fraction(0))) * action[3]

    def dual(point):
        return sum((max(affine(action, point) for action in component)
                    for component in vectors), Fraction(0))

    nature_point = min(candidates, key=lambda point: (dual(point), point))
    value = dual(nature_point)
    tied = tuple(
        tuple(i for i, action in enumerate(component)
              if affine(action, nature_point)
              == max(affine(candidate, nature_point) for candidate in component))
        for component in vectors
    )
    active_count = 1
    for actions in tied:
        active_count *= len(actions)
    if active_count > int(max_active_joint_actions):
        raise ValueError("exact tied joint-action limit exceeded")

    active = []
    for actions in product(*tied):
        payoff = tuple(
            sum((vectors[t][actions[t]][scenario] for t in range(len(vectors))),
                Fraction(0))
            for scenario in range(4)
        )
        active.append((tuple(actions), payoff))
    joint = _fixed_scenario_policy(tuple(active), value, 4)
    realized = tuple(
        sum((mass * sum((vectors[t][actions[t]][scenario]
                         for t in range(len(vectors))), Fraction(0))
             for actions, mass in joint), Fraction(0))
        for scenario in range(4)
    )
    expanded = 1
    for component in vectors:
        expanded *= len(component)
    nature = tuple(nature_point) + (1 - sum(nature_point, Fraction(0)),)
    upper_bound = comb(len(ties) + 4, 3)
    valid = (
        sum((mass for _, mass in joint), Fraction(0)) == 1
        and all(mass > 0 for _, mass in joint)
        and min(realized) == value
        and len(joint) <= 4
        and sum(nature) == 1
        and all(probability >= 0 for probability in nature)
        and len(candidates) <= upper_bound
    )
    return FourVertexAdditiveRobustPlan(
        vectors, joint, value, nature, len(joint) > 1, expanded, len(ties),
        len(candidates), upper_bound, 4, valid,
        "four_vertex_additive_arrangement_certificate",
    )


def _zero_bonus_nature_feasibility(matrices, vertices, values):
    """Return lambda on coupled vertices attaining every component value."""
    m = len(vertices)
    if m == 1:
        ok = all(matrix[action][vertices[0][t]] <= values[t]
                 for t, matrix in enumerate(matrices)
                 for action in range(len(matrix)))
        return (Fraction(1),) if ok else ()
    d = m - 1
    inequalities = []
    for i in range(d):
        row = [Fraction(0)] * d
        row[i] = -1
        inequalities.append((tuple(row), Fraction(0)))
    inequalities.append((tuple(Fraction(1) for _ in range(d)), Fraction(1)))
    last = vertices[-1]
    for t, matrix in enumerate(matrices):
        for action in range(len(matrix)):
            base = matrix[action][last[t]]
            row = tuple(matrix[action][vertices[i][t]] - base for i in range(d))
            inequalities.append((row, values[t] - base))
    for selected in combinations(range(len(inequalities)), d):
        x = _solve_fraction_system(
            tuple(inequalities[i][0] for i in selected),
            tuple(inequalities[i][1] for i in selected),
        )
        if x is None:
            continue
        if all(sum((row[i] * x[i] for i in range(d)), Fraction(0)) <= rhs
               for row, rhs in inequalities):
            return tuple(x) + (Fraction(1) - sum(x, Fraction(0)),)
    return ()


def synthesize_coupled_additive_plan(
    component_payoff_matrices,
    ambiguity_vertices,
    *,
    payoff_additive_certified: bool,
    max_active_sets: int = 2_000_000,
) -> CoupledAdditiveRobustPlan:
    """Exact reduced planner for additive payoffs and finite coupled ambiguity."""
    if not payoff_additive_certified:
        raise ValueError("a certificate that payoff is additive is required")
    if not component_payoff_matrices:
        raise ValueError("at least one component payoff matrix is required")
    matrices = tuple(tuple(tuple(Fraction(x) for x in row) for row in raw)
                     for raw in component_payoff_matrices)
    if any(not matrix or not matrix[0] or
           any(len(row) != len(matrix[0]) for row in matrix) for matrix in matrices):
        raise ValueError("component payoff matrices must be nonempty and rectangular")
    if not ambiguity_vertices:
        raise ValueError("at least one coupled ambiguity vertex is required")
    vertices = tuple(tuple(int(i) for i in vertex) for vertex in ambiguity_vertices)
    if len(set(vertices)) != len(vertices):
        raise ValueError("coupled ambiguity vertices must be unique")
    if any(len(vertex) != len(matrices) or
           any(i < 0 or i >= len(matrices[t][0]) for t, i in enumerate(vertex))
           for vertex in vertices):
        raise ValueError("coupled ambiguity vertex is outside a component domain")

    component = tuple(_component_exact_solution(matrix) for matrix in matrices)
    values = tuple(item[1] for item in component)
    baseline = sum(values, Fraction(0))
    offsets, marginal_dimension = [], 0
    for matrix in matrices:
        offsets.append(marginal_dimension)
        marginal_dimension += len(matrix) - 1
    dimension = marginal_dimension + 1

    boundaries = []
    for t, matrix in enumerate(matrices):
        for action in range(len(matrix) - 1):
            row = [Fraction(0)] * dimension
            row[offsets[t] + action] = 1
            boundaries.append((tuple(row), Fraction(0)))
        row = [Fraction(0)] * dimension
        for action in range(len(matrix) - 1):
            row[offsets[t] + action] = 1
        boundaries.append((tuple(row), Fraction(1)))
    for vertex in vertices:
        row = [Fraction(0)] * dimension
        base = Fraction(0)
        for t, matrix in enumerate(matrices):
            last = matrix[-1][vertex[t]]
            base += last
            for action in range(len(matrix) - 1):
                row[offsets[t] + action] -= matrix[action][vertex[t]] - last
        row[-1] = 1
        boundaries.append((tuple(row), base))

    from math import comb
    active_sets = comb(len(boundaries), dimension)
    if active_sets > int(max_active_sets):
        raise ValueError("exact coupled solver active-set limit exceeded")

    candidates = []
    for selected in combinations(range(len(boundaries)), dimension):
        x = _solve_fraction_system(
            tuple(boundaries[i][0] for i in selected),
            tuple(boundaries[i][1] for i in selected),
        )
        if x is None:
            continue
        feasible = True
        for t, matrix in enumerate(matrices):
            marginal = x[offsets[t]:offsets[t] + len(matrix) - 1]
            if any(p < 0 for p in marginal) or sum(marginal, Fraction(0)) > 1:
                feasible = False
                break
        if not feasible:
            continue
        realized = []
        for vertex in vertices:
            payoff = Fraction(0)
            for t, matrix in enumerate(matrices):
                marginal = x[offsets[t]:offsets[t] + len(matrix) - 1]
                payoff += sum((marginal[a] * matrix[a][vertex[t]]
                               for a in range(len(matrix) - 1)), Fraction(0))
                payoff += (1 - sum(marginal, Fraction(0))) * matrix[-1][vertex[t]]
            realized.append(payoff)
        if x[-1] <= min(realized):
            candidates.append((x[-1], x))
    if not candidates:
        raise RuntimeError("coupled marginal LP had no rational vertex")
    value = max(item[0] for item in candidates)
    x = min(item[1] for item in candidates if item[0] == value)
    probabilities = tuple(
        tuple(x[offsets[t]:offsets[t] + len(matrix) - 1])
        + (Fraction(1) - sum(x[offsets[t]:offsets[t] + len(matrix) - 1], Fraction(0)),)
        for t, matrix in enumerate(matrices)
    )
    joint = _greedy_common_mass_coupling(probabilities)
    sizes = tuple(sum(p > 0 for p in marginal) for marginal in probabilities)
    support_bound = 1 + sum(size - 1 for size in sizes)
    realized = tuple(
        sum((mass * sum((matrices[t][actions[t]][vertex[t]]
                         for t in range(len(matrices))), Fraction(0))
             for actions, mass in joint), Fraction(0))
        for vertex in vertices
    )
    bonus = value - baseline
    witness = _zero_bonus_nature_feasibility(matrices, vertices, values)
    expanded = 1
    for matrix in matrices:
        expanded *= len(matrix)
    recovered = tuple(
        tuple(sum((mass for actions, mass in joint if actions[t] == action), Fraction(0))
              for action in range(len(matrices[t])))
        for t in range(len(matrices))
    )
    valid = (
        bonus >= 0 and min(realized) == value and recovered == probabilities
        and sum((mass for _, mass in joint), Fraction(0)) == 1
        and len(joint) <= support_bound
        and (bonus == 0) == bool(witness)
        and (not witness or sum(witness, Fraction(0)) == 1)
    )
    return CoupledAdditiveRobustPlan(
        matrices, vertices, probabilities, joint, value, baseline, bonus,
        bonus == 0, witness, expanded, dimension, support_bound, valid,
        "coupled_additive_marginal_lp_certificate",
    )


def solve_two_vertex_robust_game(
    payoff_matrix: tuple[tuple[Fraction, Fraction], ...],
) -> TwoVertexRobustGame:
    """Solve an arbitrary-action, two-vertex robust game exactly.

    Each action is a point in the two-vertex payoff plane. A strict mixed
    improvement exists exactly when a segment joining points on opposite sides
    of the diagonal crosses it above every pure action's worst-case payoff.
    Thus a maximin plan always has support of size at most two.
    """
    if not payoff_matrix or any(len(row) != 2 for row in payoff_matrix):
        raise ValueError("payoff_matrix must contain nonempty two-entry rows")
    matrix = tuple(tuple(Fraction(value) for value in row) for row in payoff_matrix)
    action_count = len(matrix)
    pure_values = tuple(min(row) for row in matrix)
    pure = max(pure_values)
    pure_index = min(i for i, candidate in enumerate(pure_values) if candidate == pure)

    crossings: list[tuple[Fraction, tuple[int, int], Fraction]] = []
    for left, right in combinations(range(action_count), 2):
        left_delta = matrix[left][0] - matrix[left][1]
        right_delta = matrix[right][0] - matrix[right][1]
        if left_delta * right_delta >= 0:
            continue
        left_weight = right_delta / (right_delta - left_delta)
        if not 0 < left_weight < 1:
            continue
        value = left_weight * matrix[left][0] + (1 - left_weight) * matrix[right][0]
        crossings.append((value, (left, right), left_weight))

    best_crossing = max((item[0] for item in crossings), default=pure)
    probabilities = [Fraction(0) for _ in range(action_count)]
    supported: tuple[int, ...]
    if best_crossing > pure:
        value = best_crossing
        _, supported, left_weight = min(item for item in crossings if item[0] == value)
        probabilities[supported[0]] = left_weight
        probabilities[supported[1]] = 1 - left_weight
    else:
        value = pure
        supported = (pure_index,)
        probabilities[pure_index] = 1

    probability_tuple = tuple(probabilities)
    realized = tuple(sum((
        probability_tuple[i] * matrix[i][vertex]
        for i in range(action_count)
    ), Fraction(0)) for vertex in range(2))
    dual_candidates = {Fraction(0), Fraction(1)}
    for left, right in combinations(range(action_count), 2):
        left_slope = matrix[left][0] - matrix[left][1]
        right_slope = matrix[right][0] - matrix[right][1]
        if left_slope == right_slope:
            continue
        crossing = (matrix[right][1] - matrix[left][1]) / (left_slope - right_slope)
        if 0 <= crossing <= 1:
            dual_candidates.add(crossing)
    dual_scored = tuple((
        max(q * row[0] + (1 - q) * row[1] for row in matrix), q
    ) for q in dual_candidates)
    dual_value = min(candidate[0] for candidate in dual_scored)
    dual_weight = min(candidate[1] for candidate in dual_scored if candidate[0] == dual_value)
    ambiguity_probabilities = (dual_weight, 1 - dual_weight)
    dual_realized = tuple(
        dual_weight * row[0] + (1 - dual_weight) * row[1] for row in matrix
    )
    active = tuple(i for i, payoff in enumerate(realized) if payoff == value)
    gain = value - pure
    valid = (
        sum(probability_tuple) == 1
        and all(probability >= 0 for probability in probability_tuple)
        and min(realized) == value
        and gain >= 0
        and len(supported) <= 2
        and tuple(i for i, probability in enumerate(probability_tuple) if probability > 0)
        == supported
        and ((len(supported) == 2) == (gain > 0))
        and (not gain or realized[0] == realized[1] == value)
        and dual_value == value
        and max(dual_realized) == value
        and sum(ambiguity_probabilities) == 1
        and all(probability >= 0 for probability in ambiguity_probabilities)
    )
    return TwoVertexRobustGame(
        matrix, probability_tuple, ambiguity_probabilities, value, pure, gain, gain > 0,
        supported, active, valid,
    )


def solve_two_action_robust_game(
    payoff_matrix: tuple[tuple[Fraction, ...], tuple[Fraction, ...]],
) -> TwoActionRobustGame:
    """Solve a two-action finite robust game by its exact lower envelope.

    Each ambiguity vertex defines an affine payoff line in the probability of
    action zero.  Strict randomization occurs exactly at a supported interior
    crossing whose active slopes bracket zero and whose value exceeds both
    endpoint values.  The lower envelope is constructed in O(m log m).
    """
    if len(payoff_matrix) != 2 or not payoff_matrix[0]:
        raise ValueError("payoff_matrix must contain two nonempty rows")
    if len(payoff_matrix[0]) != len(payoff_matrix[1]):
        raise ValueError("payoff rows must have equal length")
    matrix = tuple(tuple(Fraction(value) for value in row) for row in payoff_matrix)
    vertex_count = len(matrix[0])
    lines = tuple(
        (matrix[0][j] - matrix[1][j], matrix[1][j], j)
        for j in range(vertex_count)
    )

    # Equal-slope lines: only the lowest intercept can constrain the envelope.
    by_slope: dict[Fraction, tuple[Fraction, int]] = {}
    for slope, intercept, index in lines:
        incumbent = by_slope.get(slope)
        if incumbent is None or (intercept, index) < incumbent:
            by_slope[slope] = (intercept, index)
    ordered = tuple(
        (slope, intercept, index)
        for slope, (intercept, index) in sorted(
            by_slope.items(), key=lambda item: (-item[0], item[1][0], item[1][1])
        )
    )

    hull: list[tuple[Fraction, Fraction, int]] = []
    starts: list[Fraction | None] = []
    for line in ordered:
        start: Fraction | None = None
        while hull:
            previous = hull[-1]
            start = (line[1] - previous[1]) / (previous[0] - line[0])
            previous_start = starts[-1]
            if previous_start is not None and start <= previous_start:
                hull.pop()
                starts.pop()
                continue
            break
        if not hull:
            start = None
        hull.append(line)
        starts.append(start)

    endpoint_values = (
        min(matrix[1]),
        min(matrix[0]),
    )
    pure = max(endpoint_values)
    candidates: list[tuple[Fraction, Fraction]] = [
        (endpoint_values[0], Fraction(0)),
        (endpoint_values[1], Fraction(1)),
    ]
    for position in range(1, len(hull)):
        crossing = starts[position]
        assert crossing is not None
        if 0 < crossing < 1:
            slope, intercept, _ = hull[position]
            candidates.append((intercept + slope * crossing, crossing))
    value = max(candidate[0] for candidate in candidates)
    weight = min(candidate[1] for candidate in candidates if candidate[0] == value)
    if value == pure:
        # Canonicalize equality plateaus to a deterministic policy: there is no
        # strict randomized advantage to certify.
        weight = Fraction(int(endpoint_values[1] > endpoint_values[0]))
    realized = tuple(
        weight * matrix[0][j] + (1 - weight) * matrix[1][j]
        for j in range(vertex_count)
    )
    active = tuple(j for j, candidate in enumerate(realized) if candidate == value)
    gain = value - pure

    supported: tuple[int, ...] = ()
    if gain > 0:
        positive = tuple(j for j in active if lines[j][0] >= 0)
        negative = tuple(j for j in active if lines[j][0] <= 0)
        pairs = tuple(
            tuple(sorted((left, right)))
            for left in positive for right in negative if left != right
        )
        if pairs:
            supported = min(pairs)

    probabilities = (weight, 1 - weight)
    valid = (
        sum(probabilities) == 1
        and all(probability >= 0 for probability in probabilities)
        and min(realized) == value
        and gain >= 0
        and ((0 < weight < 1) == (gain > 0))
        and (bool(supported) == (gain > 0))
        and (
            not supported
            or (
                all(realized[j] == value for j in supported)
                and min(lines[j][0] for j in supported) <= 0
                and max(lines[j][0] for j in supported) >= 0
            )
        )
    )
    return TwoActionRobustGame(
        matrix, probabilities, value, pure, gain, gain > 0,
        supported, active, valid,
    )


def synthesize_additive_product_plan(
    component_payoff_matrices: tuple[tuple[tuple[Fraction, ...], ...], ...],
    *,
    payoff_additive_certified: bool,
    ambiguity_rectangular_certified: bool,
) -> AdditiveProductRobustPlan:
    """Solve an additive product game through its factors and sparsely couple them.

    For ``M(a,b) = sum_t M_t(a_t,b_t)`` and a full Cartesian product of
    ambiguity vertices, the robust value and best-pure value both add.  Any
    coupling of optimal component policies is therefore optimal.  The greedy
    common-mass coupling below realizes the component marginals with at most
    ``1 + sum_t(s_t - 1)`` atoms, where ``s_t`` is the positive support size
    of component ``t``.

    This executable fast path deliberately supports factors with either two
    actions or two ambiguity vertices, the exact structural solvers currently
    certified by THEORICA.  Unsupported structure fails closed.
    """
    if not payoff_additive_certified:
        raise ValueError("a certificate that payoff is additive is required")
    if not ambiguity_rectangular_certified:
        raise ValueError("a certificate that ambiguity is rectangular is required")
    if not component_payoff_matrices:
        raise ValueError("at least one component payoff matrix is required")

    matrices: list[tuple[tuple[Fraction, ...], ...]] = []
    probabilities: list[tuple[Fraction, ...]] = []
    values: list[Fraction] = []
    pure_values: list[Fraction] = []
    for raw in component_payoff_matrices:
        if not raw or not raw[0] or any(len(row) != len(raw[0]) for row in raw):
            raise ValueError("component payoff matrices must be nonempty and rectangular")
        matrix = tuple(tuple(Fraction(value) for value in row) for row in raw)
        if len(matrix[0]) == 2:
            solved = solve_two_vertex_robust_game(matrix)
            component_probabilities = solved.action_probabilities
        elif len(matrix) == 2:
            solved = solve_two_action_robust_game(matrix)
            component_probabilities = solved.action_probabilities
        else:
            raise ValueError("each component must have two actions or two vertices")
        if not solved.certificate_valid:
            raise RuntimeError("component exact certificate failed")
        matrices.append(matrix)
        probabilities.append(component_probabilities)
        values.append(solved.minimax_value)
        pure_values.append(solved.best_pure_value)

    # Greedy common-mass coupling.  Every step exhausts at least one current
    # marginal atom; only the final step can exhaust all remaining marginals.
    active = [
        [[index, probability] for index, probability in enumerate(component) if probability > 0]
        for component in probabilities
    ]
    positions = [0 for _ in active]
    joint: list[tuple[tuple[int, ...], Fraction]] = []
    while all(positions[t] < len(active[t]) for t in range(len(active))):
        actions = tuple(active[t][positions[t]][0] for t in range(len(active)))
        mass = min(active[t][positions[t]][1] for t in range(len(active)))
        joint.append((actions, mass))
        for t in range(len(active)):
            active[t][positions[t]][1] -= mass
            if active[t][positions[t]][1] == 0:
                positions[t] += 1

    component_probability_tuple = tuple(probabilities)
    joint_tuple = tuple(joint)
    component_value_tuple = tuple(values)
    component_pure_tuple = tuple(pure_values)
    value = sum(component_value_tuple, Fraction(0))
    pure = sum(component_pure_tuple, Fraction(0))
    gain = value - pure
    support_sizes = tuple(sum(p > 0 for p in component) for component in probabilities)
    support_bound = 1 + sum(size - 1 for size in support_sizes)

    recovered_marginals = tuple(
        tuple(sum((mass for actions, mass in joint_tuple if actions[t] == action), Fraction(0))
              for action in range(len(probabilities[t])))
        for t in range(len(probabilities))
    )
    # Rectangularity makes the joint worst case equal the sum of component
    # worst cases, so certificate validation remains linear in the component
    # matrix sizes and never expands the joint ambiguity product.
    component_realized = tuple(
        tuple(sum((component_probability_tuple[t][action] * matrix[action][vertex]
                   for action in range(len(matrix))), Fraction(0))
              for vertex in range(len(matrix[0])))
        for t, matrix in enumerate(matrices)
    )
    certified_worst = sum((min(payoffs) for payoffs in component_realized), Fraction(0))
    expanded_actions = 1
    expanded_vertices = 1
    for matrix in matrices:
        expanded_actions *= len(matrix)
        expanded_vertices *= len(matrix[0])
    valid = (
        sum((mass for _, mass in joint_tuple), Fraction(0)) == 1
        and all(mass > 0 for _, mass in joint_tuple)
        and recovered_marginals == component_probability_tuple
        and certified_worst == value
        and gain == sum((values[t] - pure_values[t] for t in range(len(values))), Fraction(0))
        and (gain > 0) == any(values[t] > pure_values[t] for t in range(len(values)))
        and len(joint_tuple) <= support_bound
    )
    return AdditiveProductRobustPlan(
        tuple(matrices), component_probability_tuple, joint_tuple,
        component_value_tuple, component_pure_tuple, value, pure, gain, gain > 0,
        expanded_actions, expanded_vertices, support_bound, valid,
        "additive_rectangular_sparse_coupling_certificate",
    )


def solve_two_by_two_robust_game(
    payoff_matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
) -> TwoByTwoRobustGame:
    """Solve a 2x2 robust game and certify the protected-pairing boundary.

    Strict mixing occurs iff either the diagonal or anti-diagonal entries are
    all strictly greater than the two entries outside that pairing.  This is
    the permutation-invariant form of the interior opposing-slope criterion.
    """
    if len(payoff_matrix) != 2 or any(len(row) != 2 for row in payoff_matrix):
        raise ValueError("payoff_matrix must contain exactly two rows and two columns")
    matrix = tuple(tuple(Fraction(value) for value in row) for row in payoff_matrix)
    (a, b), (c, d) = matrix
    pure_values = (min(a, b), min(c, d))
    best_pure = max(pure_values)
    diagonal = min(a, d) > max(b, c)
    anti_diagonal = min(b, c) > max(a, d)

    if diagonal or anti_diagonal:
        denominator = (a - c) + (d - b)
        first_probability = (d - c) / denominator
        value = (a * d - b * c) / denominator
        probabilities = (first_probability, 1 - first_probability)
        pairing = "diagonal" if diagonal else "anti_diagonal"
    else:
        first_probability = Fraction(int(pure_values[0] >= pure_values[1]))
        probabilities = (first_probability, 1 - first_probability)
        value = best_pure
        pairing = "none"

    realized = tuple(
        probabilities[0] * matrix[0][column]
        + probabilities[1] * matrix[1][column]
        for column in range(2)
    )
    gain = value - best_pure
    valid = (
        sum(probabilities) == 1
        and all(probability >= 0 for probability in probabilities)
        and min(realized) == value
        and gain >= 0
        and (gain > 0) == (diagonal or anti_diagonal)
        and ((all(probability > 0 for probability in probabilities)) == (gain > 0))
    )
    return TwoByTwoRobustGame(
        matrix, probabilities, value, best_pure, gain, gain > 0, pairing, valid,
    )


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
    two_by_two: TwoByTwoRobustGame | None = None
    two_vertex: TwoVertexRobustGame | None = None
    if len(records) == len(vertices) == 2:
        two_by_two = solve_two_by_two_robust_game(payoff)  # type: ignore[arg-type]
        if not two_by_two.certificate_valid:
            raise RuntimeError("two-by-two structural certificate failed validation")
        support = tuple(
            index for index, weight in enumerate(two_by_two.action_probabilities) if weight > 0
        )
        weights = tuple(two_by_two.action_probabilities[index] for index in support)
        best = (two_by_two.minimax_value, support, weights)
    elif len(vertices) == 2:
        two_vertex = solve_two_vertex_robust_game(payoff)  # type: ignore[arg-type]
        if not two_vertex.certificate_valid:
            raise RuntimeError("two-vertex sparse-support certificate failed validation")
        support = two_vertex.supported_actions
        weights = tuple(two_vertex.action_probabilities[index] for index in support)
        best = (two_vertex.minimax_value, support, weights)
    elif len(records) == 2:
        two_action = solve_two_action_robust_game(payoff)  # type: ignore[arg-type]
        if not two_action.certificate_valid:
            raise RuntimeError("two-action supported-crossing certificate failed validation")
        support = tuple(
            index for index, weight in enumerate(two_action.action_probabilities) if weight > 0
        )
        weights = tuple(two_action.action_probabilities[index] for index in support)
        best = (two_action.minimax_value, support, weights)
    else:
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
        (
            f"two_by_two_{two_by_two.protected_pairing}_certificate"
            if two_by_two is not None
            else "two_vertex_sparse_support_certificate"
            if two_vertex is not None
            else "two_action_supported_crossing_certificate"
            if len(records) == 2
            else "exact_orbit_quotient_maximin_certificate"
        ),
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
