#!/usr/bin/env python3
"""Prospective exact test of the clean-separator law on a second cost ray."""
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

OUT = Path("results/qary_ternary_clean_separator_second_ray/results.json")
LEVEL_COSTS = (4, 11, 2)
PREDICTED_VALUE = 33


def main():
    words = (*H.BASE, *H.PAIRS[2])
    state = S.witness_state()
    separators = S.clean_separator(H.rows(words), state)
    exact = S.exact_value(words, LEVEL_COSTS, state)
    optimal_groups = [
        row["query_group"] for row in exact["root_actions"] if row["optimal"]
    ]
    supported = (
        any(row["query_group"] == 3 for row in separators)
        and 3 in optimal_groups
        and exact["exact_lower_bound"]
        == exact["constructive_upper_bound"]
        == PREDICTED_VALUE
    )
    report = {
        "schema": "theorica.ternary-clean-separator-second-ray/1",
        "family": "P2_WL_nonisomorphic",
        "words": [list(word) for word in words],
        "witness_state": {
            "lie_counts": list(state[0]),
            "erasures_used": state[1],
            "remaining_copies": list(state[2]),
        },
        "clean_separators": separators,
        "prospective": {
            "level_costs": list(LEVEL_COSTS),
            "predicted_value": PREDICTED_VALUE,
            "predicted_optimal_query_group": 3,
            **exact,
        },
        "cumulative_opened_reserved_cases": 3,
        "remaining_reserved_cases": 15,
        "summary": {
            "prediction_supported": supported,
            "classification": (
                "clean_separator_cross_ray_law_supported"
                if supported
                else "clean_separator_cross_ray_law_falsified"
            ),
            "passed": True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
