#!/usr/bin/env python3
"""Prospective exact test of the P2 high-leaf-cost root-action transition."""
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

OUT = Path("results/qary_ternary_p2_root_action_transition/results.json")
PREDICTIONS = {
    11: {
        "value": 37,
        "optimal_groups": [0, 3],
        "group0_children": [26, 26, 33],
        "group3_children": [26, 22, 22],
    },
    12: {
        "value": 37,
        "optimal_groups": [0],
        "group0_children": [27, 27, 33],
        "group3_children": [27, 22, 22],
    },
}


def endpoint(words, c):
    state = S.witness_state()
    exact = S.exact_value(words, (4, 11, c), state)
    clean = S.clean_separator(H.rows(words), state)
    actions = {row["query_group"]: row for row in exact["root_actions"]}
    prediction = PREDICTIONS[c]
    optimal_groups = sorted(
        row["query_group"] for row in exact["root_actions"] if row["optimal"]
    )
    supported = (
        any(row["query_group"] == 3 for row in clean)
        and actions[0]["child_values"] == prediction["group0_children"]
        and actions[3]["child_values"] == prediction["group3_children"]
        and optimal_groups == prediction["optimal_groups"]
        and exact["exact_lower_bound"]
        == exact["constructive_upper_bound"]
        == prediction["value"]
    )
    return {
        "leaf_cost": c,
        "level_costs": [4, 11, c],
        "predicted_value": prediction["value"],
        "predicted_optimal_groups": prediction["optimal_groups"],
        "predicted_group0_children": prediction["group0_children"],
        "predicted_group3_children": prediction["group3_children"],
        "observed_optimal_groups": optimal_groups,
        "clean_separators": clean,
        "root_group0_action": actions[0],
        "clean_group3_action": actions[3],
        "exact": exact,
        "prediction_supported": supported,
    }


def main():
    words = (*H.BASE, *H.PAIRS[2])
    endpoints = [endpoint(words, c) for c in sorted(PREDICTIONS)]
    supported = all(row["prediction_supported"] for row in endpoints)
    report = {
        "schema": "theorica.ternary-p2-root-action-transition/1",
        "family": "P2_WL_nonisomorphic",
        "words": [list(word) for word in words],
        "fixed_root_middle_costs": [4, 11],
        "prior_exact_boundary": {"c7": 33, "c8": 34},
        "predicted_clean_branch": "max(33,26+c)",
        "predicted_root_competitor": 37,
        "endpoints": endpoints,
        "transition": {
            "collision_leaf_cost": 11,
            "strict_handoff_leaf_cost": 12,
            "from_query_group": 3,
            "to_query_group": 0,
        },
        "cumulative_opened_reserved_cases": 10,
        "remaining_reserved_cases": 8,
        "summary": {
            "prediction_supported": supported,
            "classification": (
                "root_action_collision_and_handoff_confirmed"
                if supported
                else "root_action_transition_falsified"
            ),
            "passed": True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
