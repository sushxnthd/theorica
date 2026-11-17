#!/usr/bin/env python3
"""Independent stdlib-only audit for corruption-resilient feature queries."""
from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from itertools import combinations
from pathlib import Path

PRIMARY = Path("results/corruption_resilient_feature_queries/primary.json")
OUT = Path("results/corruption_resilient_feature_queries/independent_audit.json")


def rank(rows):
    matrix = [list(row) for row in rows]
    result = 0
    if not matrix:
        return 0
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


def solve(rows, rhs):
    size = len(rows)
    matrix = [list(rows[index]) + [rhs[index]] for index in range(size)]
    for column in range(size):
        pivot = next((row for row in range(column, size)
                      if matrix[row][column]), None)
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        scale = matrix[column][column]
        matrix[column] = [value / scale for value in matrix[column]]
        for row in range(size):
            if row == column or not matrix[row][column]:
                continue
            scale = matrix[row][column]
            matrix[row] = [matrix[row][item] - scale * matrix[column][item]
                           for item in range(size + 1)]
    return tuple(matrix[row][-1] for row in range(size))


def distance(rows, feature_rank):
    maximum_zeros = 0
    for size in range(feature_rank):
        for indices in combinations(range(len(rows)), size):
            basis = tuple(rows[index] for index in indices)
            if rank(basis) != size:
                continue
            maximum_zeros = max(maximum_zeros, sum(
                rank(basis + (row,)) == size for row in rows
            ))
    return len(rows) - maximum_zeros


def rows_and_table(record):
    feature_rank = record["rank"]
    count = record["scenario_count"]
    seed = record["seed"]
    xs = tuple(Fraction(3 * index - count + seed % 11, count + 7)
               for index in range(count))
    rows = tuple(tuple(x ** power for power in range(feature_rank)) for x in xs)
    rng = random.Random(seed)
    actions = []
    for _ in range(2):
        coefficients = tuple(Fraction(rng.randint(-7, 7))
                             for _ in range(feature_rank))
        actions.append(tuple(sum(
            (coefficient * feature for coefficient, feature
             in zip(coefficients, row)), Fraction(0)
        ) for row in rows))
    return rows, tuple(actions)


def decode(rows, selected, observations, feature_rank, budget):
    queried_rows = tuple(rows[index] for index in selected)
    candidates = set()
    for basis_indices in combinations(range(len(selected)), feature_rank):
        matrix = tuple(queried_rows[index] for index in basis_indices)
        coefficients = solve(
            matrix,
            tuple(observations[index] for index in basis_indices),
        )
        if coefficients is None:
            continue
        prediction = tuple(sum(
            (value * coefficient for value, coefficient in zip(row, coefficients)),
            Fraction(0),
        ) for row in rows)
        errors = sum(prediction[scenario] != observations[position]
                     for position, scenario in enumerate(selected))
        if errors <= budget:
            candidates.add(prediction)
    return next(iter(candidates)) if len(candidates) == 1 else None


def robust_value(actions):
    candidates = {Fraction(0), Fraction(1)}
    for left, right in combinations(range(len(actions[0])), 2):
        slope_left = actions[0][left] - actions[1][left]
        slope_right = actions[0][right] - actions[1][right]
        denominator = slope_left - slope_right
        if denominator:
            probability = (actions[1][right] - actions[1][left]) / denominator
            if 0 <= probability <= 1:
                candidates.add(probability)
    values = [min(
        probability * actions[0][scenario]
        + (1 - probability) * actions[1][scenario]
        for scenario in range(len(actions[0]))
    ) for probability in candidates]
    return max(values)


def audit_case(record):
    rows, table = rows_and_table(record)
    selected = tuple(record["query_indices"])
    budget = record["corruption_budget"]
    corrupt = set(range(budget))
    decoded = []
    for action_index, action in enumerate(table):
        observations = tuple(
            action[index] + (
                Fraction(2 * (action_index + 3) * (index + 5), 7)
                if index in corrupt else Fraction(0)
            )
            for index in selected
        )
        decoded.append(decode(rows, selected, observations, record["rank"], budget))
    return (
        len(selected) == record["rank"] + 2 * budget
        and distance(tuple(rows[index] for index in selected), record["rank"])
        == 2 * budget + 1
        and tuple(decoded) == table
        and robust_value(tuple(decoded)) == Fraction(record["minimax_value"])
    )


def main():
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    cases = primary["opened"] + primary["holdout"]
    audited = [audit_case(record) for record in cases]
    lower_bounds = [
        item["codeword_weight"] == 2 * item["corruption_budget"]
        and item["transcripts_equal"]
        and item["zero_corruptions"] == item["corruption_budget"]
        and item["alternative_corruptions"] == item["corruption_budget"]
        and item["robust_values_differ"]
        for item in primary["lower_bounds"]
    ]
    summary = {
        "schema": "theorica.corruption-resilient-feature-queries-audit/1",
        "reconstructions": len(audited),
        "reconstructions_passed": sum(audited),
        "lower_bounds": len(lower_bounds),
        "lower_bounds_passed": sum(lower_bounds),
        "production_imports": 0,
    }
    canonical = json.dumps(summary, sort_keys=True, separators=(",", ":"))
    summary["digest"] = hashlib.sha256(canonical.encode()).hexdigest()
    summary["passed"] = all(audited + lower_bounds)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
