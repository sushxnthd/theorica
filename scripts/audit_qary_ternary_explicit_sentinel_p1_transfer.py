#!/usr/bin/env python3
"""Zero-production-import audit of the explicit-sentinel P1 transfer."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_explicit_sentinel_p1_transfer/results.json")
OUT = Path("results/qary_ternary_explicit_sentinel_p1_transfer/audit.json")


def root_check(row, expected_value, expected_children, root):
    actions = {int(group): action for group, action in row["root_actions"].items()}
    minimum = min(action["action_value"] for action in actions.values())
    optima = sorted(
        group for group, action in actions.items() if action["action_value"] == minimum
    )
    return {
        "minimum_reconstructed": minimum == expected_value,
        "bounds_equal_minimum": row["exact"]["exact_lower_bound"]
        == row["exact"]["constructive_upper_bound"]
        == minimum,
        "unique_expected_root": optima == [root],
        "child_multiset": sorted(actions[root]["child_values"])
        == sorted(expected_children),
    }


def main():
    raw = SOURCE.read_bytes()
    result = json.loads(raw)
    qmap = result["p1_target_isomorphism"]["queries"]
    checks = {}
    for source, target in zip(result["source_endpoints"], result["target_endpoints"]):
        c = source["leaf_cost"]
        expected_value = 37 if c == 22 else 38
        expected_children = [33, 33, 33] if c == 22 else [34, 34, 33]
        source_check = root_check(source, expected_value, expected_children, 0)
        target_check = root_check(target, expected_value, expected_children, qmap[0])
        checks[str(c)] = {
            "source": source_check,
            "target": target_check,
            "transport_value": source["exact_value"] == target["exact_value"],
            "search_counts_equal": all(
                source["exact"][key] == target["exact"][key]
                for key in (
                    "states_solved",
                    "actions_evaluated",
                    "compatibility_states",
                )
            ),
        }

    p0_p1 = result["p0_p1_isomorphism"]
    structural = (
        result["p0_p1_certificate"]["mapping_edge_checked"]
        and p0_p1["queries"][0] == 0
        and p0_p1["queries"][11] == 12
        and p0_p1["queries"][12] == 11
        and result["p1_target_certificate"]["mapping_edge_checked"]
    )
    endpoint_pass = all(
        all(row[side].values())
        and row["transport_value"]
        and row["search_counts_equal"]
        for row in checks.values()
        for side in ("source", "target")
    )
    passed = structural and endpoint_pass
    report = {
        "schema": "theorica.ternary-explicit-sentinel-p1-transfer-audit/1",
        "production_imports": 0,
        "results_sha256": hashlib.sha256(raw).hexdigest(),
        "structural_isomorphisms_edge_checked": structural,
        "root_checks": checks,
        "p1_integer_chamber_transfers_from_p0": passed,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
