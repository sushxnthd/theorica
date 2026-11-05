"""Frozen exact evaluation of affine-rank-two scenario hull compression."""
from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

from theorica.agents.robust_provenance import synthesize_rank_two_scenario_hull_plan

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "rank_two_scenario_hull" / "primary.json"
SEED = 20261025
HOLDOUT_SIZES = (11, 17, 29, 47, 80)
HOLDOUT_HULLS = (3, 4, 5, 6, 8)


def solve(rows, rhs):
    size = len(rows)
    matrix = [list(rows[i]) + [rhs[i]] for i in range(size)]
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
            matrix[row] = [matrix[row][i] - multiplier * matrix[column][i]
                           for i in range(size + 1)]
    return tuple(matrix[i][-1] for i in range(size))


def exact_game(actions):
    actions = tuple(sorted(set(tuple(Fraction(x) for x in row) for row in actions)))
    count = len(actions[0])
    dimension = count - 1
    ties = set()
    for left, right in combinations(actions, 2):
        row = tuple((left[i] - left[-1]) - (right[i] - right[-1])
                    for i in range(dimension))
        if any(row):
            ties.add((row, right[-1] - left[-1]))
    facets = tuple(
        (tuple(Fraction(int(i == j)) for i in range(dimension)), Fraction(0))
        for j in range(dimension)
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
        return max(sum(weights[i] * action[i] for i in range(count))
                   for action in actions)

    value = min(score(point) for point in points)
    strict = max(min(action) for action in actions) < value
    return value, strict


def convex_hull_indices(coordinates):
    unique = {}
    for index, point in enumerate(coordinates):
        unique.setdefault(point, index)
    points = tuple(sorted((x, y, index) for (x, y), index in unique.items()))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

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
    return tuple(point[2] for point in lower[:-1] + upper[:-1])


def expand(components, indices):
    return tuple(
        tuple(sum((components[t][choice[t]][scenario]
                   for t in range(len(components))), Fraction(0))
              for scenario in indices)
        for choice in product(*(range(len(component)) for component in components))
    )


def make_case(ambient, hull_size, rng, *, pure=False):
    hull = tuple((Fraction(i), Fraction(i * i)) for i in range(hull_size))
    coordinates = list(hull)
    while len(coordinates) < ambient:
        weights = tuple(rng.randrange(1, 10) for _ in hull)
        total = sum(weights)
        coordinates.append((
            sum(Fraction(weights[i], total) * hull[i][0] for i in range(hull_size)),
            sum(Fraction(weights[i], total) * hull[i][1] for i in range(hull_size)),
        ))
    rng.shuffle(coordinates)
    coordinates = tuple(coordinates)
    if pure:
        groups = (
            ((100, 0, 0), (0, 1, 0)),
            ((0, 0, 1), (-10, -1, -1)),
        )
    else:
        groups = (
            ((rng.randrange(-3, 4), 1, 0), (rng.randrange(-3, 4), 0, 1)),
            tuple((rng.randrange(-4, 5), rng.randrange(-2, 3), rng.randrange(-2, 3))
                  for _ in range(2)),
        )
    components = tuple(
        tuple(tuple(Fraction(b) + Fraction(dx) * x + Fraction(dy) * y
                    for x, y in coordinates) for b, dx, dy in group)
        for group in groups
    )
    return coordinates, components


def opened_cases():
    rng = random.Random(SEED - 1)
    cases = []
    triangle = (
        (Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(1)),
    )
    interior = tuple((Fraction(i, 20), Fraction(j, 20))
                     for i, j in ((2, 3), (3, 4), (5, 2), (4, 5), (6, 3), (3, 6)))
    coordinates = triangle + interior
    components = ((
        tuple(1 - x - y for x, y in coordinates),
        tuple(x for x, _ in coordinates),
        tuple(y for _, y in coordinates),
    ),)
    cases.append((coordinates, components))
    for hull_size in range(3, 9):
        for index in range(20):
            ambient = 9 + (index * 7 + hull_size) % 32
            cases.append(make_case(ambient, hull_size, rng, pure=index % 5 == 0))
    return tuple(cases)


def holdout_cases():
    rng = random.Random(SEED)
    cases = []
    for ambient, hull_size in zip(HOLDOUT_SIZES, HOLDOUT_HULLS):
        for index in range(5):
            cases.append(make_case(ambient, hull_size, rng, pure=index == 0))
    return tuple(cases)


def evaluate(case):
    coordinates, components = case
    extremes = convex_hull_indices(coordinates)
    exact, strict = exact_game(expand(components, extremes))
    plan = synthesize_rank_two_scenario_hull_plan(
        components, payoff_additive_certified=True,
    )
    realized = tuple(
        sum((mass * sum((components[t][choice[t]][scenario]
                         for t in range(len(components))), Fraction(0))
             for choice, mass in plan.joint_actions), Fraction(0))
        for scenario in range(len(coordinates))
    )
    passed = (
        plan.certificate_valid
        and set(plan.extreme_indices) == set(extremes)
        and plan.minimax_value == exact
        and plan.strict_randomization_necessary == strict
        and min(realized) == exact
        and all(plan.nature_probabilities[i] == 0
                for i in range(len(coordinates)) if i not in extremes)
    )
    baseline = {
        "ambient": len(coordinates),
        "hull": len(extremes),
        "value": str(exact),
        "strict": strict,
        "expanded_actions": len(expand(components, extremes)),
    }
    return baseline, passed, len(plan.joint_actions)


def digest(items):
    value = hashlib.sha256()
    for item in items:
        value.update((json.dumps(item, sort_keys=True) + "\n").encode())
    return value.hexdigest()


def main():
    opened_results = [evaluate(case) for case in opened_cases()]
    holdout_results = [evaluate(case) for case in holdout_cases()]
    opened = [item[0] for item in opened_results]
    holdouts = [item[0] for item in holdout_results]

    rank_three_rejections = 0
    for mutation in range(50):
        third = 2 + mutation % 7
        attack = (((0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, third)),)
        try:
            synthesize_rank_two_scenario_hull_plan(
                attack, payoff_additive_certified=True,
            )
        except ValueError as error:
            rank_three_rejections += int("above two" in str(error))

    over_cap_rejections = 0
    for shift in range(20):
        x = tuple(Fraction(i + shift) for i in range(-4, 5))
        attack = ((x, tuple(value * value for value in x)),)
        try:
            synthesize_rank_two_scenario_hull_plan(
                attack, payoff_additive_certified=True,
            )
        except ValueError as error:
            over_cap_rejections += int("hull exceeds" in str(error))

    x = tuple(Fraction(i) for i in range(-2, 3))
    coordinate_attack = ((tuple(value * value + 2 * value for value in x), x),)
    attack_plan = synthesize_rank_two_scenario_hull_plan(
        coordinate_attack, payoff_additive_certified=True,
    )
    heuristic_indices = (0, 2, 4)
    heuristic_value, _ = exact_game(expand(coordinate_attack, heuristic_indices))

    scaling_rng = random.Random(SEED + 99)
    scaling_coordinates, _ = make_case(80, 8, scaling_rng)
    scaling_components = tuple(
        (
            tuple(x for x, _ in scaling_coordinates),
            tuple(y for _, y in scaling_coordinates),
        ) for _ in range(20)
    )
    scaling = synthesize_rank_two_scenario_hull_plan(
        scaling_components, payoff_additive_certified=True,
    )

    checks = {
        "opened_exact": all(item[1] for item in opened_results),
        "opened_mixed_and_pure": any(item["strict"] for item in opened)
            and any(not item["strict"] for item in opened),
        "holdouts_exact": len(holdouts) == 25
            and all(item[1] for item in holdout_results),
        "holdout_shapes": sorted(set((item["ambient"], item["hull"])
                                      for item in holdouts))
            == sorted(zip(HOLDOUT_SIZES, HOLDOUT_HULLS)),
        "rank_three_rejected": rank_three_rejections == 50,
        "over_cap_rejected": over_cap_rejections == 20,
        "coordinate_extrema_falsified": attack_plan.minimax_value == -1
            and heuristic_value == 0,
        "scaling_certificate": scaling.certificate_valid
            and scaling.scenario_count == 80
            and scaling.effective_scenario_count == 8
            and scaling.expanded_action_count == 2 ** 20,
    }
    result = {
        "schema": "rank-two-scenario-hull-v1",
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
            "hull_sizes": list(HOLDOUT_HULLS),
            "strict": sum(item["strict"] for item in holdouts),
            "max_support": max(item[2] for item in holdout_results),
            "digest": digest(holdouts),
        },
        "falsification": {
            "rank_three_attacks": 50,
            "rank_three_rejections": rank_three_rejections,
            "over_cap_attacks": 20,
            "over_cap_rejections": over_cap_rejections,
            "coordinate_extrema_actual": str(attack_plan.minimax_value),
            "coordinate_extrema_heuristic": str(heuristic_value),
        },
        "scaling": {
            "components": 20,
            "actions_per_component": 2,
            "ambient_scenarios": scaling.scenario_count,
            "hull_scenarios": scaling.effective_scenario_count,
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
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
