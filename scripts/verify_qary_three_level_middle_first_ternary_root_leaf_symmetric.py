#!/usr/bin/env python3
"""Falsify the proposed ternary (x,y,x) law at its y=3x boundary."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path(
    "results/qary_three_level_middle_first_ternary_root_leaf_symmetric/results.json"
)
ARITY = 3
LEVEL_COSTS = (1, 3, 1)
CANDIDATE_FACES = ((2, 5), (5, 4), (6, 3))


def games():
    count = ARITY**3
    return tuple(
        (
            (1 - (p := Fraction(index + 1, count + 1)), p - 1),
            (-p, p),
        )
        for index in range(count)
    )


def exposures(root):
    rows = []

    def walk(node, counts):
        if node.query_index is None:
            rows.append(counts)
            return
        index = node.query_index
        level = 0 if index < 4 else (1 if index < 16 else 2)
        updated = list(counts)
        updated[level] += 1
        for _, child in node.children:
            walk(child, tuple(updated))

    walk(root, (0, 0, 0))
    return tuple(sorted(set(rows))), len(rows)


def main():
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(),
        qary_prefix_query_library(ARITY, 3, copies=4),
        query_costs=qary_prefix_query_costs(
            ARITY, 3, copies=4, level_costs=LEVEL_COSTS
        ),
        corruption_budget=1,
        erasure_budget=1,
        allowed_initial_query_indices=range(4, 16),
        known_feasible_cost_upper_bound=18,
    )
    rows, transcript_count = exposures(plan.root)
    candidate_values = tuple(a + 3 * b for a, b in CANDIDATE_FACES)
    weighted_exposures = tuple(r + 3 * m + l for r, m, l in rows)
    result = {
        "schema": "theorica.middle-first-ternary-root-leaf-symmetric-falsification/1",
        "falsified_claim": "T_3(x,y,x)=max(2x+5y,5x+4y,6x+3y)",
        "counterexample": {
            "level_costs": list(LEVEL_COSTS),
            "candidate_face_values": list(candidate_values),
            "candidate_value": max(candidate_values),
            "exact_value": plan.worst_case_cost,
            "strict_gap": plan.worst_case_cost - max(candidate_values),
        },
        "exact_worst_case_depth": plan.worst_case_depth,
        "states_solved": plan.states_solved,
        "compatibility_states_solved": plan.compatibility_states_solved,
        "terminal_transcripts": transcript_count,
        "unique_terminal_exposures": [list(row) for row in rows],
        "maximum_weighted_exposure": max(weighted_exposures),
        "failed_cone_ray": {
            "ray": [1, 3],
            "faces": [[2, 5], [5, 4]],
            "required_budget": 17,
            "exact_minimax_cost": plan.worst_case_cost,
        },
        "prospective_holdouts_run": 0,
        "prospective_holdouts_skipped_reason": (
            "The preregistered candidate was falsified at the first shared boundary ray."
        ),
    }
    result["passed"] = (
        plan.certificate_valid
        and result["counterexample"]["candidate_value"] == 17
        and result["counterexample"]["exact_value"] == 18
        and result["counterexample"]["strict_gap"] == 1
        and result["maximum_weighted_exposure"] == 18
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_value": result["counterexample"]["candidate_value"],
        "exact_value": result["counterexample"]["exact_value"],
        "states_solved": result["states_solved"],
        "terminal_transcripts": result["terminal_transcripts"],
        "passed": result["passed"],
    }, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
