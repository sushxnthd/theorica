#!/usr/bin/env python3
"""Zero-production-import audit of the second-ray clean-separator result."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_clean_separator_second_ray/results.json")
OUT = Path("results/qary_ternary_clean_separator_second_ray/audit.json")


def main():
    source = json.loads(SOURCE.read_text())
    separators = source["clean_separators"]
    clean_group_3 = any(
        row["query_group"] == 3
        and len([cell for cell in row["cells"] if cell["zero_lie"]]) == 2
        and all(
            len(cell["zero_lie"]) == 1 and not cell["one_lie"]
            for cell in row["cells"]
            if cell["zero_lie"]
        )
        for row in separators
    )
    prospective = source["prospective"]
    root_minimum = min(row["action_value"] for row in prospective["root_actions"])
    group_3_optimal = any(
        row["query_group"] == 3
        and row["optimal"]
        and row["action_value"] == root_minimum
        for row in prospective["root_actions"]
    )
    formula = 3 * prospective["level_costs"][1]
    bounds_match = (
        prospective["predicted_value"]
        == prospective["exact_lower_bound"]
        == prospective["constructive_upper_bound"]
        == root_minimum
        == formula
    )
    count_valid = (
        source["cumulative_opened_reserved_cases"] == 3
        and source["remaining_reserved_cases"] == 15
    )
    passed = clean_group_3 and group_3_optimal and bounds_match and count_valid
    report = {
        "schema": "theorica.ternary-clean-separator-second-ray-audit/1",
        "clean_group_3_reconstructed": clean_group_3,
        "group_3_optimal": group_3_optimal,
        "independent_root_minimum": root_minimum,
        "independent_formula_value": formula,
        "exact_bounds_match": bounds_match,
        "reserved_count_valid": count_valid,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
