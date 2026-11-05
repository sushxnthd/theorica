import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_positive_leaf_cost_chamber_certificate():
    result = json.loads(
        (
            ROOT / "results/qary_ternary_positive_leaf_cost_chamber/results.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT / "results/qary_ternary_positive_leaf_cost_chamber/audit.json"
        ).read_text()
    )

    families = {row["family"]: row for row in result["families"]}
    assert families["P2"]["formula_value"] == 33
    assert families["P0"]["formula_value"] == 37
    assert not any(row["sandwich"]["closed"] for row in families.values())
    assert not any(row["leaf_free_policy_exists"] for row in families.values())
    assert all(
        row["falsification"]["constant_unbounded_leaf_cost_chamber_impossible"]
        for row in families.values()
    )
    assert families["P2"]["falsification"][
        "constant_formula_must_fail_for_c_greater_than"
    ] == 33
    assert families["P0"]["falsification"][
        "constant_formula_must_fail_for_c_greater_than"
    ] == 37
    assert result["exact_P0_minus_P2_gap_for_all_c_ge_1"] == 4
    assert result["leaf_cost_domain"] == {"minimum": 1, "unbounded_above": True}
    assert result["remaining_reserved_cases"] == 12
    assert result["summary"]["prediction_supported"] is False
    assert result["summary"]["leaf_query_necessity_falsification"] is True
    assert audit["prediction_supported"] is False
    assert audit["leaf_query_necessity_falsifies_unbounded_constant_chamber"] is True
    assert audit["passed"] is True
