#!/usr/bin/env python3
"""Zero-production-import audit of the zero-moving symbol boundary."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_zero_moving_symbol_boundary/results.json")
OUT = Path("results/qary_ternary_zero_moving_symbol_boundary/audit.json")
EXPECTED = {
    18: (37, [0], [33, 33, 33]),
    19: (38, [0], [34, 34, 33]),
}


def replay_endpoint(row):
    exact = row["exact"]
    root_minimum = min(action["action_value"] for action in exact["root_actions"])
    group0 = next(action for action in exact["root_actions"] if action["query_group"] == 0)
    expected = EXPECTED[row["leaf_cost"]]
    return {
        "leaf_cost": row["leaf_cost"],
        "root_minimum": root_minimum,
        "optimal_groups": sorted(
            action["query_group"]
            for action in exact["root_actions"]
            if action["action_value"] == root_minimum
        ),
        "group0_children": group0["child_values"],
        "valid": (
            exact["exact_lower_bound"] == exact["constructive_upper_bound"] == root_minimum
            and (root_minimum, row["optimal_groups"], group0["child_values"])
            == expected
        ),
    }


def main():
    source = json.loads(SOURCE.read_text())
    source_replay = [replay_endpoint(row) for row in source["source_endpoints"]]
    target_replay = [replay_endpoint(row) for row in source["target_endpoints"]]
    left_sizes = source["nonisomorphism_certificate"]["left_color_sizes"]
    right_sizes = source["nonisomorphism_certificate"]["right_color_sizes"]
    separation_valid = (
        source["level_preserving_isomorphism"] is None
        and source["nonisomorphism_certificate"]["WL_multiplicity_separation"] is True
        and left_sizes != right_sizes
        and left_sizes.count(5) == 2
        and right_sizes.count(3) == 2
    )
    ratios_valid = all(
        row["target_states"] > row["source_states"]
        and row["target_actions"] > row["source_actions"]
        for row in source["state_expansion"].values()
    )
    passed = (
        all(row["valid"] for row in source_replay + target_replay)
        and separation_valid
        and ratios_valid
        and source["completed_panel_reopened"] is False
    )
    report = {
        "schema": "theorica.ternary-zero-moving-symbol-boundary-audit/1",
        "production_imports": 0,
        "source_replay": source_replay,
        "target_replay": target_replay,
        "color_multiplicity_separation_valid": separation_valid,
        "search_expansion_valid": ratios_valid,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
