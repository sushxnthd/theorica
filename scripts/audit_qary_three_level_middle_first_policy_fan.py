#!/usr/bin/env python3
"""Zero-import audit of the exact all-positive-cost policy fan."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

SOURCE = Path("results/qary_three_level_middle_first_policy_fan/results.json")
OUT = Path("results/qary_three_level_middle_first_policy_fan/audit.json")
FACES = ((1, 5, 1), (2, 3, 4), (2, 4, 3), (3, 3, 3), (3, 4, 1), (4, 2, 1))


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def point(ray):
    total = sum(ray)
    return Fraction(ray[0], total), Fraction(ray[1], total)


def twice_area(vertices):
    points = tuple(point(ray) for ray in vertices)
    return abs(sum(
        left[0] * right[1] - left[1] * right[0]
        for left, right in zip(points, (*points[1:], points[0]))
    ))


def replay(record):
    face = tuple(record["face"])
    rays = tuple(map(tuple, record["extreme_rays"]))
    exposures = tuple(map(tuple, record["unique_terminal_exposures"]))
    return all(
        dot(exposure, ray) <= dot(face, ray)
        for exposure in exposures
        for ray in rays
    )


def main():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    singles = payload["single_face_policy_certificates"]
    fan = payload["problem_face_policy_fan_certificates"]
    coverage = payload["exact_coverage_certificate"]
    polygon = tuple(map(tuple, coverage["problem_face_polygon"]))
    cells = tuple(tuple(map(tuple, cell)) for cell in coverage["fan_cells"])
    polygon_area = twice_area(polygon)
    fan_area = sum(twice_area(cell) for cell in cells)
    holdouts = payload["prospective_exact_holdouts"]
    exact_costs = [
        max(dot(face, tuple(row["level_costs"])) for face in FACES)
        for row in holdouts
    ]
    report = {
        "production_module_imports": 0,
        "single_face_exposure_replays": sum(replay(row) for row in singles),
        "single_face_exposure_replay_total": len(singles),
        "fan_cell_exposure_replays": sum(replay(row) for row in fan),
        "fan_cell_exposure_replay_total": len(fan),
        "polygon_twice_area": [polygon_area.numerator, polygon_area.denominator],
        "fan_twice_area": [fan_area.numerator, fan_area.denominator],
        "coverage_area_matched": polygon_area == fan_area,
        "prospective_formula_matches": sum(
            expected == row["predicted_cost"] == row["exact_cost"]
            for expected, row in zip(exact_costs, holdouts)
        ),
        "prospective_total": len(holdouts),
    }
    report["passed"] = (
        report["single_face_exposure_replays"] == report["single_face_exposure_replay_total"] == 5
        and report["fan_cell_exposure_replays"] == report["fan_cell_exposure_replay_total"] == 6
        and report["coverage_area_matched"]
        and report["prospective_formula_matches"] == report["prospective_total"] == 18
    )
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
