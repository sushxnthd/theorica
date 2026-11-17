#!/usr/bin/env python3
"""Zero-production-import audit of explicit-sentinel P2 invariance."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_explicit_sentinel_p2_invariance/results.json")
OUT = Path("results/qary_ternary_explicit_sentinel_p2_invariance/audit.json")
FROZEN = {
    7: {"value": 33, "source_group": 3, "target_group": 1, "children": [22, 22, 22]},
    8: {"value": 34, "source_group": 3, "target_group": 1, "children": [23, 22, 22]},
}
OBSERVED = {7: (25, [0, 11, 12]), 8: (28, [0, 11, 12])}


def replay(row, group):
    exact = row["exact"]
    minimum = min(action["action_value"] for action in exact["root_actions"])
    optimal = sorted(
        action["query_group"]
        for action in exact["root_actions"]
        if action["action_value"] == minimum
    )
    action = next(item for item in exact["root_actions"] if item["query_group"] == group)
    return {
        "leaf_cost": row["leaf_cost"],
        "minimum": minimum,
        "optimal_groups": optimal,
        "children": action["child_values"],
        "bounds_equal": exact["exact_lower_bound"] == exact["constructive_upper_bound"] == minimum,
    }


def main():
    data = json.loads(SOURCE.read_text())
    source = [
        replay(row, FROZEN[row["leaf_cost"]]["source_group"])
        for row in data["source_endpoints"]
    ]
    target = [
        replay(row, FROZEN[row["leaf_cost"]]["target_group"])
        for row in data["target_endpoints"]
    ]

    frozen_prediction_falsified = True
    for source_row, target_row in zip(source, target):
        c = source_row["leaf_cost"]
        expected_value, expected_source_groups = OBSERVED[c]
        frozen_prediction_falsified &= (
            source_row["minimum"] == target_row["minimum"] == expected_value
            and source_row["optimal_groups"] == expected_source_groups
            and target_row["optimal_groups"] == sorted(data["isomorphism"]["queries"][g] for g in expected_source_groups)
            and source_row["bounds_equal"]
            and target_row["bounds_equal"]
        )

    query_map = data["isomorphism"]["queries"] if data["isomorphism"] else []
    transport_valid = (
        len(query_map) == 13
        and query_map[3] == 1
        and query_map[11] == 5
        and query_map[12] == 4
    )
    search_counts_equal = all(
        left["exact"][key] == right["exact"][key]
        for left, right in zip(data["source_endpoints"], data["target_endpoints"])
        for key in ("states_solved", "actions_evaluated", "compatibility_states")
    )
    sweep = data["post_falsification_exploratory_sweep"]
    exploratory_law_replayed = [row["exact_value"] for row in sweep] == [
        4 + 3 * c for c in range(1, 9)
    ]
    passed = (
        frozen_prediction_falsified
        and transport_valid
        and search_counts_equal
        and exploratory_law_replayed
    )
    report = {
        "schema": "theorica.ternary-explicit-sentinel-p2-invariance-audit/1",
        "production_imports": 0,
        "source_replay": source,
        "target_replay": target,
        "frozen_prediction_falsified": frozen_prediction_falsified,
        "query_group_3_maps_to_1": transport_valid,
        "search_counts_equal": search_counts_equal,
        "exploratory_law_c1_c8_replayed": exploratory_law_replayed,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
