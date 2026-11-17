import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/qary_twisted_burnside_complement/results.json"
AUDIT = ROOT / "results/qary_twisted_burnside_complement/audit.json"


def test_twisted_burnside_complement_law_on_unseen_depth_four_tree():
    subprocess.run(
        [sys.executable, "scripts/verify_qary_twisted_burnside_complement.py"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "scripts/audit_qary_twisted_burnside_complement.py"],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(RESULT.read_text())
    audit = json.loads(AUDIT.read_text())
    holdout = result["q2_h4_holdout"]

    assert result["summary"]["overall_passed"] is True
    assert holdout["group_order"] == 32768
    assert holdout["suffix_shape_classes"] == 231
    assert holdout["complement_fixed_shape_classes"] == 23
    assert holdout["twisted_weight_sum"] == 753664
    assert holdout["twisted_orbit_count"] == 23
    assert audit["production_imports"] == 0
    assert audit["passed"] is True
    assert audit["group_order_reconstructed"] == holdout["group_order"]
    assert audit["twisted_weight_sum_reconstructed"] == holdout["twisted_weight_sum"]
    assert (
        audit["eligible_even_cycle_automorphisms_reconstructed"]
        == holdout["eligible_even_cycle_automorphisms"]
    )
    assert (
        audit["cycle_type_distribution_sha256"]
        == holdout["cycle_type_distribution_sha256"]
    )
