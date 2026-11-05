import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_p2_first_integer_leaf_breakpoint():
    result = json.loads(
        (ROOT / "results/qary_ternary_p2_first_leaf_breakpoint/results.json").read_text()
    )
    audit = json.loads(
        (ROOT / "results/qary_ternary_p2_first_leaf_breakpoint/audit.json").read_text()
    )

    endpoints = {row["leaf_cost"]: row for row in result["endpoints"]}
    assert endpoints[7]["exact"]["exact_lower_bound"] == 33
    assert endpoints[7]["clean_group3_action"]["child_values"] == [22, 22, 22]
    assert endpoints[8]["exact"]["exact_lower_bound"] == 34
    assert endpoints[8]["clean_group3_action"]["child_values"] == [23, 22, 22]
    assert result["first_integer_breakpoint"] == 8
    assert result["constant_integer_chamber"] == {
        "minimum_c": 1,
        "maximum_c": 7,
        "value": 33,
    }
    assert result["remaining_reserved_cases"] == 10
    assert result["summary"]["prediction_supported"] is True
    assert audit["passed"] is True
