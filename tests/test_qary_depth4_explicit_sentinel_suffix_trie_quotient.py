import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/qary_depth4_explicit_sentinel_suffix_trie_quotient/results.json"
AUDIT = ROOT / "results/qary_depth4_explicit_sentinel_suffix_trie_quotient/audit.json"


def test_suffix_trie_quotient_complete_and_independently_audited():
    result = json.loads(RESULT.read_text())
    audit = json.loads(AUDIT.read_text())
    assert result["summary"]["overall_passed"] is True
    assert result["family_count"] == 2925
    assert result["class_count"] == 6
    assert sorted(result["class_sizes"].values(), reverse=True) == [
        1458,
        729,
        486,
        162,
        81,
        9,
    ]
    assert audit["passed"] is True
    assert audit["production_imports"] == 0
    assert audit["transport_digests_reproduced"] == 2925
    assert audit["holdout_maps_reproduced"] == 6
    assert audit["recursive_formula_grid_checks"] == 12
