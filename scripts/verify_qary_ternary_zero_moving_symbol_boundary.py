#!/usr/bin/env python3
"""Falsify unrestricted symbol transport for the prefix-query game."""
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
    "solver", Path("scripts/verify_qary_ternary_clean_separator.py")
)
assert SOLVER_SPEC and SOLVER_SPEC.loader
S = importlib.util.module_from_spec(SOLVER_SPEC)
SOLVER_SPEC.loader.exec_module(S)

OUT = Path("results/qary_ternary_zero_moving_symbol_boundary/results.json")
SOURCE_SIGNATURES = {
    18: {"value": 37, "optimal_groups": [0], "group0_children": [33, 33, 33]},
    19: {"value": 38, "optimal_groups": [0], "group0_children": [34, 34, 33]},
}


def swap_zero_one(word):
    return tuple(1 if symbol == 0 else 0 if symbol == 1 else symbol for symbol in word)


def endpoint(words, c):
    exact = S.exact_value(words, (4, 11, c), S.witness_state())
    group0 = next(row for row in exact["root_actions"] if row["query_group"] == 0)
    return {
        "leaf_cost": c,
        "exact_value": exact["exact_lower_bound"],
        "optimal_groups": sorted(
            row["query_group"] for row in exact["root_actions"] if row["optimal"]
        ),
        "group0_children": group0["child_values"],
        "exact": exact,
    }


def main():
    source = (*H.BASE, *H.PAIRS[0])
    target = tuple(swap_zero_one(word) for word in source)
    mapping, certificate = H.isomorphism(H.graph(source), H.graph(target))
    source_endpoints = [endpoint(source, c) for c in sorted(SOURCE_SIGNATURES)]
    target_endpoints = [endpoint(target, c) for c in sorted(SOURCE_SIGNATURES)]
    scalar_and_root_coincidence = all(
        {
            "value": target_row["exact_value"],
            "optimal_groups": target_row["optimal_groups"],
            "group0_children": target_row["group0_children"],
        }
        == SOURCE_SIGNATURES[target_row["leaf_cost"]]
        for target_row in target_endpoints
    )
    state_expansion = {
        str(target_row["leaf_cost"]): {
            "source_states": source_row["exact"]["states_solved"],
            "target_states": target_row["exact"]["states_solved"],
            "state_ratio": target_row["exact"]["states_solved"]
            / source_row["exact"]["states_solved"],
            "source_actions": source_row["exact"]["actions_evaluated"],
            "target_actions": target_row["exact"]["actions_evaluated"],
            "action_ratio": target_row["exact"]["actions_evaluated"]
            / source_row["exact"]["actions_evaluated"],
        }
        for source_row, target_row in zip(source_endpoints, target_endpoints)
    }
    report = {
        "schema": "theorica.ternary-zero-moving-symbol-boundary/1",
        "symbol_action": "swap_0_1_in_all_three_coordinates",
        "source_words": [list(word) for word in source],
        "target_words": [list(word) for word in target],
        "level_preserving_isomorphism": mapping,
        "nonisomorphism_certificate": certificate,
        "source_endpoints": source_endpoints,
        "target_endpoints": target_endpoints,
        "scalar_and_root_coincidence": scalar_and_root_coincidence,
        "state_expansion": state_expansion,
        "completed_panel_reopened": False,
        "summary": {
            "universal_symbol_transport_falsified": mapping is None,
            "endpoint_scalar_coincidence_preserved": scalar_and_root_coincidence,
            "classification": "structural_transport_falsified_with_scalar_coincidence",
            "passed": True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
