import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_complete_explicit_sentinel_obstruction_orbit_quotient():
    result = json.loads(
        (
            ROOT
            / "results/qary_ternary_explicit_sentinel_orbit_quotient/results.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "results/qary_ternary_explicit_sentinel_orbit_quotient/audit.json"
        ).read_text()
    )
    assert result["family_count"] == 36
    assert result["class_sizes"] == {"different_middle": 27, "same_middle": 9}
    assert result["representative_solve_reduction"] == 18
    assert result["summary"]["same_middle_values_c1_c23"] == [6, 69]
    assert result["summary"]["different_middle_values_c1_c23"] == [7, 38]
    assert result["summary"]["all_frozen_holdouts_passed"] is True
    assert result["summary"]["post_holdout_chamber_laws_passed"] is True
    assert result["summary"]["overall_passed"] is True
    assert audit["production_imports"] == 0
    assert audit["families_reconstructed"] == 36
    assert audit["edge_maps_independently_checked"] == 38
    assert audit["exact_root_minima_reconstructed"] == 50
    assert audit["passed"] is True
