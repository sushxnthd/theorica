#!/usr/bin/env python3
"""Prospective breakpoint transfer to an unseen P0 symbol-orbit family."""
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

OUT = Path("results/qary_ternary_p0_symbol_orbit_breakpoint/results.json")
EXPECTED_QUERY_MAP = [0, 1, 3, 2, 4, 6, 8, 10, 12, 9, 11, 5, 7]
PREDICTIONS = {
    18: {"value": 37, "group0_children": [33, 33, 33]},
    19: {"value": 38, "group0_children": [34, 33, 34]},
}


def endpoint(words, c):
    exact = S.exact_value(words, (4, 11, c), S.witness_state())
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
    source = (*H.BASE, *H.PAIRS[0])
    target = H.transform(source, 0b111)
    full_mapping, certificate = H.isomorphism(H.graph(source), H.graph(target))
    if full_mapping is None:
        raise RuntimeError("frozen source-target isomorphism disappeared")
    mapping = H.compact(full_mapping, source, target)
    mapping_supported = (
        mapping["queries"] == EXPECTED_QUERY_MAP
        and mapping["completions"] == list(range(10))
        and certificate["mapping_edge_checked"]
    )

    endpoints = [endpoint(target, c) for c in sorted(PREDICTIONS)]
    values = {row["leaf_cost"]: row["exact"]["exact_lower_bound"] for row in endpoints}
    first_breakpoint = 19 if values == {18: 37, 19: 38} else None
    supported = (
        mapping_supported
        and all(row["prediction_supported"] for row in endpoints)
        and first_breakpoint == 19
    )
    report = {
        "schema": "theorica.ternary-p0-symbol-orbit-breakpoint/1",
        "source_family": "P0",
        "symbol_action": "swap_1_2_in_all_three_coordinates",
        "words": [list(word) for word in target],
        "isomorphism_mapping": mapping,
        "isomorphism_certificate": certificate,
        "fixed_root_middle_costs": [4, 11],
        "endpoints": endpoints,
        "first_integer_breakpoint": first_breakpoint,
        "constant_integer_chamber": (
            {"minimum_c": 1, "maximum_c": 18, "value": 37}
            if first_breakpoint == 19
            else None
        ),
        "cumulative_opened_reserved_cases": 18,
        "remaining_reserved_cases": 0,
        "summary": {
            "mapping_supported": mapping_supported,
            "prediction_supported": supported,
            "classification": (
                "symbol_orbit_breakpoint_transfer_confirmed"
                if supported
                else "symbol_orbit_breakpoint_transfer_falsified"
            ),
            "passed": True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
