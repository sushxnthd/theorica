import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/qary_complement_transporter_coset/results.json"
AUDIT = ROOT / "results/qary_complement_transporter_coset/audit.json"


def test_complement_transporter_coset_law_is_exact_and_independently_audited():
    subprocess.run(
        [sys.executable, "scripts/verify_qary_complement_transporter_coset.py"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "scripts/audit_qary_complement_transporter_coset.py"],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(RESULT.read_text())
    audit = json.loads(AUDIT.read_text())

    holdout = result["q10_h2_holdout"]
    assert result["summary"]["overall_passed"] is True
    assert holdout["total_orbit_classes"] == 184756
    assert holdout["half_density_classes"] == 5448
    assert holdout["self_complementary_classes"] == 252
    assert holdout["nonfixed_complement_pairs"] == 2598
    assert len(holdout["fixed_class_records"]) == 252
    assert all(row["full_map_passed"] for row in holdout["fixed_class_records"])
    assert all(
        row["orbit_times_transporters"] == holdout["group_order"]
        for row in holdout["fixed_class_records"]
    )

    assert audit["passed"] is True
    assert audit["production_imports"] == 0
    assert audit["orbit_representatives_reconstructed"] == 184756
    assert audit["full_involutions_reconstructed"] == 252
    assert audit["fixed_record_stream_sha256"] == holdout["fixed_record_stream_sha256"]
    assert audit["small_model"]["group_elements"] == 8
    assert all(row["equal"] for row in audit["small_model"]["fixed_classes"])
