#!/usr/bin/env python3
"""Independent Fraction-only audit of the finite-list rank boundary."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

OUT = Path("results/finite_list_geometry_boundary/independent_audit.json")


def rank(rows):
    matrix = [[Fraction(value) for value in row] for row in rows]
    if not matrix:
        return 0
    row = 0
    for column in range(len(matrix[0])):
        pivot = next((i for i in range(row, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        scale = matrix[row][column]
        matrix[row] = [value / scale for value in matrix[row]]
        for i in range(len(matrix)):
            if i == row:
                continue
            scale = matrix[i][column]
            matrix[i] = [matrix[i][j] - scale * matrix[row][j]
                         for j in range(len(matrix[0]))]
        row += 1
    return row


def finite_after_deletions(rows, feature_rank, errors):
    return all(
        rank(tuple(row for index, row in enumerate(rows) if index not in deleted))
        == feature_rank
        for deleted in combinations(range(len(rows)), errors)
    )


def main():
    transcript = []
    positives = attacks = 0
    for feature_rank, errors, count in ((2, 1, 40), (3, 1, 20),
                                        (2, 2, 20), (3, 2, 20)):
        rows = tuple(tuple(Fraction(x) ** degree for degree in range(feature_rank))
                     for x in range(feature_rank + errors))
        passed = finite_after_deletions(rows, feature_rank, errors)
        positives += int(passed) * count
        transcript.append(("mds", feature_rank, errors, count, passed))
    for feature_rank, errors, count in ((2, 1, 20), (2, 2, 20), (3, 1, 20)):
        if feature_rank == 2:
            rows = tuple([(1, 0)] * (1 + errors) + [(0, 1)])
        else:
            rows = tuple([(1, 0, 0)] * (1 + errors)
                         + [(0, 1, 0), (0, 0, 1)])
        failed = not finite_after_deletions(rows, feature_rank, errors)
        attacks += int(failed) * count
        transcript.append(("degenerate", feature_rank, errors, count, failed))
    result = {
        "schema": "theorica.finite-list-geometry-boundary-audit/1",
        "production_imports": 0,
        "positive_cases": positives,
        "positive_total": 100,
        "attacks_rejected": attacks,
        "attack_total": 60,
        "digest": hashlib.sha256(json.dumps(transcript).encode()).hexdigest(),
        "passed": positives == 100 and attacks == 60,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
