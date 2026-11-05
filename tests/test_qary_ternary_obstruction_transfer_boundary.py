import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_obstruction_transfer_boundary_reproduces():
    subprocess.run(
        [
            sys.executable,
            "scripts/verify_qary_ternary_obstruction_transfer_boundary.py",
        ],
        cwd=ROOT,
        check=True,
    )


def test_obstruction_transfer_boundary_independent_audit():
    subprocess.run(
        [sys.executable, "scripts/audit_qary_ternary_obstruction_transfer_boundary.py"],
        cwd=ROOT,
        check=True,
    )
