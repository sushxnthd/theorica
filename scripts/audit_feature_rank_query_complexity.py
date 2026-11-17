#!/usr/bin/env python3
"""Independent stdlib-only audit of the feature-rank query law."""
from __future__ import annotations

import ast
import hashlib
import json
import random
from fractions import Fraction
from itertools import combinations
from pathlib import Path

PRIMARY = Path("results/feature_rank_query_complexity/primary.json")
OUT = Path("results/feature_rank_query_complexity/independent_audit.json")


def solve(rows, rhs):
    n = len(rows)
    matrix = [list(rows[index]) + [rhs[index]] for index in range(n)]
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
            matrix[row] = [matrix[row][item] - scale * matrix[column][item]
                           for item in range(n + 1)]
    return tuple(matrix[row][-1] for row in range(n))


def rank(rows):
    matrix = [list(row) for row in rows]
    if not matrix:
        return 0
    result = 0
    for column in range(len(matrix[0])):
        pivot = next((row for row in range(result, len(matrix))
                      if matrix[row][column]), None)
        if pivot is None:
            continue
        matrix[result], matrix[pivot] = matrix[pivot], matrix[result]
        scale = matrix[result][column]
        matrix[result] = [value / scale for value in matrix[result]]
        for row in range(len(matrix)):
            if row != result and matrix[row][column]:
                scale = matrix[row][column]
                matrix[row] = [matrix[row][item] - scale * matrix[result][item]
                               for item in range(len(matrix[0]))]
        result += 1
    return result


def simplex_points(dimension, count):
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


def rows_and_table(record):
    feature_rank = record["rank"]
    base = tuple((Fraction(1),) + point for point in simplex_points(
        feature_rank - 1, record["scenario_count"]))
    rows = (tuple(row + (sum(row, Fraction(0)), 2 * row[0] - row[1], row[-1])
                  for row in base) if record["redundant"] else base)
    rng = random.Random(record["seed"])
    components = []
    for component in range(2 + record["seed"] % 4):
        actions = []
        for action in range(2 + (component + record["seed"]) % 2):
            coefficients = [Fraction(rng.randint(-5, 5))
                            for _ in range(feature_rank)]
            if component == 0 and action < feature_rank - 1:
                coefficients = [Fraction(0)] + [
                    Fraction(index == action) for index in range(feature_rank - 1)
                ]
            actions.append(tuple(sum((coefficient * value
                                      for coefficient, value
                                      in zip(coefficients, row)), Fraction(0))
                                 for row in base))
        components.append(tuple(actions))
    return rows, tuple(components)


def audit_record(record):
    rows, table = rows_and_table(record)
    indices = tuple(record["query_indices"])
    expected_rank = rank(rows)
    if expected_rank != record["rank"] or len(indices) != expected_rank:
        return False
    basis = tuple(rows[index] for index in indices)
    width = len(rows[0])
    pivots = next((columns for columns in combinations(range(width), expected_rank)
                   if solve(tuple(tuple(basis[row][column] for column in columns)
                                  for row in range(expected_rank)),
                            (Fraction(0),) * expected_rank) is not None), None)
    if pivots is None or tuple(record["pivot_columns"]) != pivots:
        return False
    pivot_matrix = tuple(tuple(basis[row][column]
                               for row in range(expected_rank))
                         for column in pivots)
    weights = [solve(pivot_matrix, tuple(row[column] for column in pivots))
               for row in rows]
    if any(item is None for item in weights):
        return False
    reconstructed = tuple(tuple(tuple(
        sum((weights[scenario][position] * action[indices[position]]
             for position in range(expected_rank)), Fraction(0))
        for scenario in range(len(rows))) for action in component)
        for component in table)
    return reconstructed == table and record["query_count"] == expected_rank


def main():
    primary = json.loads(PRIMARY.read_text())
    payload = dict(primary)
    expected_digest = payload.pop("digest")
    payload.pop("passed")
    digest = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    records = primary["opened"] + primary["holdouts"]
    reconstruction = [audit_record(record) for record in records]
    polynomial = [
        item["passed"] and item["affine_certificate_invalid"]
        and item["query_count"] == item["feature_rank"]
        for item in primary["polynomial_witnesses"]
    ]
    lower = [
        item["passed"] and item["transcripts_equal"] and item["values_differ"]
        and item["queried"] + 1 == item["rank"]
        and Fraction(item["alternative_value"]) < 0
        for item in primary["lower_bound_witnesses"]
    ]
    imports = {node.module for node in ast.walk(ast.parse(Path(__file__).read_text()))
               if isinstance(node, ast.ImportFrom)}
    result = {
        "digest": digest,
        "digest_matches": digest == expected_digest,
        "reconstructions_passed": sum(reconstruction),
        "reconstructions_total": len(reconstruction),
        "polynomial_witnesses_passed": sum(polynomial),
        "polynomial_witnesses_total": len(polynomial),
        "lower_bounds_passed": sum(lower),
        "lower_bounds_total": len(lower),
        "production_imports": any(name and name.startswith("theorica")
                                  for name in imports),
    }
    result["passed"] = all((
        result["digest_matches"],
        result["reconstructions_passed"] == result["reconstructions_total"],
        result["polynomial_witnesses_passed"]
        == result["polynomial_witnesses_total"],
        result["lower_bounds_passed"] == result["lower_bounds_total"],
        not result["production_imports"],
    ))
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
