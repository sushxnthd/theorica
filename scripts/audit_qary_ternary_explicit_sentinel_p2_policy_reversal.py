#!/usr/bin/env python3
"""Zero-production-import audit of the explicit-sentinel P2 collision."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_explicit_sentinel_p2_policy_reversal/results.json")
OUT = Path("results/qary_ternary_explicit_sentinel_p2_policy_reversal/audit.json")


def replay(row):
    exact = row["exact"]
    minimum = min(action["action_value"] for action in exact["root_actions"])
    optimal = sorted(
        action["query_group"]
        for action in exact["root_actions"]
        if action["action_value"] == minimum
    )
    actions = {action["query_group"]: action for action in exact["root_actions"]}
    return {
        "leaf_cost": row["leaf_cost"],
        "minimum": minimum,
        "optimal_groups": optimal,
        "group0_children": actions[0]["child_values"],
        "group3_children": actions[3]["child_values"],
        "group11_children": actions[11]["child_values"],
        "bounds_equal": exact["exact_lower_bound"] == exact["constructive_upper_bound"] == minimum,
    }


def main():
    data = json.loads(SOURCE.read_text())
    source = [replay(row) for row in data["source_endpoints"]]
    target = [replay(row) for row in data["target_endpoints"]]
    diagnostics = [replay(row) for row in data["post_falsification_diagnostic_endpoints"]]

    collision_valid = (
        source[0]["leaf_cost"] == 11
        and source[0]["minimum"] == 37
        and source[0]["optimal_groups"] == [0, 3, 11, 12]
        and source[0]["group0_children"] == [22, 22, 33]
        and source[0]["group3_children"] == [26, 22, 22]
        and source[0]["group11_children"] == [26, 22]
        and source[0]["bounds_equal"]
    )
    reversal_falsified = (
        source[1]["leaf_cost"] == 12
        and source[1]["minimum"] == 37
        and source[1]["optimal_groups"] == [0]
        and source[1]["group0_children"] == [23, 23, 33]
        and source[1]["group3_children"] == [27, 22, 22]
        and source[1]["group11_children"] == [27, 22]
        and source[1]["bounds_equal"]
    )
    query_map = data["isomorphism"]["queries"]
    transport_valid = all(
        left["minimum"] == right["minimum"]
        and sorted(query_map[group] for group in left["optimal_groups"])
        == right["optimal_groups"]
        and left["bounds_equal"]
        and right["bounds_equal"]
        for left, right in zip(source, target)
    )
    search_counts_equal = all(
        left["exact"][key] == right["exact"][key]
        for left, right in zip(data["source_endpoints"], data["target_endpoints"])
        for key in ("states_solved", "actions_evaluated", "compatibility_states")
    )
    diagnostics_valid = (
        [(row["leaf_cost"], row["minimum"], row["optimal_groups"]) for row in diagnostics]
        == [(9, 31, [0, 11, 12]), (10, 34, [0, 11, 12])]
        and all(row["bounds_equal"] for row in diagnostics)
    )
    passed = collision_valid and reversal_falsified and transport_valid and search_counts_equal and diagnostics_valid
    report = {
        "schema": "theorica.ternary-explicit-sentinel-p2-policy-reversal-audit/1",
        "production_imports": 0,
        "source_replay": source,
        "target_replay": target,
        "diagnostic_replay": diagnostics,
        "collision_at_c11_valid": collision_valid,
        "reversal_at_c12_falsified": reversal_falsified,
        "unseen_family_transport_valid": transport_valid,
        "search_counts_equal": search_counts_equal,
        "diagnostic_law_c9_c10_valid": diagnostics_valid,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
