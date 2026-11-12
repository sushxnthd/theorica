#!/usr/bin/env python3
"""Zero-production-import audit for explicit outside-sentinel covariance."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_explicit_outside_sentinel/results.json")
OUT = Path("results/qary_ternary_explicit_outside_sentinel/audit.json")


def replay(row):
    exact = row["exact"]
    minimum = min(action["action_value"] for action in exact["root_actions"])
    group0 = next(action for action in exact["root_actions"] if action["query_group"] == 0)
    optimal = sorted(
        action["query_group"]
        for action in exact["root_actions"]
        if action["action_value"] == minimum
    )
    return {
        "leaf_cost": row["leaf_cost"],
        "minimum": minimum,
        "optimal_groups": optimal,
        "group0_children": group0["child_values"],
        "bounds_equal": exact["exact_lower_bound"]
        == exact["constructive_upper_bound"]
        == minimum,
    }


def main():
    data = json.loads(SOURCE.read_text())
    source = [replay(row) for row in data["source_endpoints"]]
    target = [replay(row) for row in data["target_endpoints"]]
    structural = (
        data["outside_response"] == -1
        and data["isomorphism"] is not None
        and data["isomorphism_certificate"].get("mapping_edge_checked") is True
    )
    paired = source == target
    counts = all(
        s["exact"]["states_solved"] == t["exact"]["states_solved"]
        and s["exact"]["actions_evaluated"] == t["exact"]["actions_evaluated"]
        and s["exact"]["compatibility_states"] == t["exact"]["compatibility_states"]
        for s, t in zip(data["source_endpoints"], data["target_endpoints"])
    )
    passed = structural and paired and counts and all(x["bounds_equal"] for x in source + target)
    report = {
        "schema": "theorica.ternary-explicit-outside-sentinel-audit/1",
        "production_imports": 0,
        "structural_map_valid": structural,
        "endpoint_replays_equal": paired,
        "search_counts_equal": counts,
        "source_replay": source,
        "target_replay": target,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
