#!/usr/bin/env python3
"""Prove the exact ternary equal-level-cost middle-first slice."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_ternary_middle_first_symmetric,
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_three_level_middle_first_ternary_symmetric/results.json")
ARITY = 3


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
    certificate = certify_ternary_middle_first_symmetric(1)
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(),
        qary_prefix_query_library(ARITY, 3, copies=4),
        query_costs=qary_prefix_query_costs(
            ARITY, 3, copies=4, level_costs=(1, 1, 1)
        ),
        corruption_budget=1,
        erasure_budget=1,
        allowed_initial_query_indices=range(4, 16),
        known_feasible_cost_upper_bound=certificate.exact_worst_case_cost,
    )
    unique_exposures, transcript_count = exposures(plan.root)
    scales = (1, 2, 3, 5, 11, 29)
    result = {
        "schema": "theorica.middle-first-ternary-symmetric/1",
        "arity": ARITY,
        "completions": ARITY**3,
        "copies_per_prefix": 4,
        "corruption_budget": 1,
        "erasure_budget": 1,
        "exact_unit_cost": plan.worst_case_cost,
        "exact_worst_case_depth": plan.worst_case_depth,
        "states_solved": plan.states_solved,
        "compatibility_states_solved": plan.compatibility_states_solved,
        "unique_terminal_exposures": [list(row) for row in unique_exposures],
        "terminal_transcripts": transcript_count,
        "prospective_scales": [
            {
                "level_cost": scale,
                "predicted_exact_cost": 9 * scale,
                "homogeneous_from_unit_certificate": True,
            }
            for scale in scales
        ],
        "binary_embedding_lower_bound": 9,
        "certificate_api_cost": certificate.exact_worst_case_cost,
    }
    result["passed"] = (
        plan.certificate_valid
        and plan.worst_case_cost == plan.worst_case_depth == 9
        and max(sum(row) for row in unique_exposures) == 9
        and certificate.certificate_valid
        and certificate.exact_worst_case_cost == 9
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "exact_unit_cost": result["exact_unit_cost"],
        "states_solved": result["states_solved"],
        "terminal_transcripts": result["terminal_transcripts"],
        "passed": result["passed"],
    }, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
