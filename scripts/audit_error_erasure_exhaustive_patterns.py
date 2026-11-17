#!/usr/bin/env python3
"""Independent rank/distance audit of every enumerated fault placement."""
from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from itertools import combinations
from pathlib import Path

PRIMARY = Path("results/error_erasure_feature_queries/exhaustive_patterns.json")
OUT = Path("results/error_erasure_feature_queries/exhaustive_patterns_audit.json")


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


def distance(rows, feature_rank):
    maximum_zeros = 0
    for size in range(feature_rank):
        for indices in combinations(range(len(rows)), size):
            basis = tuple(rows[index] for index in indices)
            if rank(basis) != size:
                continue
            zero_count = sum(rank(basis + (row,)) == size for row in rows)
            maximum_zeros = max(maximum_zeros, zero_count)
    return len(rows) - maximum_zeros


def rows_for(record):
    count, feature_rank = record["query_count"], record["rank"]
    xs = tuple(Fraction(2 * index - count, count + 5) for index in range(count))
    if record["family"] == "vandermonde":
        return tuple(tuple(x ** power for power in range(feature_rank)) for x in xs)
    return tuple(tuple(Fraction(1, x - (count + column + 2))
                             for column in range(feature_rank)) for x in xs)


def audit_record(record):
    rows = rows_for(record)
    q, t, s, r = (record["query_count"], record["error_budget"],
                  record["erasure_budget"], record["rank"])
    erasure_checks = 0
    distance_failures = 0
    for erasures in range(s + 1):
        for erased in combinations(range(q), erasures):
            erased_set = set(erased)
            punctured = tuple(row for index, row in enumerate(rows)
                              if index not in erased_set)
            erasure_checks += 1
            if rank(punctured) != r or distance(punctured, r) < 2 * t + 1:
                distance_failures += 1
    placements = sum(
        math.comb(q, erasures)
        * sum(math.comb(q - erasures, errors) for errors in range(t + 1))
        for erasures in range(s + 1)
    )
    return {
        "family": record["family"], "rank": r,
        "error_budget": t, "erasure_budget": s,
        "erasure_patterns_checked": erasure_checks,
        "distance_failures": distance_failures,
        "placements_recomputed": placements,
        "passed": distance_failures == 0 and placements == record["placements"],
    }


def main():
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    records = [audit_record(record) for record in primary["configs"]]
    payload = {
        "schema": "theorica.error-erasure-exhaustive-patterns-audit/1",
        "records": records,
        "summary": {
            "configurations": len(records),
            "configurations_passed": sum(record["passed"] for record in records),
            "erasure_patterns_checked": sum(
                record["erasure_patterns_checked"] for record in records
            ),
            "placements_recomputed": sum(
                record["placements_recomputed"] for record in records
            ),
            "production_imports": 0,
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(canonical.encode()).hexdigest()
    payload["passed"] = all(record["passed"] for record in records)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({**payload["summary"], "digest": payload["digest"],
                      "passed": payload["passed"]}, indent=2, sort_keys=True))
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
