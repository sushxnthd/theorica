#!/usr/bin/env python3
"""Prospective exact test of the first P0 integer leaf-cost breakpoint."""
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

OUT = Path("results/qary_ternary_p0_first_leaf_breakpoint/results.json")
PREDICTIONS = {
    18: {"value": 37, "group0_children": [33, 33, 33]},
    19: {"value": 38, "group0_children": [34, 34, 33]},
}


def endpoint(words, c):
    state = S.witness_state()
    exact = S.exact_value(words, (4, 11, c), state)
    group0 = next(row for row in exact["root_actions"] if row["query_group"] == 0)
    prediction = PREDICTIONS[c]
    supported = (
        group0["optimal"]
        and group0["child_values"] == prediction["group0_children"]
        and exact["exact_lower_bound"]
        == exact["constructive_upper_bound"]
        == prediction["value"]
    )
    return {
        "leaf_cost": c,
        "level_costs": [4, 11, c],
        "predicted_value": prediction["value"],
        "predicted_group0_children": prediction["group0_children"],
        "root_group0_action": group0,
        "observed_optimal_groups": sorted(
            row["query_group"] for row in exact["root_actions"] if row["optimal"]
        ),
        "exact": exact,
        "prediction_supported": supported,
    }


def main():
    words = (*H.BASE, *H.PAIRS[0])
    endpoints = [endpoint(words, c) for c in sorted(PREDICTIONS)]
    supported = all(row["prediction_supported"] for row in endpoints)
    values = {row["leaf_cost"]: row["exact"]["exact_lower_bound"] for row in endpoints}
    first_breakpoint = 19 if values == {18: 37, 19: 38} else None
    report = {
        "schema": "theorica.ternary-p0-first-leaf-breakpoint/1",
        "family": "P0_isomorphic_orbit_representative",
        "words": [list(word) for word in words],
        "fixed_root_middle_costs": [4, 11],
        "prior_exact_endpoints": {"c1": 37, "c2": 37},
        "predicted_root_branch": "max(37,19+c)",
        "endpoints": endpoints,
        "first_integer_breakpoint": first_breakpoint,
        "constant_integer_chamber": (
            {"minimum_c": 1, "maximum_c": 18, "value": 37}
            if first_breakpoint == 19
            else None
        ),
        "cumulative_opened_reserved_cases": 12,
        "remaining_reserved_cases": 6,
        "summary": {
            "prediction_supported": supported and first_breakpoint == 19,
            "classification": (
                "first_integer_leaf_breakpoint_confirmed"
                if supported and first_breakpoint == 19
                else "first_integer_leaf_breakpoint_falsified"
            ),
            "passed": True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
