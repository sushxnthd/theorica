"""Independent Fraction-only audit; imports no THEORICA production code."""

import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOLDOUTS = ROOT / "results" / "rank_three_scenario_polytope" / "holdouts.json"
OUT = ROOT / "results" / "rank_three_scenario_polytope" / "independent_audit.json"
AUDIT_INDICES = (0, 4, 5, 10, 14, 15, 20, 24)


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


def hull_indices(points):
    unique = {}
    for index, point in enumerate(points):
        unique.setdefault(point, index)
    coordinates = tuple(unique)
    return tuple(
        unique[point] for point in coordinates
        if not in_hull(point, tuple(other for other in coordinates if other != point))
    )


def exact_game(actions):
    actions = tuple(sorted(set(actions)))
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
    for selected in combinations(tuple(ties) + facets, dimension):
        point = solve(tuple(item[0] for item in selected),
                      tuple(item[1] for item in selected))
        if point is not None and all(value >= 0 for value in point) \
                and sum(point) <= 1:
            points.add(point)

    def score(point):
        weights = tuple(point) + (1 - sum(point),)
        return max(sum(weights[index] * action[index]
                       for index in range(count)) for action in actions)

    value = min(score(point) for point in points)
    return value, max(min(action) for action in actions) < value


def expand(components, indices):
    return tuple(
        tuple(sum((components[component][choice[component]][scenario]
                   for component in range(len(components))), Fraction(0))
              for scenario in indices)
        for choice in product(*(range(len(component)) for component in components))
    )


def main():
    payload = json.loads(HOLDOUTS.read_text())
    results = []
    for index in AUDIT_INDICES:
        case = payload["cases"][index]
        coordinates = tuple(tuple(Fraction(value) for value in point)
                            for point in case["coordinates"])
        components = tuple(
            tuple(tuple(Fraction(value) for value in action)
                  for action in component)
            for component in case["components"]
        )
        extremes = hull_indices(coordinates)
        value, strict = exact_game(expand(components, extremes))
        expected = case["expected"]
        passed = (
            len(extremes) == expected["vertices"]
            and value == Fraction(expected["value"])
            and strict is expected["strict"]
            and case["production_passed"] is True
            and case["production_support"] <= len(extremes)
        )
        results.append({
            "case_index": index,
            "ambient": len(coordinates),
            "vertices": len(extremes),
            "value": str(value),
            "strict": strict,
            "passed": passed,
        })
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    report = {
        "schema": "rank-three-scenario-polytope-independent-audit-v1",
        "fraction_only": True,
        "production_imports": False,
        "cases": len(results),
        "passed_cases": sum(item["passed"] for item in results),
        "digest": hashlib.sha256(canonical.encode()).hexdigest(),
        "results": results,
        "passed": all(item["passed"] for item in results),
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
