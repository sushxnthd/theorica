#!/usr/bin/env python3
"""Independent standard-library checker; deliberately imports no THEORICA solver."""
from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
from pathlib import Path


def solve_2x2(matrix):
    matrix = tuple(tuple(Fraction(x) for x in row) for row in matrix)
    candidates = {Fraction(0), Fraction(1)}
    slope0 = matrix[0][0] - matrix[1][0]
    slope1 = matrix[0][1] - matrix[1][1]
    if slope0 != slope1:
        crossing = (matrix[1][1] - matrix[1][0]) / (slope0 - slope1)
        if 0 <= crossing <= 1:
            candidates.add(crossing)
    scored = tuple((min(p * matrix[0][j] + (1 - p) * matrix[1][j] for j in range(2)), p)
                   for p in candidates)
    value = max(v for v, _ in scored)
    p = min(p for v, p in scored if v == value)
    pure = max(min(row) for row in matrix)
    return value, pure, (p, 1 - p)


def greedy(marginals):
    active = [[[i, p] for i, p in enumerate(marginal) if p] for marginal in marginals]
    positions = [0] * len(active)
    result = []
    while all(positions[t] < len(active[t]) for t in range(len(active))):
        actions = tuple(active[t][positions[t]][0] for t in range(len(active)))
        mass = min(active[t][positions[t]][1] for t in range(len(active)))
        result.append((actions, mass))
        for t in range(len(active)):
            active[t][positions[t]][1] -= mass
            positions[t] += int(active[t][positions[t]][1] == 0)
    return tuple(result)


def audit_family(family):
    solved = tuple(solve_2x2(matrix) for matrix in family)
    value = sum((item[0] for item in solved), Fraction(0))
    pure = sum((item[1] for item in solved), Fraction(0))
    marginals = tuple(item[2] for item in solved)
    coupling = greedy(marginals)
    support_bound = 1 + sum(sum(p > 0 for p in marginal) - 1 for marginal in marginals)
    vertices = tuple(product(range(2), repeat=len(family)))
    realized = tuple(sum(mass * sum(family[t][actions[t]][vertex[t]]
                                    for t in range(len(family)))
                         for actions, mass in coupling) for vertex in vertices)
    assert min(realized) == value
    assert len(coupling) <= support_bound
    return value, pure, len(coupling), support_bound


def main():
    games = tuple(tuple(tuple(entries[2 * r + c] for c in range(2)) for r in range(2))
                  for entries in product(range(3), repeat=4))
    strict = 0
    maximum_support = 0
    for left in games:
        for right in games:
            value, pure, support, _ = audit_family((left, right))
            strict += int(value > pure)
            maximum_support = max(maximum_support, support)
    result = {
        "checker": "independent_fraction_only_no_production_import",
        "exhaustive_cases": len(games) ** 2,
        "strict_pairs": strict,
        "maximum_support": maximum_support,
        "status": "pass",
    }
    target = Path("results/additive_product_minimax/independent_audit.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
