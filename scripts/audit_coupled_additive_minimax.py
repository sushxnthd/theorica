#!/usr/bin/env python3
"""Independent Fraction-only checker; imports no THEORICA code."""
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path


def solve(rows, rhs):
    n = len(rows)
    a = [list(rows[i]) + [rhs[i]] for i in range(n)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col]), None)
        if pivot is None:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        a[col] = [x / scale for x in a[col]]
        for row in range(n):
            if row == col or not a[row][col]:
                continue
            scale = a[row][col]
            a[row] = [a[row][j] - scale * a[col][j] for j in range(n + 1)]
    return tuple(a[i][-1] for i in range(n))


def maximin(matrix):
    row_count, column_count = len(matrix), len(matrix[0])
    d = row_count
    planes = []
    for index in range(row_count - 1):
        row = [Fraction(0)] * d
        row[index] = 1
        planes.append((tuple(row), Fraction(0)))
    planes.append((tuple([Fraction(1)] * (d - 1) + [Fraction(0)]), Fraction(1)))
    for column in range(column_count):
        row = [Fraction(0)] * d
        base = Fraction(matrix[-1][column])
        for action in range(row_count - 1):
            row[action] = -(Fraction(matrix[action][column]) - base)
        row[-1] = 1
        planes.append((tuple(row), base))
    best = None
    for selected in combinations(range(len(planes)), d):
        x = solve(tuple(planes[i][0] for i in selected),
                  tuple(planes[i][1] for i in selected))
        if x is None:
            continue
        probabilities = x[:-1] + (1 - sum(x[:-1], Fraction(0)),)
        if any(p < 0 for p in probabilities):
            continue
        floor = min(sum(probabilities[row] * matrix[row][column]
                        for row in range(row_count))
                    for column in range(column_count))
        if x[-1] <= floor and (best is None or x[-1] > best):
            best = x[-1]
    assert best is not None
    return best


def main():
    games = tuple(tuple(tuple(entries[2 * r + c] for c in range(2))
                        for r in range(2))
                  for entries in product(range(3), repeat=4))
    universe = tuple(product(range(2), repeat=2))
    subsets = tuple(tuple(universe[i] for i in range(4) if mask & (1 << i))
                    for mask in range(1, 16))
    cases = zero = strict = 0
    for left in games:
        left_value = maximin(left)
        for right in games:
            baseline = left_value + maximin(right)
            actions = tuple(product(range(2), repeat=2))
            for vertices in subsets:
                expanded = tuple(
                    tuple(left[action[0]][vertex[0]] + right[action[1]][vertex[1]]
                          for vertex in vertices)
                    for action in actions
                )
                value = maximin(expanded)
                assert value >= baseline
                cases += 1
                zero += int(value == baseline)
                strict += int(value > baseline)
    assert (cases, zero, strict) == (98415, 60903, 37512)
    result = {
        "checker": "independent_fraction_only_no_production_import",
        "exhaustive_cases": cases,
        "zero_bonus_cases": zero,
        "strict_bonus_cases": strict,
        "status": "pass",
    }
    target = Path("results/coupled_additive_minimax/independent_audit.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
