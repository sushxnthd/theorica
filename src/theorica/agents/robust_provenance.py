"""Robust query frontiers for uncertain certified provenance priors."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

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


def deterministic_tv_frontier(
    prior_weights: tuple[int, ...], query_budget: int, tv_radius: Fraction,
) -> Fraction:
    """Exact deterministic robust value: max(0, top-(q+1) mass - delta)."""
    weights = tuple(int(value) for value in prior_weights)
    if len(weights) < 3 or any(value < 0 for value in weights) or sum(weights) <= 0:
        raise ValueError("prior_weights must be nonnegative with positive sum")
    q = int(query_budget)
    if not 0 <= q < len(weights):
        raise ValueError("query_budget must lie in [0,n-1]")
    delta = Fraction(tv_radius)
    if not 0 <= delta <= 1:
        raise ValueError("tv_radius must lie in [0,1]")
    nominal = Fraction(sum(sorted(weights, reverse=True)[: q + 1]), sum(weights))
    return max(Fraction(0), nominal - delta)


def randomized_tv_frontier_lp(
    prior_weights: tuple[int, ...], query_budget: int, tv_radius: Fraction,
) -> float:
    """Compute min_{TV(pi,p)<=delta} sum of the q+1 largest pi masses.

    Finite minimax duality makes this exactly the randomized robust value.
    The returned floating value is accepted only after HiGHS reports optimality.
    """
    weights = tuple(int(value) for value in prior_weights)
    n = len(weights)
    _ = deterministic_tv_frontier(weights, query_budget, tv_radius)
    k = int(query_budget) + 1
    p = np.asarray(weights, dtype=float) / sum(weights)
    delta = float(Fraction(tv_radius))
    # Variables: adversarial pi[0:n], absolute deviations u[n:2n], epigraph v.
    objective = np.zeros(2 * n + 1); objective[-1] = 1.0
    aub, bub = [], []
    for subset in combinations(range(n), k):
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
    return float(result.fun)


def robust_provenance_frontier(
    prior_weights: tuple[int, ...], query_budget: int, tv_radius: Fraction,
    *, tolerance: float = 1e-9,
) -> RobustProvenanceFrontier:
    deterministic = deterministic_tv_frontier(prior_weights, query_budget, tv_radius)
    randomized = randomized_tv_frontier_lp(prior_weights, query_budget, tv_radius)
    gap = randomized - float(deterministic)
    minimax = gap <= tolerance
    return RobustProvenanceFrontier(
        len(prior_weights), int(query_budget), int(query_budget) + 1,
        Fraction(tv_radius), deterministic, randomized, gap, minimax,
        "use_deterministic_top_mass" if minimax else "refuse_dominated_deterministic_plan",
    )

