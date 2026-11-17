#!/usr/bin/env python3
"""Zero-production-import audit of the P2 second-breakpoint evidence."""
from __future__ import annotations

import json
from pathlib import Path

CURRENT = Path("results/qary_ternary_explicit_sentinel_p2_second_breakpoint/results.json")
LOW = Path("results/qary_ternary_explicit_sentinel_p2_invariance/results.json")
COLLISION = Path("results/qary_ternary_explicit_sentinel_p2_policy_reversal/results.json")
OUT = Path("results/qary_ternary_explicit_sentinel_p2_second_breakpoint/audit.json")


def endpoint_check(row, expected_value, expected_children):
    actions = {int(group): action for group, action in row["root_actions"].items()}
    minimum = min(action["action_value"] for action in actions.values())
    optima = sorted(group for group, action in actions.items() if action["action_value"] == minimum)
    return {
        "root_minimum": minimum,
        "exact_bounds_equal": row["exact"]["exact_lower_bound"]
        == row["exact"]["constructive_upper_bound"]
        == minimum,
        "expected_value": minimum == expected_value,
        "unique_root": optima == [0],
        "expected_root_children": actions[0]["child_values"] == expected_children,
    }


def main():
    current = json.loads(CURRENT.read_text())
    low = json.loads(LOW.read_text())
    collision = json.loads(COLLISION.read_text())
    checks = {}
    for source, target in zip(current["source_endpoints"], current["target_endpoints"]):
        c = source["leaf_cost"]
        expected_value = 37 if c == 22 else 38
        expected_children = [33, 33, 33] if c == 22 else [34, 34, 33]
        source_check = endpoint_check(source, expected_value, expected_children)
        target_check = endpoint_check(target, expected_value, target["root_actions"]["0"]["child_values"])
        checks[str(c)] = {
            "source": source_check,
            "target": target_check,
            "transport_value": source["exact_value"] == target["exact_value"],
            "transport_child_multiset": sorted(source["root_actions"]["0"]["child_values"])
            == sorted(target["root_actions"]["0"]["child_values"]),
            "search_counts_equal": all(
                source["exact"][key] == target["exact"][key]
                for key in ("states_solved", "actions_evaluated", "compatibility_states")
            ),
        }

    low_rows = low["post_falsification_exploratory_sweep"]
    diagnostic_rows = collision["post_falsification_diagnostic_endpoints"]
    c11 = collision["source_endpoints"][0]
    low_law = all(row["exact_value"] == 4 + 3 * row["leaf_cost"] for row in low_rows)
    diagnostics = all(
        row["exact_value"] == 4 + 3 * row["leaf_cost"] for row in diagnostic_rows
    )
    plateau_endpoints = c11["exact_value"] == current["source_endpoints"][0]["exact_value"] == 37
    # Query costs are nondecreasing in c, hence the minimax value is nondecreasing.
    # Equal exact endpoint values therefore force every integer between them to 37.
    monotonicity_closes_plateau = plateau_endpoints
    passed = (
        low_law
        and diagnostics
        and monotonicity_closes_plateau
        and current["source_endpoints"][1]["exact_value"] == 38
        and all(
            all(value for value in row["source"].values())
            and all(value for value in row["target"].values())
            and row["transport_value"]
            and row["transport_child_multiset"]
            and row["search_counts_equal"]
            for row in checks.values()
        )
    )
    report = {
        "schema": "theorica.ternary-explicit-sentinel-p2-second-breakpoint-audit/1",
        "production_imports": 0,
        "checks": checks,
        "low_law_c1_c8": low_law,
        "diagnostic_law_c9_c10": diagnostics,
        "plateau_endpoints_c11_c22": plateau_endpoints,
        "monotonicity_closes_all_integer_costs_c11_c22": monotonicity_closes_plateau,
        "first_post_collision_increase_c23": current["source_endpoints"][1]["exact_value"] == 38,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
