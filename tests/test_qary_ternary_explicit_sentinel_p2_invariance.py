import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_explicit_sentinel_p2_invariance():
    result = json.loads(
        (ROOT / "results/qary_ternary_explicit_sentinel_p2_invariance/results.json").read_text()
    )
    audit = json.loads(
        (ROOT / "results/qary_ternary_explicit_sentinel_p2_invariance/audit.json").read_text()
    )
    assert result["summary"]["frozen_invariance_prediction_passed"] is False
    assert result["summary"]["classification"] == "boundary_invariance_falsified"
    assert result["summary"]["response_refinement_changes_p2_values"] is True
    assert result["summary"]["observed_values_c7_c8"] == [25, 28]
    assert result["summary"]["exploratory_integer_law_c1_c8"] == "V=4+3c"
    assert result["summary"]["unseen_family_covariance_passed"] is True
    assert audit["production_imports"] == 0
    assert audit["frozen_prediction_falsified"] is True
    assert audit["query_group_3_maps_to_1"] is True
    assert audit["exploratory_law_c1_c8_replayed"] is True
    assert audit["passed"] is True
