import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_quaternary_explicit_sentinel_orbit_transfer():
    directory = ROOT / "results/qary_quaternary_explicit_sentinel_orbit_transfer"
    result = json.loads((directory / "results.json").read_text())
    audit = json.loads((directory / "audit.json").read_text())
    assert result["family_count"] == 120
    assert result["class_sizes"] == {"different_middle": 96, "same_middle": 24}
    assert result["representative_solve_reduction"] == 60
    assert result["summary"]["two_class_generalization_passed"] is True
    assert result["summary"]["active_row_reduction_passed"] is True
    assert result["summary"]["all_frozen_symbol3_holdouts_passed"] is True
    assert result["summary"]["overall_passed"] is True
    assert audit["production_imports"] == 0
    assert audit["families_reconstructed"] == 120
    assert audit["edge_maps_independently_checked"] == 122
    assert audit["exact_root_minima_reconstructed"] == 8
    assert audit["passed"] is True
