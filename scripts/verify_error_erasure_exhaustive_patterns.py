#!/usr/bin/env python3
"""Exhaust every allowed error/erasure placement on small exact feature codes."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    reconstruct_corruption_resilient_feature_payoffs,
)

OUT = Path("results/error_erasure_feature_queries/exhaustive_patterns.json")
CONFIGS = tuple(
    (family, rank, errors, erasures)
    for family in ("vandermonde", "cauchy")
    for rank in (2, 3)
    for errors, erasures in ((1, 1), (1, 2))
)


def rows_for(family, rank, count):
    xs = tuple(Fraction(2 * index - count, count + 5) for index in range(count))
    if family == "vandermonde":
        return tuple(tuple(x ** power for power in range(rank)) for x in xs)
    return tuple(tuple(Fraction(1, x - (count + column + 2))
                             for column in range(rank)) for x in xs)


def table_for(rows):
    width = len(rows[0])
    coefficient_blocks = (
        (tuple(Fraction(2 * item + 1) for item in range(width)),
         tuple(Fraction(3 - item) for item in range(width))),
        (tuple(Fraction(-item - 2) for item in range(width)),
         tuple(Fraction(2 * item - 3) for item in range(width)),
         tuple(Fraction(item + 4, 3) for item in range(width))),
    )
    return tuple(tuple(tuple(sum(
        (coefficient * feature for coefficient, feature
         in zip(coefficients, row)), Fraction(0)
    ) for row in rows) for coefficients in block) for block in coefficient_blocks)


def evaluate_config(family, rank, error_budget, erasure_budget):
    query_count = rank + 2 * error_budget + erasure_budget
    rows = rows_for(family, rank, query_count)
    table = table_for(rows)
    total = 0
    failures = []
    for actual_erasures in range(erasure_budget + 1):
        for erased_tuple in combinations(range(query_count), actual_erasures):
            erased = set(erased_tuple)
            available = tuple(index for index in range(query_count)
                              if index not in erased)
            for actual_errors in range(error_budget + 1):
                for corrupted_tuple in combinations(available, actual_errors):
                    corrupted = set(corrupted_tuple)
                    total += 1

                    def oracle(index, erased=erased, corrupted=corrupted):
                        if index in erased:
                            return None
                        return tuple(tuple(
                            action[index] + (
                                Fraction((component + 2) * (action_index + 3)
                                         * (index + 5), 13)
                                if index in corrupted else Fraction(0)
                            )
                            for action_index, action in enumerate(component_actions)
                        ) for component, component_actions in enumerate(table))

                    result = reconstruct_corruption_resilient_feature_payoffs(
                        rows, oracle, payoff_in_feature_span_certified=True,
                        corruption_budget=error_budget,
                        erasure_budget=erasure_budget,
                    )
                    if not (
                        result.certificate_valid
                        and result.component_payoff_vectors == table
                        and result.erased_query_indices == tuple(sorted(erased))
                        and result.corrected_query_indices == tuple(sorted(corrupted))
                        and result.minimum_distance
                        == 2 * error_budget + erasure_budget + 1
                    ):
                        failures.append({
                            "actual_errors": actual_errors,
                            "actual_erasures": actual_erasures,
                            "corrupted": sorted(corrupted),
                            "erased": sorted(erased),
                        })
    return {
        "family": family, "rank": rank,
        "error_budget": error_budget, "erasure_budget": erasure_budget,
        "query_count": query_count, "placements": total,
        "failures": failures, "passed": not failures,
    }


def main():
    records = [evaluate_config(*config) for config in CONFIGS]
    payload = {
        "schema": "theorica.error-erasure-exhaustive-patterns/1",
        "configs": records,
        "summary": {
            "configurations": len(records),
            "configurations_passed": sum(record["passed"] for record in records),
            "placements": sum(record["placements"] for record in records),
            "failures": sum(len(record["failures"]) for record in records),
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
