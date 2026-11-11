import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_explicit_sentinel_p2_policy_reversal():
    result = json.loads(
        (ROOT / "results/qary_ternary_explicit_sentinel_p2_policy_reversal/results.json").read_text()
    )
    audit = json.loads(
        (ROOT / "results/qary_ternary_explicit_sentinel_p2_policy_reversal/audit.json").read_text()
    )
    summary = result["summary"]
    assert summary["all_frozen_predictions_passed"] is False
    assert summary["collision_prediction_passed"] is True
    assert summary["reversal_prediction_passed"] is False
    assert summary["classification"] == "collision_confirmed_reversal_falsified"
    assert summary["collision_cost"] == 11
    assert summary["observed_c12_value"] == 37
    assert summary["observed_c12_optimal_groups"] == [0]
    assert summary["unseen_family_transport_passed"] is True
    assert audit["production_imports"] == 0
    assert audit["collision_at_c11_valid"] is True
    assert audit["reversal_at_c12_falsified"] is True
    assert audit["unseen_family_transport_valid"] is True
    assert audit["passed"] is True
