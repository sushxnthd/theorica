import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_zero_moving_symbol_boundary():
    result = json.loads(
        (ROOT / "results/qary_ternary_zero_moving_symbol_boundary/results.json").read_text()
    )
    audit = json.loads(
        (ROOT / "results/qary_ternary_zero_moving_symbol_boundary/audit.json").read_text()
    )
    assert result["level_preserving_isomorphism"] is None
    assert result["nonisomorphism_certificate"]["WL_multiplicity_separation"] is True
    assert result["scalar_and_root_coincidence"] is True
    assert result["summary"]["universal_symbol_transport_falsified"] is True
    assert result["summary"]["endpoint_scalar_coincidence_preserved"] is True
    assert result["completed_panel_reopened"] is False
    assert audit["production_imports"] == 0
    assert audit["color_multiplicity_separation_valid"] is True
    assert audit["search_expansion_valid"] is True
    assert audit["passed"] is True
