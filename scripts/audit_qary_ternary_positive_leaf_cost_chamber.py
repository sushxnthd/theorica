#!/usr/bin/env python3
"""Zero-production-import audit of the positive-leaf-cost chamber proof."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_positive_leaf_cost_chamber/results.json")
OUT = Path("results/qary_ternary_positive_leaf_cost_chamber/audit.json")


def main():
    source = json.loads(SOURCE.read_text())
    a, b = source["fixed_root_middle_costs"]
    expected = {"P2": 3 * b, "P0": a + 3 * b}
    replay = []
    for family in source["families"]:
        name = family["family"]
        endpoint = family["endpoint_c1"]
        restricted = family["root_middle_only_upper_bound"]
        partitions = family["middle_partitions"]
        clean = any(row["clean_separator"] for row in partitions)
        formula = expected[name]
        endpoint_formula_holds = (
            endpoint["allowed_query_levels"] == [0, 1, 2]
            and endpoint["exact_lower_bound"]
            == endpoint["constructive_upper_bound"]
            == family["formula_value"]
            == formula
        )
        closed = (
            endpoint_formula_holds
            and restricted["allowed_query_levels"] == [0, 1]
            and restricted["exact_lower_bound"]
            == restricted["constructive_upper_bound"]
            == formula
            and family["sandwich"]["upper_bound_for_all_c_ge_1"] == formula
        )
        leaf_free_infeasible = (
            restricted["allowed_query_levels"] == [0, 1]
            and restricted["exact_lower_bound"] >= 10**9
            and restricted["constructive_upper_bound"] >= 10**9
            and not family["leaf_free_policy_exists"]
            and family["sandwich"]["upper_bound_for_all_c_ge_1"] is None
        )
        threshold_valid = (
            family["falsification"]["necessary_leaf_lower_bound"] == "V(c) >= c"
            and family["falsification"][
                "constant_formula_must_fail_for_c_greater_than"
            ]
            == formula
        )
        replay.append(
            {
                "family": name,
                "independent_formula": formula,
                "clean_separator": clean,
                "endpoint_formula_holds": endpoint_formula_holds,
                "sandwich_closed": closed,
                "leaf_free_policy_infeasible": leaf_free_infeasible,
                "leaf_query_necessary": leaf_free_infeasible,
                "counterexample_threshold_valid": threshold_valid,
            }
        )
    structural = replay[0]["clean_separator"] and not replay[1]["clean_separator"]
    gap = expected["P0"] - expected["P2"]
    count_valid = (
        source["cumulative_opened_reserved_cases"] == 6
        and source["remaining_reserved_cases"] == 12
    )
    positive_proof = all(row["sandwich_closed"] for row in replay)
    falsification = (
        all(row["endpoint_formula_holds"] for row in replay)
        and all(row["leaf_free_policy_infeasible"] for row in replay)
        and all(row["counterexample_threshold_valid"] for row in replay)
    )
    passed = (
        (positive_proof or falsification)
        and structural
        and gap == source["exact_P0_minus_P2_gap_for_all_c_ge_1"] == a
        and source["leaf_cost_domain"]
        == {"minimum": 1, "unbounded_above": True}
        and count_valid
    )
    report = {
        "schema": "theorica.ternary-positive-leaf-cost-chamber-audit/1",
        "production_imports": 0,
        "family_replay": replay,
        "structural_branch_replayed": structural,
        "independent_gap": gap,
        "gap_matches_root_cost": gap == a,
        "monotonicity_sandwich_valid_for_all_real_c_ge_1": positive_proof,
        "leaf_query_necessity_falsifies_unbounded_constant_chamber": falsification,
        "prediction_supported": positive_proof,
        "reserved_count_valid": count_valid,
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
