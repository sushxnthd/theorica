import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/qary_ternary_dense_suffix_trie_complement_duality/results.json"
AUDIT = ROOT / "results/qary_ternary_dense_suffix_trie_complement_duality/audit.json"


def test_dense_suffix_trie_complement_duality_is_complete_and_audited():
    result = json.loads(RESULT.read_text())
    audit = json.loads(AUDIT.read_text())

    assert result["summary"]["overall_passed"] is True
    assert result["orbit_polynomial_palindromic"] is True
    assert result["family_count"] == 80730
    assert result["class_count"] == 18
    assert sorted(result["class_sizes"]) == sorted(result["sparse_class_sizes"])
    assert len(result["sparse_to_dense_class"]) == 18
    assert len({row["dense_class"] for row in result["sparse_to_dense_class"].values()}) == 18
    assert result["automorphism_group_order"] == 13060694016
    assert result["q4_symbolic_complement_identity"]["class_count_each"] == 24
    assert result["q4_symbolic_complement_identity"]["sum_each"] == 7624512

    assert audit["passed"] is True
    assert audit["production_imports"] == 0
    assert audit["transport_digests_reproduced"] == 80730
    assert audit["class_transport_streams_reproduced"] == 18
    assert audit["holdout_maps_reproduced"] == 18
    assert audit["cross_classes_separated"] is True
