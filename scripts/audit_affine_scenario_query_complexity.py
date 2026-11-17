#!/usr/bin/env python3
"""Independent stdlib-only audit of affine-scenario query evidence."""
from __future__ import annotations

import ast
import hashlib
import json
import random
from fractions import Fraction
from pathlib import Path

SOURCE = Path("src/theorica/agents/robust_provenance.py")
PRIMARY = Path("results/affine_scenario_query_complexity/primary.json")
OUT = Path("results/affine_scenario_query_complexity/independent_audit.json")


def solve(rows, rhs):
    n = len(rows)
    matrix = [list(rows[i]) + [rhs[i]] for i in range(n)]
    for column in range(n):
        pivot = next((row for row in range(column, n)
                      if matrix[row][column]), None)
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        scale = matrix[column][column]
        matrix[column] = [value / scale for value in matrix[column]]
        for row in range(n):
            if row == column:
                continue
            scale = matrix[row][column]
            matrix[row] = [matrix[row][i] - scale * matrix[column][i]
                           for i in range(n + 1)]
    return tuple(matrix[row][-1] for row in range(n))


def descriptors(dimension, count):
    if dimension == 1:
        return ((Fraction(0),), (Fraction(1),)) + tuple(
            (Fraction(index, count + 1),) for index in range(2, count))
    points = [(Fraction(0),) * dimension]
    points.extend(tuple(Fraction(i == j) for i in range(dimension))
                  for j in range(dimension))
    denominator = 4
    while len(points) < count:
        candidates = (
            ((Fraction(a, denominator), Fraction(b, denominator))
             for a in range(1, denominator)
             for b in range(1, denominator - a))
            if dimension == 2 else
            ((Fraction(a, denominator), Fraction(b, denominator),
              Fraction(c, denominator))
             for a in range(1, denominator)
             for b in range(1, denominator)
             for c in range(1, denominator - a - b))
        )
        for point in candidates:
            if point not in points:
                points.append(point)
                if len(points) == count:
                    break
        denominator += 1
    return tuple(points)


def table_for(dimension, count, seed):
    rng = random.Random(seed)
    points = descriptors(dimension, count)
    coefficients = []
    for component in range(2 + seed % 4):
        actions = []
        for action in range(2 + (component + seed) % 2):
            values = [rng.randint(-5, 5) for _ in range(dimension + 1)]
            if component == 0 and action < dimension:
                values = [0] + [int(index == action)
                                for index in range(dimension)]
            actions.append(tuple(Fraction(value) for value in values))
        coefficients.append(tuple(actions))
    table = tuple(tuple(tuple(
        action[0] + sum((action[index + 1] * point[index]
                         for index in range(dimension)), Fraction(0))
        for point in points) for action in component)
        for component in coefficients)
    return points, table


def audit_family(record):
    dimension = record["dimension"]
    points, table = table_for(dimension, record["scenario_count"], record["seed"])
    indices = tuple(record["query_indices"])
    if len(indices) != dimension + 1:
        return False
    rows = tuple((Fraction(1),) + points[index] for index in indices)
    reconstructed = []
    for component in table:
        actions = []
        for action in component:
            coefficients = solve(rows, tuple(action[index] for index in indices))
            if coefficients is None:
                return False
            actions.append(tuple(sum((coefficient * coordinate
                                      for coefficient, coordinate
                                      in zip(coefficients, (Fraction(1),) + point)),
                                     Fraction(0)) for point in points))
        reconstructed.append(tuple(actions))
    return tuple(reconstructed) == table


def main():
    primary = json.loads(PRIMARY.read_text())
    digest_payload = dict(primary)
    expected_digest = digest_payload.pop("digest")
    digest_payload.pop("passed")
    digest = hashlib.sha256(json.dumps(
        digest_payload, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    families = primary["opened"] + primary["holdouts"]
    family_checks = [audit_family(record) for record in families]
    lower_checks = [
        item["transcripts_equal"] and item["values_differ"]
        and Fraction(item["alternative_value"]) < 0
        and item["queried"] == item["dimension"]
        for item in primary["lower_bound_witnesses"]
    ]
    imports = {node.module for node in ast.walk(ast.parse(Path(__file__).read_text()))
               if isinstance(node, ast.ImportFrom)}
    result = {
        "digest": digest,
        "digest_matches": digest == expected_digest,
        "families_passed": sum(family_checks),
        "families_total": len(family_checks),
        "lower_bounds_passed": sum(lower_checks),
        "lower_bounds_total": len(lower_checks),
        "production_imports": any(name and name.startswith("theorica")
                                  for name in imports),
        "production_source_contains_query_api":
            "def reconstruct_affine_scenario_payoffs(" in SOURCE.read_text(),
    }
    result["passed"] = (
        result["digest_matches"]
        and result["families_passed"] == result["families_total"]
        and result["lower_bounds_passed"] == result["lower_bounds_total"]
        and not result["production_imports"]
        and result["production_source_contains_query_api"]
    )
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
