#!/usr/bin/env python3
"""Prove the exact ternary middle-first law for costs (x,x,y)."""

from __future__ import annotations

import json
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_ternary_middle_first_ancestor_symmetric,
)

SOURCE = Path("results/qary_three_level_middle_first_ternary_symmetric/results.json")
OUT = Path(
    "results/qary_three_level_middle_first_ternary_ancestor_symmetric/results.json"
)
CONES = (
    {"face": (7, 1), "rays": ((1, 0), (2, 1))},
    {"face": (6, 3), "rays": ((1, 1), (2, 1))},
    {"face": (5, 4), "rays": ((0, 1), (1, 1))},
)
PROSPECTIVE = (
    (79, 1),
    (81, 40),
    (41, 40),
    (40, 41),
    (1, 79),
    (2, 1),
    (1, 1),
    (3, 2),
    (5, 7),
    (11, 3),
    (13, 17),
    (29, 11),
)


def projected(exposure):
    return exposure[0] + exposure[1], exposure[2]


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def main():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    exposures = tuple(
        projected(tuple(row)) for row in source["unique_terminal_exposures"]
    )
    cone_certificates = []
    for cone in CONES:
        inequalities = []
        for ray in cone["rays"]:
            face_cost = dot(cone["face"], ray)
            policy_cost = max(dot(exposure, ray) for exposure in exposures)
            inequalities.append(
                {
                    "ray": list(ray),
                    "face_cost": face_cost,
                    "policy_cost": policy_cost,
                    "passed": policy_cost <= face_cost,
                }
            )
        cone_certificates.append(
            {
                "face": list(cone["face"]),
                "rays": [list(ray) for ray in cone["rays"]],
                "inequalities": inequalities,
                "passed": all(row["passed"] for row in inequalities),
            }
        )
    holdouts = []
    for x, y in PROSPECTIVE:
        certificate = certify_ternary_middle_first_ancestor_symmetric(x, y)
        holdouts.append(
            {
                "root_middle_cost": x,
                "leaf_cost": y,
                "face_values": list(certificate.adversary_lower_bounds),
                "exact_cost": certificate.exact_worst_case_cost,
                "active_faces": list(certificate.active_faces),
                "certificate_valid": certificate.certificate_valid,
            }
        )
    summary = {
        "cone_certificates_passed": sum(row["passed"] for row in cone_certificates),
        "cone_certificate_total": len(cone_certificates),
        "ray_inequalities_passed": sum(
            inequality["passed"]
            for cone in cone_certificates
            for inequality in cone["inequalities"]
        ),
        "ray_inequality_total": sum(
            len(cone["inequalities"]) for cone in cone_certificates
        ),
        "terminal_transcripts_reused": source["terminal_transcripts"],
        "prospective_holdouts_certified": sum(
            row["certificate_valid"] for row in holdouts
        ),
        "prospective_holdout_total": len(holdouts),
        "binary_embedding_lower_faces": 3,
    }
    summary["passed"] = (
        summary["cone_certificates_passed"] == summary["cone_certificate_total"] == 3
        and summary["ray_inequalities_passed"] == summary["ray_inequality_total"] == 6
        and summary["prospective_holdouts_certified"]
        == summary["prospective_holdout_total"]
        == len(PROSPECTIVE)
        and source["passed"]
    )
    result = {
        "schema": "theorica.middle-first-ternary-ancestor-symmetric/1",
        "theorem": "T_3(x,x,y)=max(7x+y,6x+3y,5x+4y)",
        "projected_policy_exposures": [list(row) for row in sorted(set(exposures))],
        "cone_certificates": cone_certificates,
        "prospective_holdouts": holdouts,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
