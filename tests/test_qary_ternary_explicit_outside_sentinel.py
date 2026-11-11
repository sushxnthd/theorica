import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_explicit_outside_sentinel_covariance():
    result = json.loads(
        (ROOT / "results/qary_ternary_explicit_outside_sentinel/results.json").read_text()
    )
    audit = json.loads(
        (ROOT / "results/qary_ternary_explicit_outside_sentinel/audit.json").read_text()
    )
    assert result["outside_response"] == -1
    assert result["summary"]["structural_covariance_restored"] is True
    assert result["summary"]["endpoint_and_root_signatures_equal"] is True
    assert result["summary"]["search_counts_equal"] is True
    assert result["summary"]["overall_covariance_claim_passed"] is True
    assert result["summary"]["frozen_numeric_predictions_passed"] is False
    assert [row["exact_value"] for row in result["source_endpoints"]] == [37, 37]
    assert result["source_endpoints"][1]["group0_children"] == [30, 30, 33]
    assert audit["production_imports"] == 0
    assert audit["passed"] is True
