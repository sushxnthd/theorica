#!/usr/bin/env python3
"""Independent stdlib-only audit of the joint error-erasure query law."""
from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from itertools import combinations
from pathlib import Path

PRIMARY = Path("results/error_erasure_feature_queries/primary.json")
OUT = Path("results/error_erasure_feature_queries/independent_audit.json")


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


def rows_for(record):
    feature_rank = record["rank"]
    count = record["scenario_count"]
    seed = record["seed"]
    xs = tuple(Fraction(3 * index - count + seed % 13, count + 11)
               for index in range(count))
    if record["family"] == "vandermonde":
        return tuple(tuple(x ** power for power in range(feature_rank)) for x in xs)
    return tuple(tuple(Fraction(1, x - (column + count + 3))
                             for column in range(feature_rank)) for x in xs)


def table_for(rows, seed):
    rng = random.Random(seed)
    actions = []
    for _ in range(2):
        coefficients = tuple(Fraction(rng.randint(-9, 9))
                             for _ in range(len(rows[0])))
        actions.append(tuple(sum(
            (coefficient * feature for coefficient, feature
             in zip(coefficients, row)), Fraction(0)
        ) for row in rows))
    return tuple(actions)


def decode(rows, selected, observations, available_positions, feature_rank, budget):
    candidates = set()
    for basis_positions in combinations(available_positions, feature_rank):
        coefficients = solve(
            tuple(rows[selected[position]] for position in basis_positions),
            tuple(observations[position] for position in basis_positions),
        )
        if coefficients is None:
            continue
        prediction = tuple(sum(
            (value * coefficient for value, coefficient in zip(row, coefficients)),
            Fraction(0),
        ) for row in rows)
        errors = sum(
            prediction[selected[position]] != observations[position]
            for position in available_positions
        )
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
    return max(min(
        probability * actions[0][scenario]
        + (1 - probability) * actions[1][scenario]
        for scenario in range(len(actions[0]))
    ) for probability in candidates)


def audit_case(record):
    rows = rows_for(record)
    table = table_for(rows, record["seed"])
    selected = tuple(record["query_indices"])
    errors = record["error_budget"]
    erasures = record["erasure_budget"]
    erased = set(range(erasures))
    corrupted = set(range(erasures, erasures + errors))
    available_positions = tuple(
        position for position, scenario in enumerate(selected)
        if scenario not in erased
    )
    decoded = []
    for action_index, action in enumerate(table):
        observations = {}
        for position, scenario in enumerate(selected):
            if scenario in erased:
                continue
            observations[position] = action[scenario] + (
                Fraction(2 * (action_index + 3) * (scenario + 5), 11)
                if scenario in corrupted else Fraction(0)
            )
        decoded.append(decode(
            rows, selected, observations, available_positions,
            record["rank"], errors,
        ))
    return (
        len(selected) == record["rank"] + 2 * errors + erasures
        and distance(tuple(rows[index] for index in selected), record["rank"])
        == 2 * errors + erasures + 1
        and tuple(decoded) == table
        and robust_value(tuple(decoded)) == Fraction(record["minimax_value"])
    )


def product(values):
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def audit_lower_bound(record):
    r, t, s = record["rank"], record["error_budget"], record["erasure_budget"]
    count, offset = record["query_count"], record["offset"]
    xs = tuple(Fraction(index + offset + 1, count + 5) for index in range(count))
    word = tuple(-product(tuple(x - root for root in xs[:r - 1])) for x in xs)
    support = tuple(index for index, value in enumerate(word) if value)
    erased = set(support[:s])
    remaining = tuple(index for index in support if index not in erased)
    left, right = set(remaining[:t]), set(remaining[t:])
    visible = tuple(index for index in range(count) if index not in erased)
    a = tuple(word[index] if index in left else Fraction(0) for index in visible)
    b = tuple(Fraction(0) if index in right else word[index] for index in visible)
    return len(support) == 2 * t + s and a == b and min(word) != 0


def main():
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    cases = primary["opened"] + primary["holdout"]
    audited = [audit_case(record) for record in cases]
    lower = [audit_lower_bound(record) for record in primary["lower_bounds"]]
    summary = {
        "schema": "theorica.error-erasure-feature-queries-audit/1",
        "reconstructions": len(audited),
        "reconstructions_passed": sum(audited),
        "lower_bounds": len(lower),
        "lower_bounds_passed": sum(lower),
        "production_imports": 0,
    }
    canonical = json.dumps(summary, sort_keys=True, separators=(",", ":"))
    summary["digest"] = hashlib.sha256(canonical.encode()).hexdigest()
    summary["passed"] = all(audited + lower)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
