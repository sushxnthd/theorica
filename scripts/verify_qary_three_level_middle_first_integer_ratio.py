"""Prove the frozen integer-ratio middle-first family."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

from verify_qary_three_level_middle_first_symmetric import games, problem

from theorica.agents.corruption_resilient_features import (
    certify_common_robust_plan,
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_three_level_middle_first_integer_ratio/results.json")
FROZEN_RATIOS = (3, 4, 7, 11)
BREAKPOINT_RATIOS = tuple(range(2, 10))


def faces(orientation, k):
    if orientation == "root":
        return ((4 * k + 2, 1), (3 * k + 3, 3), (2 * k + 3, 4))
    return ((5 * k + 1, 1), (4 * k + 2, 3), (3 * k + 2, 4))


def weights(orientation, k):
    return (k, 1) if orientation == "root" else (1, k)


def projected(vector, orientation, k):
    root, middle, leaf = vector
    first = k * root + middle if orientation == "root" else root + k * middle
    return first, leaf


def symbolic_projected_guarantees(orientation, k):
    """Run the exact recursion while retaining the affine exposure source."""
    groups = problem()
    alphabets = tuple(tuple(sorted(set(row))) for row, _, _ in groups)
    states = 0

    def maximal(vectors):
        representatives = {}
        for vector in vectors:
            representatives.setdefault(projected(vector, orientation, k), vector)
        values = tuple(representatives.values())
        return frozenset(
            vector
            for vector in values
            if not any(
                projected(vector, orientation, k) != projected(other, orientation, k)
                and all(
                    left <= right
                    for left, right in zip(
                        projected(vector, orientation, k),
                        projected(other, orientation, k),
                    )
                )
                for other in values
            )
        )

    def intersect(left, right):
        candidates = []
        for first in left:
            for second in right:
                first_p = projected(first, orientation, k)[0]
                second_p = projected(second, orientation, k)[0]
                source = first if first_p <= second_p else second
                candidates.append((source[0], source[1], min(first[2], second[2])))
        return maximal(candidates)

    def children(counts, erased, remaining, group):
        row, _, _ = groups[group]
        rest = tuple(count - (index == group) for index, count in enumerate(remaining))
        answer = []
        for observed in alphabets[group]:
            child = tuple(min(2, count + (row[index] != observed)) for index, count in enumerate(counts))
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
            return frozenset({(0, 0, 0)})
        actions = []
        for group, count in enumerate(remaining):
            if count == 0 or (initial and group not in (1, 2)):
                continue
            row, _, _ = groups[group]
            if len({row[index] for index in live}) < 2:
                continue
            increment = (1, 0, 0) if group == 0 else ((0, 1, 0) if group < 3 else (0, 0, 1))
            union = set()
            for child in children(counts, erased, remaining, group):
                union.update(tuple(a + b for a, b in zip(vector, increment)) for vector in force(*child, False))
            actions.append(maximal(union))
        if not actions:
            return frozenset({(0, 0, 0)})
        answer = actions[0]
        for action in actions[1:]:
            answer = intersect(answer, action)
        return answer

    return force((0,) * 8, 0, (4,) * len(groups), True), states


def rays(cone, k):
    return (
        ((1, 0), (2, k - 1)),
        ((2, k - 1), (1, k)),
        ((0, 1), (1, k)),
    )[cone]


def synthesize_universal_policy(orientation, cone):
    """Synthesize at k=2, then certify every affine margin for k>=2."""
    k = 2
    groups = problem()
    alphabets = tuple(tuple(sorted(set(row))) for row, _, _ in groups)
    exact_games = games()
    target = faces(orientation, k)[cone]
    cone_rays = rays(cone, k)
    limits = tuple(sum(a * b for a, b in zip(target, ray)) for ray in cone_rays)
    choices = {}

    def live(counts):
        return tuple(index for index, count in enumerate(counts) if count <= 1)

    @cache
    def terminal(indices):
        return certify_common_robust_plan(tuple(exact_games[index] for index in indices)).policy_identifiable

    def children(counts, erased, remaining, group):
        row, _, _ = groups[group]
        rest = tuple(count - (index == group) for index, count in enumerate(remaining))
        answer = []
        for observed in alphabets[group]:
            child = tuple(min(2, count + (row[index] != observed)) for index, count in enumerate(counts))
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
        for group, count in enumerate(remaining):
            if count == 0 or (initial and group not in (1, 2)):
                continue
            row, _, _ = groups[group]
            if len({row[index] for index in indices}) < 2:
                continue
            level = 0 if group == 0 else (1 if group < 3 else 2)
            increment = weights(orientation, 2)[level] if level < 2 else 0
            projected_increment = (increment, int(level == 2))
            costs = tuple(sum(a * b for a, b in zip(projected_increment, ray)) for ray in cone_rays)
            if costs[0] > left or costs[1] > right:
                continue
            descendants = children(counts, erased, remaining, group)
            if descendants and all(feasible(*child, left - costs[0], right - costs[1], False) for child in descendants):
                choices[(counts, erased, remaining, left, right, initial)] = group
                return True
        return False

    initial = ((0,) * 8, 0, (4,) * len(groups), limits[0], limits[1], True)
    if not feasible(*initial):
        raise RuntimeError("frozen ratio-two cone has no feasible policy")
    exposures = []

    def walk(counts, erased, remaining, left, right, initial_state, exposure):
        indices = live(counts)
        if terminal(indices):
            exposures.append(exposure)
            return
        group = choices[(counts, erased, remaining, left, right, initial_state)]
        level = 0 if group == 0 else (1 if group < 3 else 2)
        increment = weights(orientation, 2)[level] if level < 2 else 0
        projected_increment = (increment, int(level == 2))
        costs = tuple(sum(a * b for a, b in zip(projected_increment, ray)) for ray in cone_rays)
        next_exposure = list(exposure)
        next_exposure[level] += 1
        for child in children(counts, erased, remaining, group):
            walk(*child, left - costs[0], right - costs[1], False, tuple(next_exposure))

    walk(*initial, (0, 0, 0))
    unique = tuple(sorted(set(exposures)))
    inequalities = []
    for ray_index in range(2):
        margins = []
        for exposure in unique:
            values = []
            for ratio in (2, 3):
                ray = rays(cone, ratio)[ray_index]
                face = faces(orientation, ratio)[cone]
                point = projected(exposure, orientation, ratio)
                values.append(sum(a * b for a, b in zip(face, ray)) - sum(a * b for a, b in zip(point, ray)))
            slope = values[1] - values[0]
            intercept = values[0] - 2 * slope
            margins.append({"exposure": list(exposure), "slope": slope, "intercept": intercept, "value_at_k2": values[0]})
        inequalities.append({
            "ray_index": ray_index,
            "minimum_slope": min(item["slope"] for item in margins),
            "minimum_value_at_k2": min(item["value_at_k2"] for item in margins),
            "margins": margins,
            "passed": all(item["slope"] >= 0 and item["value_at_k2"] >= 0 for item in margins),
        })
    return {
        "cone": cone,
        "original_exposures": [list(item) for item in unique],
        "terminal_transcripts": len(exposures),
        "symbolic_inequalities": inequalities,
        "passed": all(item["passed"] for item in inequalities),
    }


def exact_holdout(orientation, k, x, y):
    candidate_faces = faces(orientation, k)
    bound = max(a * x + b * y for a, b in candidate_faces)
    level_costs = (k * x, x, y) if orientation == "root" else (x, k * x, y)
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(),
        qary_prefix_query_library(2, 3, copies=4),
        query_costs=qary_prefix_query_costs(2, 3, copies=4, level_costs=level_costs),
        corruption_budget=1,
        erasure_budget=1,
        allowed_initial_query_indices=range(4, 12),
        known_feasible_cost_upper_bound=bound,
    )
    return {
        "orientation": orientation,
        "k": k,
        "base_and_leaf_costs": [x, y],
        "level_costs": list(level_costs),
        "predicted_cost": bound,
        "exact_cost": plan.worst_case_cost,
        "matched": plan.worst_case_cost == bound,
    }


def main():
    breakpoint_records = []
    for orientation in ("root", "middle"):
        for k in BREAKPOINT_RATIOS:
            symbolic, states = symbolic_projected_guarantees(orientation, k)
            actual = {projected(vector, orientation, k) for vector in symbolic}
            breakpoint_records.append({
                "orientation": orientation,
                "k": k,
                "symbolic_antichain": [list(vector) for vector in sorted(symbolic)],
                "projected_antichain": [list(vector) for vector in sorted(actual)],
                "expected_antichain": [list(vector) for vector in sorted(faces(orientation, k))],
                "states_checked": states,
                "matched": actual == set(faces(orientation, k)),
            })
    stable_tail = {
        orientation: [list(vector) for vector in sorted(symbolic_projected_guarantees(orientation, 9)[0])]
        for orientation in ("root", "middle")
    }
    expected_tail = {
        "root": [[2, 3, 4], [3, 3, 3], [4, 2, 1]],
        "middle": [[1, 5, 1], [2, 3, 4], [2, 4, 3]],
    }
    universal_policies = {
        orientation: [synthesize_universal_policy(orientation, cone) for cone in range(3)]
        for orientation in ("root", "middle")
    }
    holdouts = []
    for k in FROZEN_RATIOS:
        cases = ((79, 1), (2, k - 1), (2, 2 * k - 1), (1, k), (1, 79 * k))
        for orientation in ("root", "middle"):
            holdouts.extend(exact_holdout(orientation, k, x, y) for x, y in cases)
    summary = {
        "breakpoint_antichains_matched": sum(item["matched"] for item in breakpoint_records),
        "breakpoint_antichain_total": len(breakpoint_records),
        "stable_tail_symbolic_sources_matched": stable_tail == expected_tail,
        "universal_cones_certified": sum(item["passed"] for rows in universal_policies.values() for item in rows),
        "holdout_matches": sum(item["matched"] for item in holdouts),
        "holdout_total": len(holdouts),
    }
    summary["passed"] = (
        summary["breakpoint_antichains_matched"] == summary["breakpoint_antichain_total"] == 16
        and summary["stable_tail_symbolic_sources_matched"]
        and summary["universal_cones_certified"] == 6
        and summary["holdout_matches"] == summary["holdout_total"] == 40
    )
    result = {
        "schema": "theorica.middle-first-integer-ratio-family/1",
        "breakpoint_lemma": {
            "root_query_copy_bound": 4,
            "middle_query_copy_bound": 8,
            "integer_ratios_checked": list(BREAKPOINT_RATIOS),
            "stable_for_integer_k_at_least": 9,
            "records": breakpoint_records,
            "stable_tail_symbolic_sources": stable_tail,
        },
        "universal_upper_policies": universal_policies,
        "prospective_holdouts": holdouts,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
