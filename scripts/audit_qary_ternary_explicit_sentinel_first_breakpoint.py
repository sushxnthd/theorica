#!/usr/bin/env python3
"""Zero-production-import audit of the explicit-sentinel breakpoint."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_explicit_sentinel_first_breakpoint/results.json")
OUT = Path("results/qary_ternary_explicit_sentinel_first_breakpoint/audit.json")
EXPECTED = {
    22: (37, [0], [33, 33, 33]),
    23: (38, [0], [34, 34, 33]),
}


def replay(row):
    exact = row["exact"]
    minimum = min(action["action_value"] for action in exact["root_actions"])
    optimal = sorted(
        action["query_group"]
        for action in exact["root_actions"]
        if action["action_value"] == minimum
    )
    group0 = next(action for action in exact["root_actions"] if action["query_group"] == 0)
    expected = EXPECTED[row["leaf_cost"]]
    return {
        "leaf_cost": row["leaf_cost"],
        "minimum": minimum,
        "optimal_groups": optimal,
        "group0_children": group0["child_values"],
        "valid": (
            exact["exact_lower_bound"]
            == exact["constructive_upper_bound"]
            == minimum
            and (minimum, optimal, group0["child_values"]) == expected
        ),
    }


def main():
    data = json.loads(SOURCE.read_text())
    replayed = [replay(row) for row in data["endpoints"]]
    monotonicity_valid = (
        data["certified_anchor"] == {"leaf_cost": 1, "exact_value": 37}
        and replayed[0]["leaf_cost"] == 22
        and replayed[0]["minimum"] == 37
        and replayed[1]["leaf_cost"] == 23
        and replayed[1]["minimum"] == 38
    )
    passed = all(row["valid"] for row in replayed) and monotonicity_valid
    report = {
        "schema": "theorica.ternary-explicit-sentinel-first-breakpoint-audit/1",
        "production_imports": 0,
        "replayed_endpoints": replayed,
        "monotonicity_argument_valid": monotonicity_valid,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
