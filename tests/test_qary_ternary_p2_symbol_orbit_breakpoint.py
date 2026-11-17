import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_p2_symbol_orbit_breakpoint_transfer():
    result = json.loads(
        (ROOT / "results/qary_ternary_p2_symbol_orbit_breakpoint/results.json").read_text()
    )
    audit = json.loads(
        (ROOT / "results/qary_ternary_p2_symbol_orbit_breakpoint/audit.json").read_text()
    )

    endpoints = {row["leaf_cost"]: row for row in result["endpoints"]}
    assert endpoints[7]["exact"]["exact_lower_bound"] == 33
    assert endpoints[7]["observed_optimal_groups"] == [2]
    assert endpoints[7]["root_group2_action"]["child_values"] == [22, 22, 22]
    assert endpoints[8]["exact"]["exact_lower_bound"] == 34
    assert endpoints[8]["observed_optimal_groups"] == [2]
    assert endpoints[8]["root_group2_action"]["child_values"] == [23, 22, 22]
    assert result["first_integer_breakpoint"] == 8
    assert result["constant_integer_chamber"] == {
        "minimum_c": 1,
        "maximum_c": 7,
        "value": 33,
    }
    assert result["remaining_reserved_cases"] == 2
    assert result["summary"]["mapping_supported"] is True
    assert result["summary"]["prediction_supported"] is True
    assert audit["production_imports"] == 0
    assert audit["passed"] is True
