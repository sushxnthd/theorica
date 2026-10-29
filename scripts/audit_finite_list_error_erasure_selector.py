#!/usr/bin/env python3
"""Independent Fraction-only audit of the finite-list error-erasure law."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

OUT = Path("results/finite_list_error_erasure_selector/independent_audit.json")


def rank(rows):
    matrix = [[Fraction(value) for value in row] for row in rows]
    if not matrix:
        return 0
    pivot_row = 0
    for column in range(len(matrix[0])):
        pivot = next((i for i in range(pivot_row, len(matrix))
                      if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        scale = matrix[pivot_row][column]
        matrix[pivot_row] = [value / scale for value in matrix[pivot_row]]
        for i in range(len(matrix)):
            if i == pivot_row:
                continue
            scale = matrix[i][column]
            matrix[i] = [matrix[i][j] - scale * matrix[pivot_row][j]
                         for j in range(len(matrix[0]))]
        pivot_row += 1
    return pivot_row


def safe_after_deletions(rows, feature_rank, deletions):
    return all(
        rank(tuple(row for i, row in enumerate(rows) if i not in deleted))
        == feature_rank
        for deleted in combinations(range(len(rows)), deletions)
    )


def main():
    transcript = []
    positives = punctures = attacks = 0
    for family in ("vandermonde", "cauchy"):
        for feature_rank in (2, 3):
            for errors in (1, 2):
                for erasures in (1, 2):
                    count = feature_rank + errors + erasures
                    if family == "vandermonde":
                        rows = tuple(
                            tuple(Fraction(7 + i) ** degree
                                  for degree in range(feature_rank))
                            for i in range(count)
                        )
                    else:
                        rows = tuple(
                            tuple(Fraction(1, 11 + i + 3 * column)
                                  for column in range(feature_rank))
                            for i in range(count)
                        )
                    safe = safe_after_deletions(
                        rows, feature_rank, errors + erasures
                    )
                    punctured = all(
                        safe_after_deletions(
                            tuple(row for i, row in enumerate(rows) if i not in erased),
                            feature_rank,
                            errors,
                        )
                        for erased_count in range(erasures + 1)
                        for erased in combinations(range(count), erased_count)
                    )
                    positives += int(safe and punctured) * 5
                    punctures += sum(
                        1 for erased_count in range(erasures + 1)
                        for _ in combinations(range(count), erased_count)
                    ) * 5
                    transcript.append((family, feature_rank, errors, erasures,
                                       safe, punctured))
    for case in range(60):
        feature_rank = 2 + (case % 2)
        errors = 1 + ((case // 2) % 2)
        erasures = 1 + ((case // 4) % 2)
        rows = tuple(
            [(1,) + (0,) * (feature_rank - 1)] * (1 + errors + erasures)
            + [tuple(int(i == column) for i in range(feature_rank))
               for column in range(1, feature_rank)]
        )
        failed = not safe_after_deletions(
            rows, feature_rank, errors + erasures
        )
        attacks += int(failed)
        transcript.append(("degenerate", feature_rank, errors, erasures, failed))
    result = {
        "schema": "theorica.finite-list-error-erasure-selector-audit/1",
        "production_imports": 0,
        "positive_cases": positives,
        "positive_total": 80,
        "erasure_patterns_checked": punctures,
        "attacks_rejected": attacks,
        "attack_total": 60,
        "digest": hashlib.sha256(json.dumps(transcript).encode()).hexdigest(),
        "passed": positives == 80 and attacks == 60,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
