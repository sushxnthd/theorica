import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/qary_quaternary_arbitrary_family_alphabet_lift/results.json"
AUDIT = ROOT / "results/qary_quaternary_arbitrary_family_alphabet_lift/audit.json"


def test_quaternary_arbitrary_family_alphabet_lift_is_complete_and_audited():
    result = json.loads(RESULT.read_text())
    audit = json.loads(AUDIT.read_text())
    assert result["summary"]["overall_passed"] is True
    assert result["family_count"] == 41664
    assert result["class_sizes"] == {
        "0": 1152,
        "1": 4608,
        "2": 64,
        "3": 18432,
        "4": 1024,
        "5": 16384,
    }
    assert result["representative_solve_reduction"]["factor"] == 6944
    assert audit["passed"] is True
    assert audit["production_imports"] == 0
    assert audit["transport_digests_reproduced"] == 41664
    assert audit["aggregate_transport_stream_reproduced"] is True
    assert audit["class_transport_streams_reproduced"] == 6
    assert audit["holdout_maps_reproduced"] == 6
