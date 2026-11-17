#!/usr/bin/env python3
"""Prospective exact test of the explicit-sentinel first breakpoint."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "sentinel", Path("scripts/verify_qary_ternary_explicit_outside_sentinel.py")
)
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)

OUT = Path("results/qary_ternary_explicit_sentinel_first_breakpoint/results.json")
PREDICTIONS = {
    22: {"value": 37, "optimal_groups": [0], "children": [33, 33, 33]},
    23: {"value": 38, "optimal_groups": [0], "children": [34, 34, 33]},
}


def main():
    source = (*V.H.BASE, *V.H.PAIRS[0])
    V.H.rows = V.sentinel_rows
    V.S.H.rows = V.sentinel_rows
    endpoints = [V.endpoint(source, c) for c in sorted(PREDICTIONS)]
    checks = {
        str(row["leaf_cost"]): {
            "value": row["exact_value"] == PREDICTIONS[row["leaf_cost"]]["value"],
            "optimal_groups": row["optimal_groups"]
            == PREDICTIONS[row["leaf_cost"]]["optimal_groups"],
            "children": row["group0_children"]
            == PREDICTIONS[row["leaf_cost"]]["children"],
            "bounds_equal": row["exact"]["exact_lower_bound"]
            == row["exact"]["constructive_upper_bound"],
        }
        for row in endpoints
    }
    predictions_passed = all(all(values.values()) for values in checks.values())
    report = {
        "schema": "theorica.ternary-explicit-sentinel-first-breakpoint/1",
        "fixed_root_middle_costs": [4, 11],
        "candidate_root_children": "[c+11,c+11,33]",
        "candidate_root_action": "max(37,c+15)",
        "certified_anchor": {"leaf_cost": 1, "exact_value": 37},
        "endpoints": endpoints,
        "checks": checks,
        "summary": {
            "predictions_passed": predictions_passed,
            "constant_integer_chamber": "1<=c<=22" if predictions_passed else None,
            "first_positive_integer_breakpoint": 23 if predictions_passed else None,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if predictions_passed else 1)


if __name__ == "__main__":
    main()
