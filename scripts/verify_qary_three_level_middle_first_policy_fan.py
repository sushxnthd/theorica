#!/usr/bin/env python3
"""Prove the exact all-positive-cost law with a finite policy fan."""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

from verify_qary_three_level_middle_first_exact_all_ratios import (
    FACES,
    exact_case,
    synthesize_face,
)

OUT = Path("results/qary_three_level_middle_first_policy_fan/results.json")
PROSPECTIVE = (
    (31, 59, 7), (43, 61, 11), (47, 53, 13),
    (53, 47, 13), (61, 43, 11), (59, 31, 7),
    (5, 17, 41), (7, 13, 37), (11, 19, 23),
    (17, 11, 29), (19, 7, 31), (37, 13, 5),
    (41, 29, 3), (29, 41, 3), (23, 17, 43),
    (17, 23, 43), (47, 31, 19), (31, 47, 19),
)
R0 = (1, 2, 0)
R1 = (2, 4, 1)
B = (2, 2, 1)
R3 = (4, 2, 1)
R4 = (2, 1, 0)
E1 = (2, 3, 0)
E2 = (1, 1, 0)
E3 = (3, 2, 0)
POLYGON = (R0, R1, B, R3, R4)
FAN = (
    (R0, R1, B),
    (R0, E1, B),
    (E1, E2, B),
    (E2, E3, B),
    (E3, R4, B),
    (R4, R3, B),
)


def point(ray):
    total = sum(ray)
    return Fraction(ray[0], total), Fraction(ray[1], total)


def twice_area(vertices):
    points = tuple(point(ray) for ray in vertices)
    return abs(sum(
        left[0] * right[1] - left[1] * right[0]
        for left, right in zip(points, (*points[1:], points[0]))
    ))


def main():
    single_face_certificates = [
        synthesize_face(index) for index in (0, 1, 2, 3, 5)
    ]
    fan_certificates = [
        synthesize_face(4, custom_rays=cell) for cell in FAN
    ]
    polygon_area = twice_area(POLYGON)
    fan_area = sum(twice_area(cell) for cell in FAN)
    boundary_order = tuple(Fraction(ray[0], ray[1]) for ray in (R0, E1, E2, E3, R4))
    coverage = {
        "problem_face_polygon": [list(ray) for ray in POLYGON],
        "fan_cells": [[list(ray) for ray in cell] for cell in FAN],
        "zero_leaf_boundary_ratios": [
            [ratio.numerator, ratio.denominator] for ratio in boundary_order
        ],
        "strict_boundary_order": all(
            left < right for left, right in pairwise(boundary_order)
        ),
        "polygon_twice_area": [polygon_area.numerator, polygon_area.denominator],
        "fan_twice_area": [fan_area.numerator, fan_area.denominator],
        "area_matched": polygon_area == fan_area,
    }
    holdouts = [exact_case(costs) for costs in PROSPECTIVE]
    summary = {
        "single_face_policies_passed": sum(row["feasible"] for row in single_face_certificates),
        "single_face_policy_total": len(single_face_certificates),
        "problem_face_fan_cells_passed": sum(row["feasible"] for row in fan_certificates),
        "problem_face_fan_cell_total": len(fan_certificates),
        "terminal_transcript_total": sum(
            row["terminal_transcripts"]
            for row in [*single_face_certificates, *fan_certificates]
        ),
        "coverage_area_matched": coverage["area_matched"],
        "coverage_boundary_ordered": coverage["strict_boundary_order"],
        "prospective_holdouts_matched": sum(row["matched"] for row in holdouts),
        "prospective_holdout_total": len(holdouts),
    }
    summary["passed"] = (
        summary["single_face_policies_passed"] == summary["single_face_policy_total"] == 5
        and summary["problem_face_fan_cells_passed"] == summary["problem_face_fan_cell_total"] == 6
        and summary["coverage_area_matched"]
        and summary["coverage_boundary_ordered"]
        and summary["prospective_holdouts_matched"] == summary["prospective_holdout_total"] == 18
    )
    result = {
        "schema": "theorica.middle-first-all-positive-costs-policy-fan/1",
        "candidate_faces": [list(face) for face in FACES],
        "single_face_policy_certificates": single_face_certificates,
        "problem_face_policy_fan_certificates": fan_certificates,
        "exact_coverage_certificate": coverage,
        "prospective_exact_holdouts": holdouts,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
