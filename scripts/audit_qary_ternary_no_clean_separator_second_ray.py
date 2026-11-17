#!/usr/bin/env python3
"""Zero-production-import audit of the second-ray no-clean artifact."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_no_clean_separator_second_ray/results.json")
OUT = Path("results/qary_ternary_no_clean_separator_second_ray/audit.json")


def main():
    source = json.loads(SOURCE.read_text())
    partitions = source["middle_partitions"]
    recomputed = []
    for partition in partitions:
        zero_cells = [cell for cell in partition["cells"] if cell["zero_lie"]]
        zero_ids = {index for cell in zero_cells for index in cell["zero_lie"]}
        clean = (
            zero_ids == {8, 9}
            and len(zero_cells) == 2
            and all(len(cell["zero_lie"]) == 1 for cell in zero_cells)
            and all(not cell["one_lie"] for cell in zero_cells)
        )
        recomputed.append(
            {
                "query_group": partition["query_group"],
                "clean_separator": clean,
                "matches_primary": clean == partition["clean_separator"],
            }
        )
    prospective = source["prospective"]
    a, b, _ = prospective["level_costs"]
    formula = a + 3 * b
    root_minimum = min(row["action_value"] for row in prospective["root_actions"])
    no_clean = bool(recomputed) and not any(row["clean_separator"] for row in recomputed)
    classifications_match = all(row["matches_primary"] for row in recomputed)
    bounds_match = (
        prospective["predicted_value"]
        == prospective["exact_lower_bound"]
        == prospective["constructive_upper_bound"]
        == root_minimum
        == formula
    )
    gap_matches = (
        prospective["exact_lower_bound"] - source["prior_P2_exact_value"]
        == source["exact_P0_minus_P2_gap"]
        == a
    )
    count_valid = (
        source["cumulative_opened_reserved_cases"] == 4
        and source["remaining_reserved_cases"] == 14
    )
    passed = no_clean and classifications_match and bounds_match and gap_matches and count_valid
    report = {
        "schema": "theorica.ternary-no-clean-separator-second-ray-audit/1",
        "partition_replay": recomputed,
        "no_clean_separator": no_clean,
        "partition_classifications_match": classifications_match,
        "independent_formula_value": formula,
        "independent_root_minimum": root_minimum,
        "exact_bounds_match": bounds_match,
        "exact_gap_matches_root_cost": gap_matches,
        "reserved_count_valid": count_valid,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
