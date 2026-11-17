#!/usr/bin/env python3
"""Zero-production-import audit of P2 symbol-orbit breakpoint evidence."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_p2_symbol_orbit_breakpoint/results.json")
OUT = Path("results/qary_ternary_p2_symbol_orbit_breakpoint/audit.json")
EXPECTED_QUERY_MAP = [0, 1, 3, 2, 4, 6, 8, 10, 12, 9, 11, 5, 7]


def main():
    source = json.loads(SOURCE.read_text())
    replay = []
    for row in source["endpoints"]:
        c = row["leaf_cost"]
        exact = row["exact"]
        group2 = row["root_group2_action"]
        expected_children = [15 + c, 22, 22]
        expected_value = max(33, 26 + c)
        root_minimum = min(action["action_value"] for action in exact["root_actions"])
        valid = (
            row["level_costs"] == [4, 11, c]
            and group2["child_values"] == expected_children
            and group2["action_value"] == expected_value
            and exact["exact_lower_bound"]
            == exact["constructive_upper_bound"]
            == root_minimum
        )
        replay.append(
            {
                "leaf_cost": c,
                "independent_group2_children": expected_children,
                "independent_group2_value": expected_value,
                "independent_root_minimum": root_minimum,
                "valid": valid,
            }
        )

    values = {row["leaf_cost"]: row["independent_root_minimum"] for row in replay}
    breakpoint_holds = values == {7: 33, 8: 34}
    mapping_valid = (
        source["isomorphism_mapping"]["queries"] == EXPECTED_QUERY_MAP
        and source["isomorphism_mapping"]["completions"] == list(range(10))
        and source["isomorphism_certificate"]["mapping_edge_checked"] is True
    )
    inference_consistent = (
        (source["first_integer_breakpoint"] == 8) == breakpoint_holds
        and (source["constant_integer_chamber"] is not None) == breakpoint_holds
    )
    count_valid = (
        source["cumulative_opened_reserved_cases"] == 16
        and source["remaining_reserved_cases"] == 2
    )
    passed = (
        all(row["valid"] for row in replay)
        and breakpoint_holds
        and mapping_valid
        and inference_consistent
        and count_valid
    )
    report = {
        "schema": "theorica.ternary-p2-symbol-orbit-breakpoint-audit/1",
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
