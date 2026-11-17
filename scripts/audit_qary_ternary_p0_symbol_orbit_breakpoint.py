#!/usr/bin/env python3
"""Zero-production-import audit of P0 symbol-orbit breakpoint evidence."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_p0_symbol_orbit_breakpoint/results.json")
OUT = Path("results/qary_ternary_p0_symbol_orbit_breakpoint/audit.json")
EXPECTED_QUERY_MAP = [0, 1, 3, 2, 4, 6, 8, 10, 12, 9, 11, 5, 7]
EXPECTED = {
    18: {"children": [33, 33, 33], "value": 37},
    19: {"children": [34, 33, 34], "value": 38},
}


def main():
    source = json.loads(SOURCE.read_text())
    replay = []
    for row in source["endpoints"]:
        c = row["leaf_cost"]
        exact = row["exact"]
        group0 = row["root_group0_action"]
        expected = EXPECTED[c]
        root_minimum = min(action["action_value"] for action in exact["root_actions"])
        valid = (
            row["level_costs"] == [4, 11, c]
            and group0["child_values"] == expected["children"]
            and group0["action_value"] == expected["value"]
            and row["observed_optimal_groups"] == [0]
            and exact["exact_lower_bound"]
            == exact["constructive_upper_bound"]
            == root_minimum
            == expected["value"]
        )
        replay.append(
            {
                "leaf_cost": c,
                "independent_group0_children": expected["children"],
                "independent_group0_value": expected["value"],
                "independent_root_minimum": root_minimum,
                "valid": valid,
            }
        )

    values = {row["leaf_cost"]: row["independent_root_minimum"] for row in replay}
    breakpoint_holds = values == {18: 37, 19: 38}
    mapping_valid = (
        source["isomorphism_mapping"]["queries"] == EXPECTED_QUERY_MAP
        and source["isomorphism_mapping"]["completions"] == list(range(10))
        and source["isomorphism_certificate"]["mapping_edge_checked"] is True
    )
    inference_consistent = (
        (source["first_integer_breakpoint"] == 19) == breakpoint_holds
        and (source["constant_integer_chamber"] is not None) == breakpoint_holds
    )
    count_valid = (
        source["cumulative_opened_reserved_cases"] == 18
        and source["remaining_reserved_cases"] == 0
    )
    passed = (
        all(row["valid"] for row in replay)
        and breakpoint_holds
        and mapping_valid
        and inference_consistent
        and count_valid
    )
    report = {
        "schema": "theorica.ternary-p0-symbol-orbit-breakpoint-audit/1",
        "production_imports": 0,
        "endpoint_replay": replay,
        "predicted_breakpoint_holds": breakpoint_holds,
        "mapping_valid": mapping_valid,
        "inference_consistent": inference_consistent,
        "reserved_count_valid": count_valid,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
