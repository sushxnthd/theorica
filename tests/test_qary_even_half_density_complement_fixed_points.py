import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/qary_even_half_density_complement_fixed_points/results.json"
AUDIT = ROOT / "results/qary_even_half_density_complement_fixed_points/audit.json"


def test_even_half_density_complement_fixed_point_law_is_exact_and_audited():
    subprocess.run(
        [sys.executable, "scripts/verify_qary_even_half_density_complement_fixed_points.py"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "scripts/audit_qary_even_half_density_complement_fixed_points.py"],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(RESULT.read_text())
    audit = json.loads(AUDIT.read_text())

    holdout = result["q6_h2_holdout"]
    assert result["summary"]["overall_passed"] is True
    assert holdout["labelled_family_count"] == 9075135300
    assert holdout["total_orbit_classes"] == 924
    assert holdout["half_density_classes"] == 58
    assert holdout["self_complementary_classes"] == 20
    assert holdout["nonfixed_complement_pairs"] == 19
    assert holdout["coefficient_window_15_21"] == [51, 55, 55, 58, 55, 55, 51]
    assert len(holdout["fixed_child_bijections"]) == 20

    q4 = result["q4_h3_theorem_check"]
    assert q4 == {
        "half_density_classes": 60802,
        "nonfixed_complement_pairs": 29738,
        "self_complementary_classes": 1326,
        "total_orbit_classes": 1088430,
    }
    assert audit["passed"] is True
    assert audit["production_imports"] == 0
    assert audit["orbit_representatives_reconstructed"] == 924
    assert audit["fixed_classes_reconstructed"] == 20
