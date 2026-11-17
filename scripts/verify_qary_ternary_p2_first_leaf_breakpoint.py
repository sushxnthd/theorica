#!/usr/bin/env python3
"""Prospective exact test of the first P2 integer leaf-cost breakpoint."""
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

OUT = Path("results/qary_ternary_p2_first_leaf_breakpoint/results.json")
PREDICTIONS = {
    7: {"value": 33, "clean_children": [22, 22, 22]},
    8: {"value": 34, "clean_children": [23, 22, 22]},
}


def endpoint(words, c):
    state = S.witness_state()
    exact = S.exact_value(words, (4, 11, c), state)
    clean = S.clean_separator(H.rows(words), state)
    group3 = next(row for row in exact["root_actions"] if row["query_group"] == 3)
    predicted = PREDICTIONS[c]
    supported = (
        any(row["query_group"] == 3 for row in clean)
        and group3["optimal"]
        and group3["child_values"] == predicted["clean_children"]
        and exact["exact_lower_bound"]
        == exact["constructive_upper_bound"]
        == predicted["value"]
        and group3["action_value"] == predicted["value"]
    )
    return {
        "leaf_cost": c,
        "level_costs": [4, 11, c],
        "predicted_value": predicted["value"],
        "predicted_clean_children": predicted["clean_children"],
        "clean_separators": clean,
        "clean_group3_action": group3,
        "exact": exact,
        "prediction_supported": supported,
    }


def main():
    words = (*H.BASE, *H.PAIRS[2])
    endpoints = [endpoint(words, c) for c in sorted(PREDICTIONS)]
    supported = all(row["prediction_supported"] for row in endpoints)
    values = {row["leaf_cost"]: row["exact"]["exact_lower_bound"] for row in endpoints}
    first_breakpoint = 8 if values == {7: 33, 8: 34} else None
    report = {
        "schema": "theorica.ternary-p2-first-leaf-breakpoint/1",
        "family": "P2_WL_nonisomorphic",
        "words": [list(word) for word in words],
        "fixed_root_middle_costs": [4, 11],
        "prior_exact_endpoints": {"c1": 33, "c2": 33},
        "predicted_root_branch": "max(33,26+c)",
        "endpoints": endpoints,
        "first_integer_breakpoint": first_breakpoint,
        "constant_integer_chamber": {"minimum_c": 1, "maximum_c": 7, "value": 33},
        "cumulative_opened_reserved_cases": 8,
        "remaining_reserved_cases": 10,
        "summary": {
            "prediction_supported": supported and first_breakpoint == 8,
            "classification": (
                "first_integer_leaf_breakpoint_confirmed"
                if supported and first_breakpoint == 8
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
