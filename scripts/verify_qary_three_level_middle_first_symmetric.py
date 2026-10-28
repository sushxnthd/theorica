#!/usr/bin/env python3
"""Prove the frozen symmetric-cost middle-first law exactly."""

from __future__ import annotations

import json
from fractions import Fraction
from functools import cache
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_three_level_middle_first_symmetric/results.json")
FACES = ((7, 1), (6, 3), (5, 4))
HOLDOUTS = ((79, 1), (81, 40), (41, 40), (40, 41), (1, 79), (2, 1), (1, 1))
CONES = (
    {"face": (7, 1), "synthesis_point": (2, 1), "rays": ((1, 0), (2, 1))},
    {"face": (6, 3), "synthesis_point": (1, 1), "rays": ((1, 1), (2, 1))},
    {"face": (5, 4), "synthesis_point": (1, 1), "rays": ((0, 1), (1, 1))},
)


def games():
    return tuple(
        (
            (1 - (p := Fraction(index + 1, 9)), p - 1),
            (-p, p),
        )
        for index in range(8)
    )


def problem():
    words = tuple(
        (root, middle, leaf)
        for root in range(2)
        for middle in range(2)
        for leaf in range(2)
    )
    groups = []
    for level in range(3):
        for prefix in sorted({word[:level] for word in words}):
            row = tuple(word[level] if word[:level] == prefix else 0 for word in words)
            groups.append((row, 0 if level < 2 else 1, 4))
    return tuple(groups)


def maximal(vectors):
    vectors = set(vectors)
    return frozenset(
        vector
        for vector in vectors
        if not any(
            vector != other
            and all(left <= right for left, right in zip(vector, other))
            for other in vectors
        )
    )


def intersect_downsets(left, right):
    return maximal(
        tuple(min(a, b) for a, b in zip(x, y)) for x in left for y in right
    )


def projected_guarantees(groups):
    alphabets = tuple(tuple(sorted(set(row))) for row, _, _ in groups)
    states = 0

    def children(counts, erased, remaining, group):
        row, _, _ = groups[group]
        next_remaining = tuple(
            count - (index == group) for index, count in enumerate(remaining)
        )
        answer = []
        for observed in alphabets[group]:
            child = tuple(
                min(2, count + (row[index] != observed))
                for index, count in enumerate(counts)
            )
            if any(count <= 1 for count in child):
                answer.append((child, erased, next_remaining))
        if erased < 1:
            answer.append((counts, erased + 1, next_remaining))
        return tuple(answer)

    @cache
    def guarantees(counts, erased, remaining, initial):
        nonlocal states
        states += 1
        feasible = tuple(index for index, count in enumerate(counts) if count <= 1)
        if len(feasible) <= 1:
            return frozenset({(0, 0)})
        action_guarantees = []
        for group, count in enumerate(remaining):
            if count == 0 or (initial and group not in (1, 2)):
                continue
            row, axis, _ = groups[group]
            if len({row[index] for index in feasible}) < 2:
                continue
            union = set()
            for child in children(counts, erased, remaining, group):
                union.update(
                    tuple(value + (coordinate == axis) for coordinate, value in enumerate(vector))
                    for vector in guarantees(*child, False)
                )
            action_guarantees.append(maximal(union))
        if not action_guarantees:
            return frozenset({(0, 0)})
        answer = action_guarantees[0]
        for action in action_guarantees[1:]:
            answer = intersect_downsets(answer, action)
        return answer

    initial = guarantees((0,) * 8, 0, (4,) * len(groups), True)
    return initial, states


def query_axis(index):
    return 0 if index < 12 else 1


def projected_exposures(root):
    leaves = []

    def walk(node, exposure):
        if node.query_index is None:
            leaves.append(exposure)
            return
        next_exposure = list(exposure)
        next_exposure[query_axis(node.query_index)] += 1
        for _, child in node.children:
            walk(child, tuple(next_exposure))

    walk(root, (0, 0))
    return tuple(sorted(set(leaves)))


def predicted(x, y):
    values = tuple(p * x + q * y for p, q in FACES)
    return max(values), tuple(face for face, value in zip(FACES, values) if value == max(values))


def solve(x, y):
    bound, active = predicted(x, y)
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(),
        qary_prefix_query_library(2, 3, copies=4),
        query_costs=qary_prefix_query_costs(2, 3, copies=4, level_costs=(x, x, y)),
        corruption_budget=1,
        erasure_budget=1,
        allowed_initial_query_indices=range(4, 12),
        known_feasible_cost_upper_bound=bound,
    )
    return plan, bound, active


def cone_certificate(cone):
    x, y = cone["synthesis_point"]
    plan, bound, active = solve(x, y)
    exposures = projected_exposures(plan.root)
    inequalities = []
    for ray in cone["rays"]:
        face_cost = sum(a * b for a, b in zip(cone["face"], ray))
        worst = max(sum(a * b for a, b in zip(vector, ray)) for vector in exposures)
        inequalities.append({"ray": list(ray), "face_cost": face_cost, "policy_cost": worst, "passed": worst <= face_cost})
    return {
        "face": list(cone["face"]),
        "synthesis_point": [x, y],
        "exact_cost": plan.worst_case_cost,
        "predicted_cost": bound,
        "active_faces": [list(face) for face in active],
        "unique_projected_exposures": [list(vector) for vector in exposures],
        "extreme_ray_inequalities": inequalities,
        "passed": plan.worst_case_cost == bound and cone["face"] in active and all(item["passed"] for item in inequalities),
    }


def main():
    guarantees, states = projected_guarantees(problem())
    lower_faces_present = all(face in guarantees for face in FACES)
    cones = [cone_certificate(cone) for cone in CONES]
    holdouts = []
    for x, y in HOLDOUTS:
        plan, bound, active = solve(x, y)
        holdouts.append({
            "symmetric_costs": [x, y],
            "level_costs": [x, x, y],
            "predicted_cost": bound,
            "exact_cost": plan.worst_case_cost,
            "active_faces": [list(face) for face in active],
            "matched": plan.worst_case_cost == bound,
        })
    summary = {
        "guarantee_states_checked": states,
        "projected_guarantees": [list(vector) for vector in sorted(guarantees)],
        "all_lower_faces_present": lower_faces_present,
        "upper_cones_certified": sum(item["passed"] for item in cones),
        "holdout_matches": sum(item["matched"] for item in holdouts),
        "holdout_total": len(holdouts),
        "boundary_ties": {
            "x_equals_y": [list(face) for face in predicted(1, 1)[1]],
            "x_equals_2y": [list(face) for face in predicted(2, 1)[1]],
        },
    }
    summary["passed"] = (
        lower_faces_present
        and summary["upper_cones_certified"] == 3
        and summary["holdout_matches"] == summary["holdout_total"] == 7
        and len(summary["boundary_ties"]["x_equals_y"]) == 2
        and len(summary["boundary_ties"]["x_equals_2y"]) == 2
    )
    result = {
        "schema": "theorica.middle-first-symmetric-slice/1",
        "theorem": "S(x,y)=max(7x+y,6x+3y,5x+4y) for binary middle-first costs (x,x,y)",
        "lower_bound": {
            "maximal_projected_componentwise_guarantees": summary["projected_guarantees"],
            "states_checked": states,
        },
        "upper_bound_cones": cones,
        "holdouts": holdouts,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
