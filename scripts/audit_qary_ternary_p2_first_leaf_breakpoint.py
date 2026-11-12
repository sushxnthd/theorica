#!/usr/bin/env python3
"""Zero-production-import audit of the P2 first-breakpoint artifact."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_p2_first_leaf_breakpoint/results.json")
OUT = Path("results/qary_ternary_p2_first_leaf_breakpoint/audit.json")


def main():
    source = json.loads(SOURCE.read_text())
    replay = []
    for row in source["endpoints"]:
        c = row["leaf_cost"]
        exact = row["exact"]
        clean_action = row["clean_group3_action"]
        expected_value = max(33, 26 + c)
        expected_children = [15 + c, 22, 22]
        root_minimum = min(action["action_value"] for action in exact["root_actions"])
        clean_present = any(
            separator["query_group"] == 3 for separator in row["clean_separators"]
        )
        valid = (
            row["level_costs"] == [4, 11, c]
            and row["predicted_value"] == expected_value
            and row["predicted_clean_children"] == expected_children
            and clean_present
            and clean_action["query_group"] == 3
            and clean_action["optimal"]
            and clean_action["child_values"] == expected_children
            and clean_action["action_value"] == expected_value
            and exact["exact_lower_bound"]
            == exact["constructive_upper_bound"]
            == root_minimum
            == expected_value
        )
        replay.append(
            {
                "leaf_cost": c,
                "independent_branch_value": expected_value,
                "independent_child_values": expected_children,
                "clean_group3_present": clean_present,
                "valid": valid,
            }
        )
    values = {row["leaf_cost"]: row["independent_branch_value"] for row in replay}
    monotone_first_break = (
        source["prior_exact_endpoints"] == {"c1": 33, "c2": 33}
        and values == {7: 33, 8: 34}
        and source["constant_integer_chamber"]
        == {"minimum_c": 1, "maximum_c": 7, "value": 33}
        and source["first_integer_breakpoint"] == 8
    )
    count_valid = (
        source["cumulative_opened_reserved_cases"] == 8
        and source["remaining_reserved_cases"] == 10
    )
    passed = all(row["valid"] for row in replay) and monotone_first_break and count_valid
    report = {
        "schema": "theorica.ternary-p2-first-leaf-breakpoint-audit/1",
        "production_imports": 0,
        "endpoint_replay": replay,
        "critical_child_crossing_replayed": values == {7: 33, 8: 34},
        "monotonic_first_integer_breakpoint_valid": monotone_first_break,
        "reserved_count_valid": count_valid,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
