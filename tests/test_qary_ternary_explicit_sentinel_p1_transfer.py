import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_explicit_sentinel_p1_structural_transfer_and_holdout():
    result = json.loads(
        (
            ROOT / "results/qary_ternary_explicit_sentinel_p1_transfer/results.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT / "results/qary_ternary_explicit_sentinel_p1_transfer/audit.json"
        ).read_text()
    )
    assert result["summary"]["all_frozen_predictions_passed"] is True
    assert result["summary"]["structural_transfer_passed"] is True
    assert result["summary"]["unseen_composed_transport_passed"] is True
    assert audit["production_imports"] == 0
    assert audit["structural_isomorphisms_edge_checked"] is True
    assert audit["p1_integer_chamber_transfers_from_p0"] is True
    assert audit["passed"] is True
