#!/usr/bin/env python3
"""Falsify the frozen componentwise middle-first proof obligation."""

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

OUT = Path("results/qary_three_level_middle_first_proof/results.json")
FACES = (
    (1, 5, 1),
    (2, 3, 4),
    (2, 4, 3),
    (3, 3, 3),
    (3, 4, 1),
    (4, 2, 1),
)
TARGET = (3, 4, 1)
WITNESS_COSTS = (79, 79, 1)


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
            row = tuple(
                word[level] if word[:level] == prefix else 0 for word in words
            )
            groups.append((row, level, 4))
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


def child_states(groups, alphabets, counts, erased, remaining, group):
    row, _, _ = groups[group]
    next_remaining = tuple(
        count - (index == group) for index, count in enumerate(remaining)
    )
    children = []
    for answer in alphabets[group]:
        child = tuple(
            min(2, count + (row[index] != answer))
            for index, count in enumerate(counts)
        )
        if any(count <= 1 for count in child):
            children.append((child, erased, next_remaining))
    if erased < 1:
        children.append((counts, erased + 1, next_remaining))
    return tuple(children)


def componentwise_guarantees(groups):
    alphabets = tuple(tuple(sorted(set(row))) for row, _, _ in groups)
    states = 0

    @cache
    def guarantees(counts, erased, remaining, initial):
        nonlocal states
        states += 1
        feasible = tuple(index for index, count in enumerate(counts) if count <= 1)
        if len(feasible) <= 1:
            return frozenset({(0, 0, 0)})
        action_guarantees = []
        for group, count in enumerate(remaining):
            if count == 0 or (initial and group not in (1, 2)):
                continue
            row, level, _ = groups[group]
            if len({row[index] for index in feasible}) < 2:
                continue
            union = set()
            for child in child_states(
                groups, alphabets, counts, erased, remaining, group
            ):
                union.update(
                    tuple(value + (axis == level) for axis, value in enumerate(vector))
                    for vector in guarantees(*child, False)
                )
            action_guarantees.append(maximal(union))
        if not action_guarantees:
            return frozenset({(0, 0, 0)})
        answer = action_guarantees[0]
        for action in action_guarantees[1:]:
            answer = intersect_downsets(answer, action)
        return answer

    initial = guarantees((0,) * 8, 0, (4,) * len(groups), True)
    return initial, states


def avoidance_policy(groups, target):
    alphabets = tuple(tuple(sorted(set(row))) for row, _, _ in groups)
    choices = {}

    @cache
    def solve(counts, erased, remaining, capped_exposure, initial):
        if all(left >= right for left, right in zip(capped_exposure, target)):
            return False
        feasible = tuple(index for index, count in enumerate(counts) if count <= 1)
        if len(feasible) <= 1:
            return True
        for group, count in enumerate(remaining):
            if count == 0 or (initial and group not in (1, 2)):
                continue
            row, level, _ = groups[group]
            if len({row[index] for index in feasible}) < 2:
                continue
            next_exposure = list(capped_exposure)
            next_exposure[level] = min(target[level], next_exposure[level] + 1)
            next_exposure = tuple(next_exposure)
            children = child_states(
                groups, alphabets, counts, erased, remaining, group
            )
            if children and all(
                solve(*child, next_exposure, False) for child in children
            ):
                choices[(counts, erased, remaining, capped_exposure, initial)] = group
                return True
        return False

    initial_counts = (0,) * 8
    initial_remaining = (4,) * len(groups)
    exists = solve(initial_counts, 0, initial_remaining, (0, 0, 0), True)
    leaves = []

    def walk(counts, erased, remaining, capped_exposure, exposure, initial):
        feasible = tuple(index for index, count in enumerate(counts) if count <= 1)
        if len(feasible) <= 1:
            leaves.append(exposure)
            return
        key = (counts, erased, remaining, capped_exposure, initial)
        group = choices[key]
        level = groups[group][1]
        next_capped = list(capped_exposure)
        next_capped[level] = min(target[level], next_capped[level] + 1)
        next_exposure = list(exposure)
        next_exposure[level] += 1
        for child in child_states(
            groups, alphabets, counts, erased, remaining, group
        ):
            walk(
                *child,
                tuple(next_capped),
                tuple(next_exposure),
                False,
            )

    if exists:
        walk(
            initial_counts,
            0,
            initial_remaining,
            (0, 0, 0),
            (0, 0, 0),
            True,
        )
    return {
        "exists": exists,
        "states_checked": solve.cache_info().misses,
        "terminal_transcripts": len(leaves),
        "unique_exposures": len(set(leaves)),
        "maximal_exposures": [list(vector) for vector in sorted(maximal(leaves))],
        "target_dominated": any(
            all(left >= right for left, right in zip(vector, target))
            for vector in leaves
        ),
    }


def games():
    return tuple(
        (
            (1 - (p := Fraction(index + 1, 9)), p - 1),
            (-p, p),
        )
        for index in range(8)
    )


def main():
    groups = problem()
    guaranteed, guarantee_states = componentwise_guarantees(groups)
    avoidance = avoidance_policy(groups, TARGET)
    target_cost = sum(x * y for x, y in zip(TARGET, WITNESS_COSTS))
    avoidance_worst_cost = max(
        sum(x * y for x, y in zip(vector, WITNESS_COSTS))
        for vector in avoidance["maximal_exposures"]
    )
    exact = plan_adaptive_decision_queries_with_weighted_faults(
        games(),
        qary_prefix_query_library(2, 3, copies=4),
        query_costs=qary_prefix_query_costs(
            2, 3, copies=4, level_costs=WITNESS_COSTS
        ),
        corruption_budget=1,
        erasure_budget=1,
        allowed_initial_query_indices=range(4, 12),
        known_feasible_cost_upper_bound=target_cost,
    )
    missing = [list(face) for face in FACES if face not in guaranteed]
    result = {
        "schema": "theorica.middle-first-componentwise-falsification/1",
        "target_faces": [list(face) for face in FACES],
        "maximal_componentwise_guarantees": [
            list(vector) for vector in sorted(guaranteed)
        ],
        "guarantee_states_checked": guarantee_states,
        "missing_target_faces": missing,
        "avoidance_policy": avoidance,
        "witness_costs": list(WITNESS_COSTS),
        "target_face_cost": target_cost,
        "avoidance_policy_worst_cost": avoidance_worst_cost,
        "production_exact_cost": exact.worst_case_cost,
    }
    result["passed"] = (
        missing == [list(TARGET)]
        and avoidance["exists"]
        and not avoidance["target_dominated"]
        and avoidance_worst_cost == target_cost == exact.worst_case_cost == 554
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
