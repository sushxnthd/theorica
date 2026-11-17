#!/usr/bin/env python3
"""Zero-production-import audit of the P1 breakpoint-transfer artifact."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_p1_breakpoint_transfer/results.json")
OUT = Path("results/qary_ternary_p1_breakpoint_transfer/audit.json")


def main():
    source = json.loads(SOURCE.read_text())
    replay = []
    for row in source["endpoints"]:
        c = row["leaf_cost"]
        exact = row["exact"]
        group0 = row["root_group0_action"]
        expected_children = [15 + c, 15 + c, 33]
        expected_action_value = max(37, 19 + c)
        root_minimum = min(action["action_value"] for action in exact["root_actions"])
        valid = (
            row["level_costs"] == [4, 11, c]
            and group0["child_values"] == expected_children
            and group0["action_value"] == expected_action_value
            and exact["exact_lower_bound"]
            == exact["constructive_upper_bound"]
            == root_minimum
        )
        replay.append(
            {
                "leaf_cost": c,
                "independent_group0_children": expected_children,
                "independent_group0_value": expected_action_value,
                "independent_root_minimum": root_minimum,
                "valid": valid,
            }
        )
    values = {row["leaf_cost"]: row["independent_root_minimum"] for row in replay}
    breakpoint_holds = values == {18: 37, 19: 38}
    inference_consistent = (
        (source["first_integer_breakpoint"] == 19) == breakpoint_holds
        and (source["constant_integer_chamber"] is not None) == breakpoint_holds
    )
    identity_mapping_valid = source["prior_isomorphism_mapping"] == {
        "query_groups": list(range(13)),
        "completions": list(range(10)),
        "mapping_edge_checked": True,
    }
    count_valid = (
        source["cumulative_opened_reserved_cases"] == 14
        and source["remaining_reserved_cases"] == 4
    )
    passed = (
        all(row["valid"] for row in replay)
        and inference_consistent
        and identity_mapping_valid
        and count_valid
    )
    report = {
        "schema": "theorica.ternary-p1-breakpoint-transfer-audit/1",
        "production_imports": 0,
        "endpoint_replay": replay,
        "predicted_breakpoint_holds": breakpoint_holds,
        "inference_consistent": inference_consistent,
        "identity_mapping_valid": identity_mapping_valid,
        "reserved_count_valid": count_valid,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
