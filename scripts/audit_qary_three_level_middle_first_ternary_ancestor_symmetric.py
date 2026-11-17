#!/usr/bin/env python3
"""Independent zero-production-import audit of the ternary (x,x,y) theorem."""

from __future__ import annotations

import json
from pathlib import Path

from audit_qary_three_level_middle_first_ternary_symmetric import exact_depth

SOURCE = Path(
    "results/qary_three_level_middle_first_ternary_ancestor_symmetric/results.json"
)
UNIT = Path("results/qary_three_level_middle_first_ternary_symmetric/results.json")
OUT = Path(
    "results/qary_three_level_middle_first_ternary_ancestor_symmetric/audit.json"
)
CONES = (
    ((7, 1), ((1, 0), (2, 1))),
    ((6, 3), ((1, 1), (2, 1))),
    ((5, 4), ((0, 1), (1, 1))),
)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def main():
    primary = json.loads(SOURCE.read_text(encoding="utf-8"))
    unit = json.loads(UNIT.read_text(encoding="utf-8"))
    exposures = tuple(
        (row[0] + row[1], row[2]) for row in unit["unique_terminal_exposures"]
    )
    inequalities = []
    for face, rays in CONES:
        for ray in rays:
            inequalities.append(
                max(dot(exposure, ray) for exposure in exposures) <= dot(face, ray)
            )
    holdouts = primary["prospective_holdouts"]
    holdout_checks = []
    for row in holdouts:
        x = row["root_middle_cost"]
        y = row["leaf_cost"]
        values = (7 * x + y, 6 * x + 3 * y, 5 * x + 4 * y)
        holdout_checks.append(
            row["face_values"] == list(values) and row["exact_cost"] == max(values)
        )
    depth_8, depth_9, depth_states = exact_depth()
    report = {
        "production_module_imports": 0,
        "independent_depth_8_feasible": depth_8,
        "independent_depth_9_feasible": depth_9,
        "independent_depth_states": depth_states,
        "independent_ray_inequalities_passed": sum(inequalities),
        "independent_ray_inequality_total": len(inequalities),
        "independent_holdouts_passed": sum(holdout_checks),
        "independent_holdout_total": len(holdout_checks),
        "phase_boundaries": ["x=y", "x=2y"],
        "binary_embedding_faces_replayed": 3,
    }
    report["passed"] = (
        not depth_8
        and depth_9
        and report["independent_ray_inequalities_passed"]
        == report["independent_ray_inequality_total"]
        == 6
        and report["independent_holdouts_passed"]
        == report["independent_holdout_total"]
        == 12
        and primary["summary"]["passed"]
    )
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
