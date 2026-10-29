"""Frozen exact evaluation of affine-rank-three scenario polytope compression."""

from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

import numpy as np
from scipy.spatial import ConvexHull

from theorica.agents.robust_provenance import (
    synthesize_fixed_scenario_additive_plan,
    synthesize_rank_three_scenario_polytope_plan,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "rank_three_scenario_polytope" / "primary.json"
HOLDOUT_OUT = ROOT / "results" / "rank_three_scenario_polytope" / "holdouts.json"
SEED = 20261026
HOLDOUT_SIZES = (9, 12, 16, 20, 24)
HOLDOUT_VERTICES = (4, 5, 6, 7, 8)


def solve(rows, rhs):
    size = len(rows)
    matrix = [list(rows[index]) + [rhs[index]] for index in range(size)]
    for column in range(size):
        pivot = next((row for row in range(column, size)
                      if matrix[row][column]), None)
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        divisor = matrix[column][column]
        matrix[column] = [entry / divisor for entry in matrix[column]]
        for row in range(size):
            if row == column or matrix[row][column] == 0:
                continue
            multiplier = matrix[row][column]
            matrix[row] = [
                matrix[row][index] - multiplier * matrix[column][index]
                for index in range(size + 1)
            ]
    return tuple(matrix[index][-1] for index in range(size))


def exact_game(actions):
    actions = tuple(sorted({tuple(Fraction(x) for x in row) for row in actions}))
    count = len(actions[0])
    dimension = count - 1
    ties = set()
    for left, right in combinations(actions, 2):
        row = tuple((left[index] - left[-1]) - (right[index] - right[-1])
                    for index in range(dimension))
        if any(row):
            ties.add((row, right[-1] - left[-1]))
    facets = tuple(
        (tuple(Fraction(int(index == other)) for index in range(dimension)),
         Fraction(0))
        for other in range(dimension)
    ) + (((Fraction(1),) * dimension, Fraction(1)),)
    points = set()
    for chosen in combinations(tuple(ties) + facets, dimension):
        point = solve(tuple(item[0] for item in chosen),
                      tuple(item[1] for item in chosen))
        if point is not None and all(value >= 0 for value in point) \
                and sum(point) <= 1:
            points.add(point)

    def score(point):
        weights = tuple(point) + (1 - sum(point),)
        return max(sum(weights[index] * action[index]
                       for index in range(count)) for action in actions)

    value = min(score(point) for point in points)
    strict = max(min(action) for action in actions) < value
    return value, strict


def in_hull(point, candidates):
    rhs = tuple(point) + (Fraction(1),)
    for size in range(1, min(4, len(candidates)) + 1):
        for support in combinations(candidates, size):
            equations = tuple(
                tuple(vertex[coordinate] for vertex in support)
                for coordinate in range(3)
            ) + ((Fraction(1),) * size,)
            for selected in combinations(range(4), size):
                weights = solve(
                    tuple(equations[index] for index in selected),
                    tuple(rhs[index] for index in selected),
                )
                if weights is None or any(weight < 0 for weight in weights):
                    continue
                if all(sum((equations[row][column] * weights[column]
                            for column in range(size)), Fraction(0)) == rhs[row]
                       for row in range(4)):
                    return True
    return False


def hull_indices(coordinates):
    unique = {}
    for index, point in enumerate(coordinates):
        unique.setdefault(point, index)
    points = tuple(unique)
    proposal = ConvexHull(np.asarray(points, dtype=float))
    proposed = tuple(points[index] for index in proposal.vertices)
    exact = tuple(
        point for point in proposed
        if not in_hull(point, tuple(other for other in proposed if other != point))
    )
    assert all(in_hull(point, exact) for point in points if point not in exact)
    return tuple(unique[point] for point in exact)


def expand(components, indices):
    return tuple(
        tuple(sum((components[component][choice[component]][scenario]
                   for component in range(len(components))), Fraction(0))
              for scenario in indices)
        for choice in product(*(range(len(component)) for component in components))
    )


def make_coordinates(ambient, vertices, rng):
    hull = tuple(
        (Fraction(t), Fraction(t * t), Fraction(t * t * t))
        for t in range(vertices)
    )
    coordinates = list(hull)
    while len(coordinates) < ambient:
        support = rng.sample(range(vertices), min(4, vertices))
        weights = tuple(rng.randrange(1, 10) for _ in support)
        total = sum(weights)
        coordinates.append(tuple(
            sum(Fraction(weight, total) * hull[index][axis]
                for index, weight in zip(support, weights, strict=True))
            for axis in range(3)
        ))
    rng.shuffle(coordinates)
    return tuple(coordinates)


def make_case(ambient, vertices, rng, *, pure):
    coordinates = make_coordinates(ambient, vertices, rng)
    if pure:
        coefficients = (
            (1000, 0, 0, 0),
            (0, 1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        )
    else:
        coefficients = (
            (1, -1, -1, -1),
            (0, 1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        )
    actions = tuple(
        tuple(Fraction(base) + Fraction(dx) * x + Fraction(dy) * y
              + Fraction(dz) * z for x, y, z in coordinates)
        for base, dx, dy, dz in coefficients
    )
    return coordinates, (actions,)


def opened_cases():
    rng = random.Random(SEED - 1)
    return tuple(
        make_case(8 + (index * 5 + vertices) % 13, vertices, rng,
                  pure=index % 5 == 0)
        for vertices in range(4, 9)
        for index in range(16)
    )


def holdout_cases():
    rng = random.Random(SEED)
    return tuple(
        make_case(ambient, vertices, rng, pure=index == 0)
        for ambient, vertices in zip(HOLDOUT_SIZES, HOLDOUT_VERTICES, strict=True)
        for index in range(5)
    )


def evaluate(case):
    coordinates, components = case
    extremes = hull_indices(coordinates)
    expanded = expand(components, extremes)
    exact, strict = exact_game(expanded)
    plan = synthesize_rank_three_scenario_polytope_plan(
        components, payoff_additive_certified=True,
    )
    realized = tuple(
        sum((mass * sum((components[component][choice[component]][scenario]
                         for component in range(len(components))), Fraction(0))
             for choice, mass in plan.joint_actions), Fraction(0))
        for scenario in range(len(coordinates))
    )
    passed = (
        plan.certificate_valid
        and set(plan.extreme_indices) == set(extremes)
        and plan.minimax_value == exact
        and plan.strict_randomization_necessary == strict
        and min(realized) == exact
        and all(plan.nature_probabilities[index] == 0
                for index in range(len(coordinates)) if index not in extremes)
    )
    return {
        "ambient": len(coordinates),
        "vertices": len(extremes),
        "value": str(exact),
        "strict": strict,
        "expanded_actions": len(expanded),
    }, passed, len(plan.joint_actions)


def digest(items):
    value = hashlib.sha256()
    for item in items:
        value.update((json.dumps(item, sort_keys=True) + "\n").encode())
    return value.hexdigest()


def serialize_case(case, evaluated):
    coordinates, components = case
    baseline, passed, support = evaluated
    return {
        "coordinates": [[str(value) for value in point] for point in coordinates],
        "components": [
            [[str(value) for value in action] for action in component]
            for component in components
        ],
        "expected": baseline,
        "production_passed": passed,
        "production_support": support,
    }


def main():
    opened = opened_cases()
    frozen_holdouts = holdout_cases()
    opened_results = [evaluate(case) for case in opened]
    holdout_results = [evaluate(case) for case in frozen_holdouts]
    opened = [item[0] for item in opened_results]
    holdouts = [item[0] for item in holdout_results]

    rank_four_rejections = 0
    for mutation in range(50):
        scale = 1 + mutation % 7
        attack = (((0, scale, 0, 0, 0), (0, 0, scale, 0, 0),
                   (0, 0, 0, scale, 0), (0, 0, 0, 0, scale)),)
        try:
            synthesize_rank_three_scenario_polytope_plan(
                attack, payoff_additive_certified=True,
            )
        except ValueError as error:
            rank_four_rejections += int("above three" in str(error))

    over_cap_rejections = 0
    for shift in range(20):
        x = tuple(Fraction(index + shift) for index in range(-4, 5))
        attack = ((x, tuple(value * value for value in x),
                   tuple(value * value * value for value in x)),)
        try:
            synthesize_rank_three_scenario_polytope_plan(
                attack, payoff_additive_certified=True,
            )
        except ValueError as error:
            over_cap_rejections += int("polytope exceeds" in str(error))

    baseline_t = tuple(Fraction(value) for value in (-2, -1, 0, 1, 2))
    baseline_coefficients = (
        (-3, -1, -2, 3), (2, 4, -3, -4),
        (2, 1, 1, 1), (-1, 0, 3, 1),
    )
    baseline_actions = tuple(
        tuple(Fraction(a + b * t + c * t * t + d * t * t * t)
              for t in baseline_t)
        for a, b, c, d in baseline_coefficients
    )
    baseline_plan = synthesize_rank_three_scenario_polytope_plan(
        (baseline_actions,), payoff_additive_certified=True,
    )
    axis_indices = (0, 2, 4)
    axis_actions = tuple(tuple(action[index] for index in axis_indices)
                         for action in baseline_actions)
    axis_plan = synthesize_fixed_scenario_additive_plan(
        (axis_actions,), payoff_additive_certified=True,
    )

    scaling_rng = random.Random(SEED + 99)
    scaling_coordinates = make_coordinates(24, 8, scaling_rng)
    scaling_components = tuple(
        (tuple(Fraction(0) for _ in scaling_coordinates),
         tuple(point[component % 3] for point in scaling_coordinates))
        for component in range(20)
    )
    scaling = synthesize_rank_three_scenario_polytope_plan(
        scaling_components, payoff_additive_certified=True,
    )

    checks = {
        "opened_exact": len(opened) == 80 and all(item[1] for item in opened_results),
        "opened_mixed_and_pure": any(item["strict"] for item in opened)
            and any(not item["strict"] for item in opened),
        "holdouts_exact": len(holdouts) == 25
            and all(item[1] for item in holdout_results),
        "holdout_shapes": sorted({(item["ambient"], item["vertices"])
                                   for item in holdouts})
            == sorted(zip(HOLDOUT_SIZES, HOLDOUT_VERTICES, strict=True)),
        "rank_four_rejected": rank_four_rejections == 50,
        "over_cap_rejected": over_cap_rejections == 20,
        "coordinate_extrema_falsified": baseline_plan.minimax_value == Fraction(29, 37)
            and axis_plan.minimax_value == Fraction(67, 38),
        "scaling_certificate": scaling.certificate_valid
            and scaling.scenario_count == 24
            and scaling.effective_scenario_count == 8
            and scaling.expanded_action_count == 2 ** 20,
    }
    result = {
        "schema": "rank-three-scenario-polytope-v1",
        "seed": SEED,
        "opened": {
            "cases": len(opened),
            "strict": sum(item["strict"] for item in opened),
            "max_support": max(item[2] for item in opened_results),
            "digest": digest(opened),
        },
        "holdouts": {
            "cases": len(holdouts),
            "ambient_sizes": list(HOLDOUT_SIZES),
            "vertex_counts": list(HOLDOUT_VERTICES),
            "strict": sum(item["strict"] for item in holdouts),
            "max_support": max(item[2] for item in holdout_results),
            "digest": digest(holdouts),
        },
        "falsification": {
            "rank_four_attacks": 50,
            "rank_four_rejections": rank_four_rejections,
            "over_cap_attacks": 20,
            "over_cap_rejections": over_cap_rejections,
            "coordinate_extrema_actual": str(baseline_plan.minimax_value),
            "coordinate_extrema_heuristic": str(axis_plan.minimax_value),
        },
        "scaling": {
            "components": 20,
            "actions_per_component": 2,
            "ambient_scenarios": scaling.scenario_count,
            "polytope_vertices": scaling.effective_scenario_count,
            "expanded_actions": scaling.expanded_action_count,
            "support": len(scaling.joint_actions),
            "value": str(scaling.minimax_value),
            "valid": scaling.certificate_valid,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    HOLDOUT_OUT.write_text(json.dumps({
        "schema": "rank-three-scenario-polytope-holdouts-v1",
        "seed": SEED,
        "cases": [
            serialize_case(case, evaluated)
            for case, evaluated in zip(
                frozen_holdouts, holdout_results, strict=True,
            )
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
