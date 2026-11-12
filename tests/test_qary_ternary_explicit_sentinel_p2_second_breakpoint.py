import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_explicit_sentinel_p2_second_breakpoint_and_transport():
    result = json.loads(
        (
            ROOT
            / "results/qary_ternary_explicit_sentinel_p2_second_breakpoint/results.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "results/qary_ternary_explicit_sentinel_p2_second_breakpoint/audit.json"
        ).read_text()
    )
    assert result["summary"]["all_frozen_predictions_passed"] is True
    assert result["summary"]["first_post_collision_increase"] == 23
    assert result["summary"]["unseen_zero_one_transport_passed"] is True
    assert audit["production_imports"] == 0
    assert audit["low_law_c1_c8"] is True
    assert audit["diagnostic_law_c9_c10"] is True
    assert audit["monotonicity_closes_all_integer_costs_c11_c22"] is True
    assert audit["first_post_collision_increase_c23"] is True
    assert audit["passed"] is True
