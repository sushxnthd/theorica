"""Robust query frontiers for uncertain certified provenance priors."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
from itertools import combinations
import json

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

