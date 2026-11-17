#!/usr/bin/env python3
"""Zero-production-import audit of the P2 root-action transition artifact."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_p2_root_action_transition/results.json")
OUT = Path("results/qary_ternary_p2_root_action_transition/audit.json")


def main():
    source = json.loads(SOURCE.read_text())
    replay = []
    for row in source["endpoints"]:
        c = row["leaf_cost"]
        exact = row["exact"]
        group0 = row["root_group0_action"]
        group3 = row["clean_group3_action"]
        expected_group0_children = [15 + c, 15 + c, 33]
        expected_group3_children = [15 + c, 22, 22]
        expected_group0_value = 37
        expected_group3_value = 26 + c
        root_minimum = min(action["action_value"] for action in exact["root_actions"])
        optimal_groups = sorted(
            action["query_group"]
            for action in exact["root_actions"]
            if action["action_value"] == root_minimum
        )
        expected_optimal = [0, 3] if c == 11 else [0]
        clean_present = any(
            separator["query_group"] == 3 for separator in row["clean_separators"]
        )
        valid = (
            row["level_costs"] == [4, 11, c]
            and group0["child_values"] == expected_group0_children
            and group3["child_values"] == expected_group3_children
            and group0["action_value"] == expected_group0_value
            and group3["action_value"] == expected_group3_value
            and clean_present
            and optimal_groups == expected_optimal
            and row["observed_optimal_groups"] == expected_optimal
            and exact["exact_lower_bound"]
            == exact["constructive_upper_bound"]
            == root_minimum
            == 37
        )
        replay.append(
            {
                "leaf_cost": c,
                "independent_group0_value": expected_group0_value,
                "independent_group3_value": expected_group3_value,
                "independent_optimal_groups": optimal_groups,
                "clean_group3_present": clean_present,
                "valid": valid,
            }
        )
    transition_valid = (
        replay[0]["leaf_cost"] == 11
        and replay[0]["independent_optimal_groups"] == [0, 3]
        and replay[1]["leaf_cost"] == 12
        and replay[1]["independent_optimal_groups"] == [0]
        and source["transition"]
        == {
            "collision_leaf_cost": 11,
            "strict_handoff_leaf_cost": 12,
            "from_query_group": 3,
            "to_query_group": 0,
        }
    )
    count_valid = (
        source["cumulative_opened_reserved_cases"] == 10
        and source["remaining_reserved_cases"] == 8
    )
    passed = all(row["valid"] for row in replay) and transition_valid and count_valid
    report = {
        "schema": "theorica.ternary-p2-root-action-transition-audit/1",
        "production_imports": 0,
        "endpoint_replay": replay,
        "tie_to_handoff_replayed": transition_valid,
        "reserved_count_valid": count_valid,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
