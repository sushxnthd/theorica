import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/qary_ternary_five_word_suffix_trie_generating_law/results.json"
AUDIT = ROOT / "results/qary_ternary_five_word_suffix_trie_generating_law/audit.json"


def test_ternary_five_word_suffix_trie_generating_law_is_complete_and_audited():
    result = json.loads(RESULT.read_text())
    audit = json.loads(AUDIT.read_text())
    assert result["summary"]["overall_passed"] is True
    assert result["family_count"] == 80730
    assert result["class_count"] == 18
    assert len(result["generating_polynomial_coefficients"]) == 27
    assert result["generating_polynomial_coefficients"][:5] == [1, 3, 6, 11, 18]
    assert result["class_sizes"] == result["recurrence_counts"]
    assert sum(result["class_sizes"]) == 80730
    assert result["q4_symbolic_identity"]["class_count"] == 24
    assert result["q4_symbolic_identity"]["sum"] == 7624512
    assert result["representative_solve_reduction"] == {
        "from": 80730,
        "to": 18,
        "ratio": "80730/18",
    }
    assert audit["passed"] is True
    assert audit["production_imports"] == 0
    assert audit["transport_digests_reproduced"] == 80730
    assert audit["class_transport_streams_reproduced"] == 18
    assert audit["holdout_maps_reproduced"] == 18
