#!/usr/bin/env python3
"""Synthesize universal upper policies for all positive level costs."""

from __future__ import annotations

import argparse
import json
from functools import cache
from itertools import combinations
from math import gcd
from pathlib import Path

from verify_qary_three_level_middle_first_all_ratios import FACES
from verify_qary_three_level_middle_first_symmetric import games, problem

from theorica.agents.corruption_resilient_features import (
    certify_common_robust_plan,
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_three_level_middle_first_exact_all_ratios/results.json")
PROSPECTIVE = (
    (1, 7, 3), (3, 8, 5), (4, 7, 6), (5, 8, 11),
    (7, 5, 9), (8, 3, 5), (11, 4, 7), (13, 9, 2),
    (17, 6, 19), (19, 17, 23), (23, 11, 29), (29, 31, 7),
)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def primitive(vector):
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(value))
    return tuple(value // divisor for value in vector)


def face_constraints(face):
    return (
        (1, 0, 0), (0, 1, 0), (0, 0, 1),
        *(tuple(a - b for a, b in zip(face, other)) for other in FACES if other != face),
    )


def extreme_rays(face):
    constraints = face_constraints(face)
    rays = set()
    for left, right in combinations(constraints, 2):
        candidate = cross(left, right)
        for ray in (candidate, tuple(-value for value in candidate)):
            if ray != (0, 0, 0) and all(dot(row, ray) >= 0 for row in constraints):
                rays.add(primitive(ray))
    return tuple(sorted(rays))


def synthesize_face(face_index, ray_indices=None):
    face = FACES[face_index]
    all_rays = extreme_rays(face)
    rays = all_rays if ray_indices is None else tuple(all_rays[index] for index in ray_indices)
    limits = tuple(dot(face, ray) for ray in rays)
    groups = problem()
    exact_games = games()
    alphabets = tuple(tuple(sorted(set(row))) for row, _, _ in groups)
    choices = {}
    states = 0

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
    def feasible(counts, erased, remaining, budgets, initial):
        nonlocal states
        states += 1
        indices = live(counts)
        if terminal(indices):
            return True
        for group, count in enumerate(remaining):
            if count == 0 or (initial and group not in (1, 2)):
                continue
            row, _, _ = groups[group]
            if len({row[index] for index in indices}) < 2:
                continue
            level = 0 if group == 0 else (1 if group < 3 else 2)
            costs = tuple(ray[level] for ray in rays)
            if any(cost > budget for cost, budget in zip(costs, budgets)):
                continue
            next_budgets = tuple(budget - cost for budget, cost in zip(budgets, costs))
            descendants = children(counts, erased, remaining, group)
            if descendants and all(
                feasible(*child, next_budgets, False) for child in descendants
            ):
                choices[(counts, erased, remaining, budgets, initial)] = group
                return True
        return False

    initial = ((0,) * 8, 0, (4,) * len(groups), limits, True)
    if not feasible(*initial):
        return {
            "face_index": face_index,
            "ray_indices": None if ray_indices is None else list(ray_indices),
            "face": list(face),
            "extreme_rays": [list(ray) for ray in rays],
            "budgets": list(limits),
            "states_solved": states,
            "feasible": False,
        }

    exposures = []

    def walk(counts, erased, remaining, budgets, initial_state, exposure):
        indices = live(counts)
        if terminal(indices):
            exposures.append(exposure)
            return
        group = choices[(counts, erased, remaining, budgets, initial_state)]
        level = 0 if group == 0 else (1 if group < 3 else 2)
        costs = tuple(ray[level] for ray in rays)
        next_budgets = tuple(budget - cost for budget, cost in zip(budgets, costs))
        next_exposure = list(exposure)
        next_exposure[level] += 1
        for child in children(counts, erased, remaining, group):
            walk(*child, next_budgets, False, tuple(next_exposure))

    walk(*initial, (0, 0, 0))
    unique = tuple(sorted(set(exposures)))
    ray_margins = [
        {
            "ray": list(ray),
            "minimum_margin": min(dot(face, ray) - dot(exposure, ray) for exposure in unique),
        }
        for ray in rays
    ]
    return {
        "face_index": face_index,
        "ray_indices": None if ray_indices is None else list(ray_indices),
        "face": list(face),
        "extreme_rays": [list(ray) for ray in rays],
        "budgets": list(limits),
        "states_solved": states,
        "terminal_transcripts": len(exposures),
        "unique_terminal_exposures": [list(item) for item in unique],
        "ray_margins": ray_margins,
        "feasible": all(row["minimum_margin"] >= 0 for row in ray_margins),
    }


def exact_case(costs):
    predicted = max(dot(face, costs) for face in FACES)
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(),
        qary_prefix_query_library(2, 3, copies=4),
        query_costs=qary_prefix_query_costs(2, 3, copies=4, level_costs=costs),
        corruption_budget=1,
        erasure_budget=1,
        allowed_initial_query_indices=range(4, 12),
        known_feasible_cost_upper_bound=predicted,
    )
    return {
        "level_costs": list(costs),
        "predicted_cost": predicted,
        "exact_cost": plan.worst_case_cost,
        "matched": plan.worst_case_cost == predicted,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect-falsification", action="store_true")
    arguments = parser.parse_args()
    certificates = [synthesize_face(index) for index in range(len(FACES))]
    problem_face_triples = [
        synthesize_face(4, ray_indices)
        for ray_indices in combinations(range(len(extreme_rays(FACES[4]))), 3)
    ]
    holdouts = [exact_case(costs) for costs in PROSPECTIVE]
    summary = {
        "face_certificates_passed": sum(row["feasible"] for row in certificates),
        "face_certificate_total": len(certificates),
        "extreme_ray_total": sum(len(row["extreme_rays"]) for row in certificates),
        "terminal_transcript_total": sum(row.get("terminal_transcripts", 0) for row in certificates),
        "problem_face_three_ray_subsets_feasible": sum(
            row["feasible"] for row in problem_face_triples
        ),
        "problem_face_three_ray_subset_total": len(problem_face_triples),
        "prospective_holdouts_matched": sum(row["matched"] for row in holdouts),
        "prospective_holdout_total": len(holdouts),
    }
    summary["passed"] = (
        summary["face_certificates_passed"] == summary["face_certificate_total"] == 6
        and summary["prospective_holdouts_matched"] == summary["prospective_holdout_total"] == 12
    )
    result = {
        "schema": "theorica.middle-first-exact-all-positive-costs/1",
        "candidate_faces": [list(face) for face in FACES],
        "face_cone_policy_certificates": certificates,
        "problem_face_three_ray_subset_search": problem_face_triples,
        "prospective_exact_holdouts": holdouts,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    expected_falsification = (
        summary["face_certificates_passed"] == 5
        and not certificates[4]["feasible"]
        and summary["problem_face_three_ray_subsets_feasible"] == 2
        and summary["problem_face_three_ray_subset_total"] == 10
        and summary["prospective_holdouts_matched"] == summary["prospective_holdout_total"] == 12
    )
    if arguments.expect_falsification and not expected_falsification:
        raise SystemExit("frozen falsification signature changed")
    if not arguments.expect_falsification and not summary["passed"]:
        raise SystemExit("exact all-positive-cost protocol failed")


if __name__ == "__main__":
    main()
