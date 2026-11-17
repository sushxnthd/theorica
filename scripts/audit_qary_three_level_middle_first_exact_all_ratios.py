#!/usr/bin/env python3
"""Zero-import audit of the all-positive-cost upper-route falsification."""

from __future__ import annotations

import json
from functools import cache
from itertools import combinations
from math import gcd
from pathlib import Path

SOURCE = Path("results/qary_three_level_middle_first_exact_all_ratios/results.json")
OUT = Path("results/qary_three_level_middle_first_exact_all_ratios/audit.json")
FACES = ((1, 5, 1), (2, 3, 4), (2, 4, 3), (3, 3, 3), (3, 4, 1), (4, 2, 1))


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def rays(face):
    constraints = (
        (1, 0, 0), (0, 1, 0), (0, 0, 1),
        *(tuple(a - b for a, b in zip(face, other)) for other in FACES if other != face),
    )
    answer = set()
    for left, right in combinations(constraints, 2):
        raw = cross(left, right)
        for candidate in (raw, tuple(-value for value in raw)):
            if candidate == (0, 0, 0) or not all(dot(row, candidate) >= 0 for row in constraints):
                continue
            divisor = 0
            for value in candidate:
                divisor = gcd(divisor, abs(value))
            answer.add(tuple(value // divisor for value in candidate))
    return tuple(sorted(answer))


def groups():
    words = tuple(
        (root, middle, leaf)
        for root in range(2)
        for middle in range(2)
        for leaf in range(2)
    )
    answer = []
    for level in range(3):
        for prefix in sorted({word[:level] for word in words}):
            answer.append(tuple(word[level] if word[:level] == prefix else 0 for word in words))
    return tuple(answer)


def independently_refute_common_problem_face_policy():
    rows = groups()
    alphabets = tuple(tuple(sorted(set(row))) for row in rows)
    face = FACES[4]
    cone_rays = rays(face)
    limits = tuple(dot(face, ray) for ray in cone_rays)
    states = 0

    def children(counts, erased, remaining, group):
        row = rows[group]
        rest = tuple(count - (index == group) for index, count in enumerate(remaining))
        answer = []
        for observed in alphabets[group]:
            child = tuple(
                min(2, count + (row[index] != observed))
                for index, count in enumerate(counts)
            )
            if any(count <= 1 for count in child):
                answer.append((child, erased, rest))
        if erased == 0:
            answer.append((counts, 1, rest))
        return tuple(answer)

    @cache
    def feasible(counts, erased, remaining, budgets, initial):
        nonlocal states
        states += 1
        live = tuple(index for index, count in enumerate(counts) if count <= 1)
        if len(live) <= 1:
            return True
        for group, count in enumerate(remaining):
            if count == 0 or (initial and group not in (1, 2)):
                continue
            row = rows[group]
            if len({row[index] for index in live}) < 2:
                continue
            level = 0 if group == 0 else (1 if group < 3 else 2)
            costs = tuple(ray[level] for ray in cone_rays)
            if any(cost > budget for cost, budget in zip(costs, budgets)):
                continue
            next_budgets = tuple(budget - cost for budget, cost in zip(budgets, costs))
            descendants = children(counts, erased, remaining, group)
            if descendants and all(
                feasible(*child, next_budgets, False) for child in descendants
            ):
                return True
        return False

    initial = ((0,) * 8, 0, (4,) * len(rows), limits, True)
    return feasible(*initial), states


def main():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    certificates = payload["face_cone_policy_certificates"]
    ray_matches = []
    exposure_checks = []
    for face, record in zip(FACES, certificates):
        expected_rays = rays(face)
        ray_matches.append(tuple(map(tuple, record["extreme_rays"])) == expected_rays)
        if record["feasible"]:
            exposure_checks.append(all(
                dot(exposure, ray) <= dot(face, ray)
                for exposure in map(tuple, record["unique_terminal_exposures"])
                for ray in expected_rays
            ))
    feasible, states = independently_refute_common_problem_face_policy()
    holdouts = payload["prospective_exact_holdouts"]
    report = {
        "production_module_imports": 0,
        "face_ray_enumerations_matched": sum(ray_matches),
        "face_ray_enumeration_total": len(ray_matches),
        "feasible_face_exposure_replays_passed": sum(exposure_checks),
        "feasible_face_exposure_replay_total": len(exposure_checks),
        "problem_face_common_policy_independently_feasible": feasible,
        "problem_face_independent_states": states,
        "prospective_scalar_matches": sum(row["matched"] for row in holdouts),
        "prospective_scalar_total": len(holdouts),
    }
    report["passed"] = (
        report["face_ray_enumerations_matched"] == report["face_ray_enumeration_total"] == 6
        and report["feasible_face_exposure_replays_passed"]
        == report["feasible_face_exposure_replay_total"] == 5
        and not feasible
        and states == 3719
        and report["prospective_scalar_matches"] == report["prospective_scalar_total"] == 12
    )
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["passed"]:
        raise SystemExit("independent falsification audit failed")


if __name__ == "__main__":
    main()
