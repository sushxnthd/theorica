import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_p1_breakpoint_transfer():
    result = json.loads(
        (ROOT / "results/qary_ternary_p1_breakpoint_transfer/results.json").read_text()
    )
    audit = json.loads(
        (ROOT / "results/qary_ternary_p1_breakpoint_transfer/audit.json").read_text()
    )

    endpoints = {row["leaf_cost"]: row for row in result["endpoints"]}
    assert endpoints[18]["exact"]["exact_lower_bound"] == 37
    assert endpoints[18]["observed_optimal_groups"] == [0]
    assert endpoints[18]["root_group0_action"]["child_values"] == [33, 33, 33]
    assert endpoints[19]["exact"]["exact_lower_bound"] == 38
    assert endpoints[19]["observed_optimal_groups"] == [0]
    assert endpoints[19]["root_group0_action"]["child_values"] == [34, 34, 33]
    assert result["first_integer_breakpoint"] == 19
    assert result["constant_integer_chamber"] == {
        "minimum_c": 1,
        "maximum_c": 18,
        "value": 37,
    }
    assert result["remaining_reserved_cases"] == 4
    assert result["summary"]["prediction_supported"] is True
    assert audit["production_imports"] == 0
    assert audit["passed"] is True
