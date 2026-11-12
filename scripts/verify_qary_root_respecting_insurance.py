#!/usr/bin/env python3
"""Verify the frozen arbitrary-depth root-respecting insurance law."""

from __future__ import annotations

import hashlib
import json
from itertools import product
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_qary_root_respecting_insurance,
)

OUT = Path("results/qary_root_respecting_insurance/results.json")
HOLDOUTS = (
    (2, (3, 1, 4, 2)),
    (3, (2, 5, 1, 3)),
    (5, (1, 3, 2, 7, 1)),
    (2, (6, 1, 2, 1, 3, 2)),
    (3, (1, 2, 3, 4, 5, 6, 7, 8)),
)


def case(arity, costs):
    certificate = certify_qary_root_respecting_insurance(arity, costs)
    return {
        "arity": arity,
        "depth": len(costs),
        "level_costs": list(costs),
        "face_count": len(certificate.face_vectors),
        "face_vectors": [list(face) for face in certificate.face_vectors],
        "face_costs": list(certificate.face_costs),
        "active_face_vectors": [list(face) for face in certificate.active_face_vectors],
        "face_maximum": max(certificate.face_costs),
        "recurrence_cost": certificate.recurrence_cost,
        "exact_root_respecting_cost": certificate.exact_worst_case_cost,
        "certificate_valid": certificate.certificate_valid,
    }


def main():
    holdouts = [case(arity, costs) for arity, costs in HOLDOUTS]
    exhaustive = []
    for depth in range(1, 7):
        for costs in product((1, 2, 3), repeat=depth):
            item = case(2 + sum(costs) % 4, costs)
            exhaustive.append(
                {
                    "arity": item["arity"],
                    "depth": depth,
                    "level_costs": item["level_costs"],
                    "face_count": item["face_count"],
                    "value": item["exact_root_respecting_cost"],
                    "matched": item["face_maximum"] == item["recurrence_cost"],
                }
            )
    exhaustive_payload = json.dumps(exhaustive, sort_keys=True, separators=(",", ":"))
    missing = certify_qary_root_respecting_insurance(
        3,
        (2, 5, 1, 3),
        available_copies=(4, 4, 3, 4),
    )
    calibration = [
        {
            "arity": 2,
            "level_costs": [1, 1, 1, 1],
            "unrestricted_exact_cost": 10,
            "root_respecting_cost": certify_qary_root_respecting_insurance(
                2, (1, 1, 1, 1)
            ).exact_worst_case_cost,
        },
        {
            "arity": 2,
            "level_costs": [1, 1, 1, 20],
            "unrestricted_exact_cost": 86,
            "root_respecting_cost": certify_qary_root_respecting_insurance(
                2, (1, 1, 1, 20)
            ).exact_worst_case_cost,
        },
    ]
    summary = {
        "holdout_total": len(holdouts),
        "holdouts_matched": sum(
            item["certificate_valid"]
            and item["face_maximum"] == item["recurrence_cost"]
            for item in holdouts
        ),
        "holdout_face_counts": [item["face_count"] for item in holdouts],
        "exhaustive_total": len(exhaustive),
        "exhaustive_matches": sum(item["matched"] for item in exhaustive),
        "exhaustive_digest": hashlib.sha256(exhaustive_payload.encode()).hexdigest(),
        "missing_copy_abstained": not missing.certificate_valid
        and missing.exact_worst_case_cost is None,
        "calibration_matches": sum(
            item["unrestricted_exact_cost"] == item["root_respecting_cost"]
            for item in calibration
        ),
    }
    summary["passed"] = (
        summary["holdouts_matched"] == summary["holdout_total"]
        and summary["holdout_face_counts"] == [10, 10, 15, 21, 36]
        and summary["exhaustive_matches"] == summary["exhaustive_total"] == 1092
        and summary["missing_copy_abstained"]
        and summary["calibration_matches"] == len(calibration)
    )
    result = {
        "schema": "theorica.qary-root-respecting-insurance/1",
        "claim": "F_d=max(2c_1+F_{d-1},3c_1+G_{d-1},4c_1+H_{d-1}) with d(d+1)/2 exact faces",
        "pre_freeze_timeouts": [
            [2, 20, 1, 1, 1],
            [2, 1, 20, 1, 1],
            [2, 1, 1, 20, 1],
        ],
        "calibration": calibration,
        "holdouts": holdouts,
        "missing_copy": {
            "available_copies": list(missing.available_copies),
            "certificate_valid": missing.certificate_valid,
            "exact_cost": missing.exact_worst_case_cost,
            "reason": missing.reason,
        },
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
