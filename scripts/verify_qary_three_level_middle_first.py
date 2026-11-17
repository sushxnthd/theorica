#!/usr/bin/env python3
"""Open the frozen prospective middle-first conditioned-law holdouts."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_binary_three_level_middle_first,
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_three_level_middle_first/results.json")
FACES = (
    (1, 5, 1),
    (2, 3, 4),
    (2, 4, 3),
    (3, 3, 3),
    (3, 4, 1),
    (4, 2, 1),
)
HOLDOUTS = (
    ((1, 79, 1), FACES[0], 397, 76, "high_ratio"),
    ((1, 1, 79), FACES[1], 321, 78, "high_ratio"),
    ((1, 79, 53), FACES[2], 477, 26, "high_ratio"),
    ((79, 1, 53), FACES[3], 399, 26, "high_ratio"),
    ((79, 79, 1), FACES[4], 554, 77, "high_ratio"),
    ((79, 1, 1), FACES[5], 319, 76, "high_ratio"),
    ((59, 30, 1), FACES[4], 298, 1, "phase_boundary"),
    ((59, 29, 1), FACES[5], 295, 1, "phase_boundary"),
    ((59, 1, 58), FACES[3], 354, 1, "phase_boundary"),
    ((58, 1, 59), FACES[1], 355, 1, "phase_boundary"),
    ((29, 59, 1), FACES[0], 325, 1, "phase_boundary"),
    ((1, 59, 58), FACES[2], 412, 1, "phase_boundary"),
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
    costs, predicted_face, predicted_cost, predicted_margin, family = frozen
    certificate = certify_binary_three_level_middle_first(*costs)
    values = tuple(face_cost(face, costs) for face in FACES)
    best = max(values)
    ordered = sorted(values, reverse=True)
    active = tuple(face for face, value in zip(FACES, values) if value == best)
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
        allowed_initial_query_indices=range(4, 12),
        known_feasible_cost_upper_bound=predicted_cost,
    )
    first_index = None if plan.root is None else plan.root.query_index
    margin = ordered[0] - ordered[1]
    return {
        "family": family,
        "level_costs": list(costs),
        "predicted_face": list(predicted_face),
        "active_faces": [list(face) for face in active],
        "predicted_cost": predicted_cost,
        "certificate_cost": certificate.exact_worst_case_cost,
        "exact_middle_first_cost": plan.worst_case_cost,
        "predicted_margin": predicted_margin,
        "computed_margin": margin,
        "first_query_index": first_index,
        "first_query_is_middle": first_index is not None and 4 <= first_index < 12,
        "states_solved": plan.states_solved,
        "compatibility_states_solved": plan.compatibility_states_solved,
        "matched": (
            active == (predicted_face,)
            and best == predicted_cost == certificate.exact_worst_case_cost
            and margin == predicted_margin
            and plan.worst_case_cost == predicted_cost
            and first_index is not None
            and 4 <= first_index < 12
            and certificate.policy_class == "binary_middle_first"
        ),
    }


def main():
    holdouts = [exact_case(frozen) for frozen in HOLDOUTS]
    summary = {
        "holdout_total": len(holdouts),
        "holdout_matches": sum(item["matched"] for item in holdouts),
        "high_ratio_matches": sum(
            item["matched"] and item["family"] == "high_ratio" for item in holdouts
        ),
        "phase_boundary_matches": sum(
            item["matched"] and item["family"] == "phase_boundary"
            for item in holdouts
        ),
        "unique_faces_covered": len(
            {tuple(item["active_faces"][0]) for item in holdouts if item["matched"]}
        ),
        "minimum_phase_margin": min(item["computed_margin"] for item in holdouts),
    }
    summary["passed"] = (
        summary["holdout_matches"] == summary["holdout_total"] == 12
        and summary["high_ratio_matches"] == 6
        and summary["phase_boundary_matches"] == 6
        and summary["unique_faces_covered"] == 6
        and summary["minimum_phase_margin"] == 1
    )
    result = {
        "schema": "theorica.qary-three-level-middle-first/1",
        "claim": "prospective binary middle-first six-face candidate",
        "holdouts": holdouts,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
