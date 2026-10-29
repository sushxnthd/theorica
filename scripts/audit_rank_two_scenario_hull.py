"""Independent exact audit; intentionally imports no THEORICA production code."""
from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "results" / "rank_two_scenario_hull" / "primary.json"
OUT = ROOT / "results" / "rank_two_scenario_hull" / "independent_audit.json"
SEED = 20261025
SIZES = (11, 17, 29, 47, 80)
HULLS = (3, 4, 5, 6, 8)


def solve(rows, rhs):
    n = len(rows)
    matrix = [list(rows[i]) + [rhs[i]] for i in range(n)]
    for column in range(n):
        pivot = next((row for row in range(column, n) if matrix[row][column]), None)
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        scale = matrix[column][column]
        matrix[column] = [value / scale for value in matrix[column]]
        for row in range(n):
            if row == column or matrix[row][column] == 0:
                continue
            scale = matrix[row][column]
            matrix[row] = [matrix[row][i] - scale * matrix[column][i]
                           for i in range(n + 1)]
    return tuple(matrix[i][-1] for i in range(n))


def exact_game(actions):
    actions = tuple(sorted(set(actions)))
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
    return value, max(min(action) for action in actions) < value


def hull_indices(coordinates):
    unique = {}
    for index, point in enumerate(coordinates):
        unique.setdefault(point, index)
    points = tuple(sorted((x, y, i) for (x, y), i in unique.items()))

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


def make_case(ambient, hull_size, rng, pure=False):
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
        groups = (((100, 0, 0), (0, 1, 0)), ((0, 0, 1), (-10, -1, -1)))
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
    triangle = ((Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)),
                (Fraction(0), Fraction(1)))
    interior = tuple((Fraction(i, 20), Fraction(j, 20))
                     for i, j in ((2, 3), (3, 4), (5, 2), (4, 5), (6, 3), (3, 6)))
    coordinates = triangle + interior
    cases = [(coordinates, ((tuple(1 - x - y for x, y in coordinates),
                              tuple(x for x, _ in coordinates),
                              tuple(y for _, y in coordinates)),))]
    for hull_size in range(3, 9):
        for index in range(20):
            ambient = 9 + (index * 7 + hull_size) % 32
            cases.append(make_case(ambient, hull_size, rng, index % 5 == 0))
    return tuple(cases)


def holdout_cases():
    rng = random.Random(SEED)
    return tuple(make_case(ambient, hull, rng, index == 0)
                 for ambient, hull in zip(SIZES, HULLS) for index in range(5))


def baseline(case):
    coordinates, components = case
    extremes = hull_indices(coordinates)
    actions = tuple(
        tuple(sum((components[t][choice[t]][scenario]
                   for t in range(len(components))), Fraction(0))
              for scenario in extremes)
        for choice in product(*(range(len(component)) for component in components))
    )
    value, strict = exact_game(actions)
    return {
        "ambient": len(coordinates),
        "hull": len(extremes),
        "value": str(value),
        "strict": strict,
        "expanded_actions": len(actions),
    }


def digest(items):
    value = hashlib.sha256()
    for item in items:
        value.update((json.dumps(item, sort_keys=True) + "\n").encode())
    return value.hexdigest()


def main():
    primary = json.loads(PRIMARY.read_text())
    opened = [baseline(case) for case in opened_cases()]
    holdouts = [baseline(case) for case in holdout_cases()]
    checks = {
        "opened_count": len(opened) == primary["opened"]["cases"] == 121,
        "opened_digest": digest(opened) == primary["opened"]["digest"],
        "opened_classification": sum(item["strict"] for item in opened)
            == primary["opened"]["strict"],
        "holdout_count": len(holdouts) == primary["holdouts"]["cases"] == 25,
        "holdout_digest": digest(holdouts) == primary["holdouts"]["digest"],
        "holdout_shapes": sorted(set((item["ambient"], item["hull"])
                                      for item in holdouts))
            == sorted(zip(SIZES, HULLS)),
        "falsification": primary["falsification"]["rank_three_rejections"] == 50
            and primary["falsification"]["over_cap_rejections"] == 20
            and primary["falsification"]["coordinate_extrema_actual"] == "-1"
            and primary["falsification"]["coordinate_extrema_heuristic"] == "0",
        "scaling": primary["scaling"]["expanded_actions"] == 2 ** 20
            and primary["scaling"]["ambient_scenarios"] == 80
            and primary["scaling"]["hull_scenarios"] == 8
            and primary["scaling"]["valid"],
        "primary_passed": primary["passed"] and all(primary["checks"].values()),
    }
    result = {
        "schema": "rank-two-scenario-hull-independent-audit-v1",
        "checks": checks,
        "passed": all(checks.values()),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
