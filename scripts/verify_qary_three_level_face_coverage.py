#!/usr/bin/env python3
"""Open the frozen large-ratio six-face coverage holdouts."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_qary_three_level_insurance,
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_three_level_face_coverage/results.json")
HOLDOUTS = (
    ((1, 1, 40), (2, 2, 4), 164, 39),
    ((1, 40, 21), (2, 3, 3), 185, 2),
    ((1, 40, 1), (2, 4, 1), 163, 38),
    ((40, 1, 20), (3, 2, 3), 182, 1),
    ((40, 21, 1), (3, 3, 1), 184, 2),
    ((40, 1, 1), (4, 1, 1), 162, 37),
)
FACES = (
    (2, 2, 4),
    (2, 3, 3),
    (2, 4, 1),
    (3, 2, 3),
    (3, 3, 1),
    (4, 1, 1),
)


def games():
    return tuple(
        (
            (1 - (p := Fraction(index + 1, 9)), p - 1),
            (-p, p),
        )
        for index in range(8)
    )


def face_cost(face, costs):
    return sum(coefficient * cost for coefficient, cost in zip(face, costs))


def exact_case(frozen):
    costs, predicted_face, predicted_cost, predicted_margin = frozen
    certificate = certify_qary_three_level_insurance(2, *costs)
    face_values = tuple(face_cost(face, costs) for face in FACES)
    best = max(face_values)
    runners_up = sorted(face_values, reverse=True)
    active = tuple(face for face, value in zip(FACES, face_values) if value == best)
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(),
        qary_prefix_query_library(2, 3, copies=4),
        query_costs=qary_prefix_query_costs(
            2,
            3,
            copies=4,
            level_costs=costs,
        ),
        corruption_budget=1,
        erasure_budget=1,
        known_feasible_cost_upper_bound=certificate.exact_worst_case_cost,
    )
    margin = runners_up[0] - runners_up[1]
    return {
        "level_costs": list(costs),
        "predicted_face": list(predicted_face),
        "active_faces": [list(face) for face in active],
        "predicted_cost": predicted_cost,
        "six_face_cost": certificate.exact_worst_case_cost,
        "exact_unrestricted_binary_cost": plan.worst_case_cost,
        "predicted_margin": predicted_margin,
        "computed_margin": margin,
        "states_solved": plan.states_solved,
        "compatibility_states_solved": plan.compatibility_states_solved,
        "matched": (
            active == (predicted_face,)
            and best == predicted_cost == certificate.exact_worst_case_cost
            and margin == predicted_margin
            and plan.worst_case_cost == predicted_cost
        ),
    }


def missing_copy_attack():
    costs = (40, 1, 20)
    outcomes = qary_prefix_query_library(2, 3, copies=4)[:-1]
    query_costs = qary_prefix_query_costs(
        2,
        3,
        copies=4,
        level_costs=costs,
    )[:-1]
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(),
        outcomes,
        query_costs=query_costs,
        corruption_budget=1,
        erasure_budget=1,
    )
    return {
        "level_costs": list(costs),
        "remaining_query_instances": len(outcomes),
        "exact_cost": plan.worst_case_cost,
        "abstained": plan.root is None and plan.worst_case_cost is None,
    }


def main():
    holdouts = [exact_case(frozen) for frozen in HOLDOUTS]
    attack = missing_copy_attack()
    summary = {
        "holdout_total": len(holdouts),
        "holdout_matches": sum(item["matched"] for item in holdouts),
        "unique_faces_covered": len(
            {tuple(item["active_faces"][0]) for item in holdouts if item["matched"]}
        ),
        "minimum_phase_margin": min(item["computed_margin"] for item in holdouts),
        "maximum_cost_ratio": max(
            max(item["level_costs"]) / min(item["level_costs"])
            for item in holdouts
        ),
        "missing_copy_abstained": attack["abstained"],
    }
    summary["passed"] = (
        summary["holdout_matches"] == summary["holdout_total"] == 6
        and summary["unique_faces_covered"] == 6
        and summary["minimum_phase_margin"] == 1
        and summary["maximum_cost_ratio"] == 40
        and summary["missing_copy_abstained"]
    )
    result = {
        "schema": "theorica.qary-three-level-face-coverage/1",
        "claim": "all six corrected faces survive ancestor bypass on the frozen holdouts",
        "holdouts": holdouts,
        "missing_copy_attack": attack,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
