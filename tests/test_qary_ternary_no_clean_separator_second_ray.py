import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_no_clean_separator_second_ray_holdout():
    result = json.loads(
        (
            ROOT
            / "results/qary_ternary_no_clean_separator_second_ray/results.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT / "results/qary_ternary_no_clean_separator_second_ray/audit.json"
        ).read_text()
    )

    assert result["clean_separator_present"] is False
    assert len(result["middle_partitions"]) == 3
    assert not any(row["clean_separator"] for row in result["middle_partitions"])
    assert result["prospective"]["predicted_value"] == 37
    assert result["prospective"]["exact_lower_bound"] == 37
    assert result["prospective"]["constructive_upper_bound"] == 37
    assert result["prior_P2_exact_value"] == 33
    assert result["exact_P0_minus_P2_gap"] == 4
    assert result["remaining_reserved_cases"] == 14
    assert result["summary"]["prediction_supported"] is True
    assert audit["passed"] is True
