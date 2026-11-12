import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_depth4_divergence_quotient():
    directory = ROOT / "results/qary_depth4_explicit_sentinel_divergence_quotient"
    result = json.loads((directory / "results.json").read_text())
    audit = json.loads((directory / "audit.json").read_text())
    assert result["family_count"] == 351
    assert result["class_count"] == 3
    assert result["class_sizes"] == {"0": 243, "1": 81, "2": 27}
    assert result["representative_solve_reduction"] == 117
    assert result["summary"]["divergence_invariant_complete"] is True
    assert result["summary"]["all_frozen_holdouts_passed"] is True
    assert result["summary"]["closed_form_counts_passed"] is True
    assert result["summary"]["overall_passed"] is True
    assert audit["production_imports"] == 0
    assert audit["families_reconstructed"] == 351
    assert audit["edge_maps_independently_checked"] == 354
    assert audit["closed_form_identity_grid_checks"] == 42
    assert audit["passed"] is True
