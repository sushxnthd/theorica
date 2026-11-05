import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_clean_separator_second_ray_exact_holdout():
    result = json.loads(
        (
            ROOT
            / "results/qary_ternary_clean_separator_second_ray/results.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT / "results/qary_ternary_clean_separator_second_ray/audit.json"
        ).read_text()
    )

    prospective = result["prospective"]
    assert prospective["level_costs"] == [4, 11, 2]
    assert prospective["predicted_value"] == 33
    assert prospective["exact_lower_bound"] == 33
    assert prospective["constructive_upper_bound"] == 33
    optimal = [row for row in prospective["root_actions"] if row["optimal"]]
    assert len(optimal) == 1
    assert optimal[0]["query_group"] == 3
    assert optimal[0]["child_values"] == [17, 22, 22]
    assert result["remaining_reserved_cases"] == 15
    assert result["summary"]["prediction_supported"] is True
    assert audit["passed"] is True
