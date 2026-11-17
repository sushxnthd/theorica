import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_clean_separator_prospective_exact_result():
    result = json.loads(
        (ROOT / "results/qary_ternary_clean_separator/results.json").read_text()
    )
    audit = json.loads(
        (ROOT / "results/qary_ternary_clean_separator/audit.json").read_text()
    )

    assert result["clean_separator"]["present"] is True
    assert result["prospective"]["level_costs"] == [3, 10, 3]
    assert result["prospective"]["predicted_value"] == 30
    assert result["prospective"]["exact_lower_bound"] == 30
    assert result["prospective"]["constructive_upper_bound"] == 30
    assert result["opened_reserved_cases"] == 1
    assert result["remaining_reserved_cases"] == 17
    assert result["summary"]["prediction_supported"] is True
    assert audit["passed"] is True
