#!/usr/bin/env python3
"""Prospective exact test of the no-clean-separator residual branch."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HELPER_SPEC = importlib.util.spec_from_file_location(
    "helper", Path("scripts/verify_qary_ternary_obstruction_transfer_boundary.py")
)
assert HELPER_SPEC and HELPER_SPEC.loader
H = importlib.util.module_from_spec(HELPER_SPEC)
HELPER_SPEC.loader.exec_module(H)

SOLVER_SPEC = importlib.util.spec_from_file_location(
    "clean_solver", Path("scripts/verify_qary_ternary_clean_separator.py")
)
assert SOLVER_SPEC and SOLVER_SPEC.loader
S = importlib.util.module_from_spec(SOLVER_SPEC)
SOLVER_SPEC.loader.exec_module(S)

OUT = Path("results/qary_ternary_no_clean_separator/results.json")
PRIOR = Path("results/qary_ternary_clean_separator/results.json")
LEVEL_COSTS = (3, 10, 3)
PREDICTED_VALUE = 33


def middle_partitions(rows, state):
    counts, _, remaining = state
    zero = {i for i, count in enumerate(counts) if count == 0}
    one = {i for i, count in enumerate(counts) if count == 1}
    partitions = []
    for query, copies in enumerate(remaining):
        if not copies or H.level(query) != 1:
            continue
        grouped = {}
        for index, answer in enumerate(rows[query]):
            grouped.setdefault(answer, []).append(index)
        cells = [
            {
                "answer": answer,
                "zero_lie": sorted(zero.intersection(members)),
                "one_lie": sorted(one.intersection(members)),
            }
            for answer, members in sorted(grouped.items())
        ]
        zero_cells = [cell for cell in cells if cell["zero_lie"]]
        clean = (
            len(zero_cells) == len(zero)
            and all(len(cell["zero_lie"]) == 1 for cell in zero_cells)
            and all(not cell["one_lie"] for cell in zero_cells)
        )
        partitions.append(
            {
                "query_group": query,
                "remaining_copies": copies,
                "cells": cells,
                "clean_separator": clean,
            }
        )
    return partitions


def main():
    words = (*H.BASE, *H.PAIRS[0])
    state = S.witness_state()
    partitions = middle_partitions(H.rows(words), state)
    prospective = S.exact_value(words, LEVEL_COSTS, state)
    prior = json.loads(PRIOR.read_text())
    p2_value = prior["prospective"]["exact_lower_bound"]
    no_clean_separator = not any(row["clean_separator"] for row in partitions)
    supported = (
        no_clean_separator
        and prospective["exact_lower_bound"]
        == prospective["constructive_upper_bound"]
        == PREDICTED_VALUE
        and PREDICTED_VALUE - p2_value == LEVEL_COSTS[0]
    )
    report = {
        "schema": "theorica.ternary-no-clean-separator/1",
        "family": "P0_isomorphic_orbit_representative",
        "words": [list(word) for word in words],
        "witness_state": {
            "lie_counts": list(state[0]),
            "erasures_used": state[1],
            "remaining_copies": list(state[2]),
        },
        "middle_partitions": partitions,
        "clean_separator_present": not no_clean_separator,
        "prospective": {
            "level_costs": list(LEVEL_COSTS),
            "predicted_value": PREDICTED_VALUE,
            **prospective,
        },
        "prior_P2_exact_value": p2_value,
        "exact_P0_minus_P2_gap": prospective["exact_lower_bound"] - p2_value,
        "cumulative_opened_reserved_cases": 2,
        "remaining_reserved_cases": 16,
        "summary": {
            "prediction_supported": supported,
            "classification": (
                "clean_separator_two_branch_boundary_supported"
                if supported
                else "no_clean_separator_branch_falsified"
            ),
            "passed": True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
