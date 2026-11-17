#!/usr/bin/env python3
"""Prospective exact test of the no-clean branch on a second cost ray."""
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

PARTITION_SPEC = importlib.util.spec_from_file_location(
    "no_clean_solver", Path("scripts/verify_qary_ternary_no_clean_separator.py")
)
assert PARTITION_SPEC and PARTITION_SPEC.loader
N = importlib.util.module_from_spec(PARTITION_SPEC)
PARTITION_SPEC.loader.exec_module(N)

OUT = Path("results/qary_ternary_no_clean_separator_second_ray/results.json")
PRIOR = Path("results/qary_ternary_clean_separator_second_ray/results.json")
LEVEL_COSTS = (4, 11, 2)
PREDICTED_VALUE = 37


def main():
    words = (*H.BASE, *H.PAIRS[0])
    state = S.witness_state()
    partitions = N.middle_partitions(H.rows(words), state)
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
        "schema": "theorica.ternary-no-clean-separator-second-ray/1",
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
        "cumulative_opened_reserved_cases": 4,
        "remaining_reserved_cases": 14,
        "summary": {
            "prediction_supported": supported,
            "classification": (
                "clean_separator_two_ray_boundary_supported"
                if supported
                else "second_ray_no_clean_branch_falsified"
            ),
            "passed": True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
