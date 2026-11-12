#!/usr/bin/env python3
"""Prove the two frozen ratio-two middle-first slices exactly."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

from verify_qary_three_level_middle_first_symmetric import (
    games,
    intersect_downsets,
    maximal,
    problem,
)

from theorica.agents.corruption_resilient_features import (
    certify_common_robust_plan,
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_three_level_middle_first_ratio_two/results.json")
HOLDOUTS = ((79, 1), (81, 40), (41, 40), (40, 41), (40, 81), (1, 79), (2, 1), (1, 2))
SLICES = {
    "root_double": {"weights": (2, 1), "faces": ((10, 1), (9, 3), (7, 4))},
    "middle_double": {"weights": (1, 2), "faces": ((11, 1), (10, 3), (8, 4))},
}
CONES = (
    {"face_index": 0, "synthesis_point": (2, 1), "rays": ((1, 0), (2, 1))},
    {"face_index": 1, "synthesis_point": (2, 1), "rays": ((2, 1), (1, 2))},
    {"face_index": 2, "synthesis_point": (1, 2), "rays": ((0, 1), (1, 2))},
)


def increments(group, weights):
    return (weights[0], 0) if group == 0 else ((weights[1], 0) if group < 3 else (0, 1))


def projected_guarantees(weights):
    groups = problem()
    alphabets = tuple(tuple(sorted(set(row))) for row, _, _ in groups)
    states = 0

    def children(counts, erased, remaining, group):
        row, _, _ = groups[group]
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
    def force(counts, erased, remaining, initial):
        nonlocal states
        states += 1
        live = tuple(index for index, count in enumerate(counts) if count <= 1)
        if len(live) <= 1:
            return frozenset({(0, 0)})
        actions = []
        for group, count in enumerate(remaining):
            if count == 0 or (initial and group not in (1, 2)):
                continue
            row, _, _ = groups[group]
            if len({row[index] for index in live}) < 2:
                continue
            inc = increments(group, weights)
            union = set()
            for child in children(counts, erased, remaining, group):
                union.update(
                    (point[0] + inc[0], point[1] + inc[1])
                    for point in force(*child, False)
                )
            actions.append(maximal(union))
        if not actions:
            return frozenset({(0, 0)})
        answer = actions[0]
        for action in actions[1:]:
            answer = intersect_downsets(answer, action)
        return answer

    return force((0,) * 8, 0, (4,) * len(groups), True), states


def candidate(faces, x, y):
    values = tuple(a * x + b * y for a, b in faces)
    return max(values), tuple(
        face for face, value in zip(faces, values) if value == max(values)
    )


def level_costs(name, x, y):
    return (2 * x, x, y) if name == "root_double" else (x, 2 * x, y)


def solve(name, faces, x, y):
    bound, active = candidate(faces, x, y)
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(),
        qary_prefix_query_library(2, 3, copies=4),
        query_costs=qary_prefix_query_costs(
            2, 3, copies=4, level_costs=level_costs(name, x, y)
        ),
        corruption_budget=1,
        erasure_budget=1,
        allowed_initial_query_indices=range(4, 12),
        known_feasible_cost_upper_bound=bound,
    )
    return plan, bound, active


def synthesize_cone(weights, face, rays, synthesis_point):
    """Find one boundary-optimal tree satisfying both cone extreme rays."""
    groups = problem()
    alphabets = tuple(tuple(sorted(set(row))) for row, _, _ in groups)
    exact_games = games()
    limits = tuple(sum(a * b for a, b in zip(face, ray)) for ray in rays)
    choices = {}

    def live(counts):
        return tuple(index for index, count in enumerate(counts) if count <= 1)

    @cache
    def terminal(indices):
        return certify_common_robust_plan(
            tuple(exact_games[index] for index in indices)
        ).policy_identifiable

    def children(counts, erased, remaining, group):
        row, _, _ = groups[group]
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
    def feasible(counts, erased, remaining, left, right, initial):
        indices = live(counts)
        if terminal(indices):
            return True
        budgets = (left, right)
        for group, count in enumerate(remaining):
            if count == 0 or (initial and group not in (1, 2)):
                continue
            row, _, _ = groups[group]
            if len({row[index] for index in indices}) < 2:
                continue
            inc = increments(group, weights)
            costs = tuple(sum(a * b for a, b in zip(inc, ray)) for ray in rays)
            if any(cost > budget for cost, budget in zip(costs, budgets)):
                continue
            descendants = children(counts, erased, remaining, group)
            if descendants and all(
                feasible(*child, left - costs[0], right - costs[1], False)
                for child in descendants
            ):
                choices[(counts, erased, remaining, left, right, initial)] = group
                return True
        return False

    initial = ((0,) * 8, 0, (4,) * len(groups), limits[0], limits[1], True)
    passed = feasible(*initial)
    exposures = []

    def walk(counts, erased, remaining, left, right, initial_state, exposure):
        indices = live(counts)
        if terminal(indices):
            exposures.append(exposure)
            return
        group = choices[(counts, erased, remaining, left, right, initial_state)]
        inc = increments(group, weights)
        costs = tuple(sum(a * b for a, b in zip(inc, ray)) for ray in rays)
        for child in children(counts, erased, remaining, group):
            walk(
                *child,
                left - costs[0],
                right - costs[1],
                False,
                (exposure[0] + inc[0], exposure[1] + inc[1]),
            )

    if passed:
        walk(*initial, (0, 0))
    unique = tuple(sorted(set(exposures)))
    inequalities = []
    for ray, limit in zip(rays, limits):
        worst = max(sum(a * b for a, b in zip(point, ray)) for point in unique)
        inequalities.append(
            {
                "ray": list(ray),
                "policy_cost": worst,
                "face_cost": limit,
                "passed": worst <= limit,
            }
        )
    x, y = synthesis_point
    return {
        "face": list(face),
        "synthesis_point": [x, y],
        "projected_exposures": [list(point) for point in unique],
        "terminal_transcripts": len(exposures),
        "search_states": feasible.cache_info().misses,
        "extreme_ray_inequalities": inequalities,
        "passed": passed and all(item["passed"] for item in inequalities),
    }


def main():
    records = {}
    for name, specification in SLICES.items():
        weights = specification["weights"]
        faces = specification["faces"]
        guarantees, states = projected_guarantees(weights)
        cones = [
            synthesize_cone(
                weights,
                faces[item["face_index"]],
                item["rays"],
                item["synthesis_point"],
            )
            for item in CONES
        ]
        holdouts = []
        for x, y in HOLDOUTS:
            plan, bound, active = solve(name, faces, x, y)
            holdouts.append(
                {
                    "base_and_leaf_costs": [x, y],
                    "level_costs": list(level_costs(name, x, y)),
                    "predicted_cost": bound,
                    "exact_cost": plan.worst_case_cost,
                    "active_faces": [list(face) for face in active],
                    "matched": plan.worst_case_cost == bound,
                }
            )
        records[name] = {
            "weights": list(weights),
            "faces": [list(face) for face in faces],
            "maximal_projected_guarantees": [
                list(point) for point in sorted(guarantees)
            ],
            "guarantee_states_checked": states,
            "lower_bound_exact": guarantees == frozenset(faces),
            "upper_bound_cones": cones,
            "holdouts": holdouts,
            "passed": guarantees == frozenset(faces)
            and all(item["passed"] for item in cones)
            and all(item["matched"] for item in holdouts),
        }
    result = {
        "schema": "theorica.middle-first-ratio-two-slices/1",
        "theorems": {
            "root_double": "R(x,y)=max(10x+y,9x+3y,7x+4y)",
            "middle_double": "M(x,y)=max(11x+y,10x+3y,8x+4y)",
        },
        "slices": records,
        "summary": {
            "slices_proved": sum(item["passed"] for item in records.values()),
            "holdout_matches": sum(
                sum(case["matched"] for case in item["holdouts"])
                for item in records.values()
            ),
            "holdout_total": 16,
            "cones_certified": sum(
                sum(cone["passed"] for cone in item["upper_bound_cones"])
                for item in records.values()
            ),
        },
    }
    result["summary"]["passed"] = result["summary"] == {
        "slices_proved": 2,
        "holdout_matches": 16,
        "holdout_total": 16,
        "cones_certified": 6,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if result["summary"]["passed"] else 1)


if __name__ == "__main__":
    main()
