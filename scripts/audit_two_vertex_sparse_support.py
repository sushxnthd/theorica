#!/usr/bin/env python3
"""Independent exact audit; imports no THEORICA production code."""
import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations, product


def solve(matrix):
    n = len(matrix)
    pure_values = tuple(min(row) for row in matrix)
    pure = max(pure_values)
    pure_index = min(i for i, value in enumerate(pure_values) if value == pure)
    candidates = []
    for i, j in combinations(range(n), 2):
        di = matrix[i][0] - matrix[i][1]
        dj = matrix[j][0] - matrix[j][1]
        if di * dj < 0:
            w = dj / (dj - di)
            candidates.append((w * matrix[i][0] + (1 - w) * matrix[j][0], i, j, w))
    crossing_value = max((row[0] for row in candidates), default=pure)
    probabilities = [Fraction(0)] * n
    if crossing_value > pure:
        value = crossing_value
        _, i, j, w = min(row for row in candidates if row[0] == value)
        probabilities[i], probabilities[j] = w, 1 - w
    else:
        value = pure
        probabilities[pure_index] = Fraction(1)

    qs = {Fraction(0), Fraction(1)}
    for i, j in combinations(range(n), 2):
        si = matrix[i][0] - matrix[i][1]
        sj = matrix[j][0] - matrix[j][1]
        if si != sj:
            q = (matrix[j][1] - matrix[i][1]) / (si - sj)
            if 0 <= q <= 1:
                qs.add(q)
    dual_rows = [(max(q * a + (1 - q) * b for a, b in matrix), q) for q in qs]
    dual_value = min(row[0] for row in dual_rows)
    q = min(row[1] for row in dual_rows if row[0] == dual_value)
    assert dual_value == value
    return tuple(probabilities), (q, 1 - q), value, value > pure


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with open(args.primary, encoding="utf-8") as handle:
        primary = json.load(handle)
    grid = tuple(Fraction(x) for x in range(3))
    digest = hashlib.sha256()
    total = strict = 0
    by_actions = {}
    for action_count in (3, 4):
        cases = strict_cases = 0
        for entries in product(grid, repeat=2 * action_count):
            matrix = tuple((entries[2 * i], entries[2 * i + 1])
                           for i in range(action_count))
            probabilities, dual, value, is_strict = solve(matrix)
            digest.update(repr((matrix, probabilities, dual, value, is_strict)).encode())
            cases += 1
            strict_cases += int(is_strict)
            total += 1
            strict += int(is_strict)
        by_actions[str(action_count)] = {"cases": cases, "strict_cases": strict_cases}
    assert primary["exact_cases"] == total
    assert primary["strict_cases"] == strict
    assert primary["by_actions"] == by_actions
    assert primary["value_digest"] == digest.hexdigest()
    result = {
        "schema": "theorica.two-vertex-sparse-support.audit.v1",
        "status": "pass",
        "independent": True,
        "exact_cases": total,
        "strict_cases": strict,
        "by_actions": by_actions,
        "mismatches": 0,
        "value_digest": digest.hexdigest(),
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
