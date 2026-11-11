import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_explicit_sentinel_first_breakpoint():
    result = json.loads(
        (ROOT / "results/qary_ternary_explicit_sentinel_first_breakpoint/results.json").read_text()
    )
    audit = json.loads(
        (ROOT / "results/qary_ternary_explicit_sentinel_first_breakpoint/audit.json").read_text()
    )
    assert result["summary"]["predictions_passed"] is True
    assert result["summary"]["constant_integer_chamber"] == "1<=c<=22"
    assert result["summary"]["first_positive_integer_breakpoint"] == 23
    assert audit["production_imports"] == 0
    assert audit["monotonicity_argument_valid"] is True
    assert audit["passed"] is True
