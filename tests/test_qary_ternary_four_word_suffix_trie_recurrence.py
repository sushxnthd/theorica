import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/qary_ternary_four_word_suffix_trie_recurrence/results.json"
AUDIT = ROOT / "results/qary_ternary_four_word_suffix_trie_recurrence/audit.json"


def test_ternary_four_word_suffix_trie_recurrence_is_complete_and_audited():
    result = json.loads(RESULT.read_text())
    audit = json.loads(AUDIT.read_text())
    assert result["summary"]["overall_passed"] is True
    assert result["family_count"] == 17550
    assert result["class_count"] == 11
    assert result["class_sizes"] == result["recurrence_counts"]
    assert sum(result["class_sizes"].values()) == 17550
    assert result["q4_symbolic_identity"]["class_count"] == 14
    assert result["q4_symbolic_identity"]["sum"] == 635376
    assert result["representative_solve_reduction"] == {
        "from": 17550,
        "to": 11,
        "ratio": "17550/11",
    }
    assert audit["passed"] is True
    assert audit["production_imports"] == 0
    assert audit["transport_digests_reproduced"] == 17550
    assert audit["class_transport_streams_reproduced"] == 11
    assert audit["holdout_maps_reproduced"] == 11
