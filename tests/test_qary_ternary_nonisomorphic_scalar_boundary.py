import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_nonisomorphic_scalar_boundary_reproduces():
    subprocess.run(
        [
            sys.executable,
            "scripts/verify_qary_ternary_nonisomorphic_scalar_boundary.py",
        ],
        cwd=ROOT,
        check=True,
    )


def test_nonisomorphic_scalar_boundary_independent_audit():
    subprocess.run(
        [sys.executable, "scripts/audit_qary_ternary_nonisomorphic_scalar_boundary.py"],
        cwd=ROOT,
        check=True,
    )
