#!/usr/bin/env python3
"""Verify the frozen binary depth-three monotonicity correction."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_qary_three_level_insurance,
    certify_three_level_monotonicity,
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_three_level_monotonicity_correction/results.json")
HOLDOUTS = (
    (1, 20, 3),
    (1, 7, 3),
    (2, 17, 5),
    (3, 25, 7),
    (1, 6, 3),
    (2, 14, 5),
)


def games():
    return tuple(
        (
            (1 - (p := Fraction(index + 1, 9)), p - 1),
            (-p, p),
        )
        for index in range(8)
    )


def exact_case(costs):
    certificate = certify_qary_three_level_insurance(2, *costs)
    monotonicity = certify_three_level_monotonicity(2, *costs)
    outcomes = qary_prefix_query_library(2, 3, copies=4)
    query_costs = qary_prefix_query_costs(
        2, 3, copies=4, level_costs=costs
    )
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(),
        outcomes,
        query_costs=query_costs,
        corruption_budget=1,
        erasure_budget=1,
        known_feasible_cost_upper_bound=certificate.exact_worst_case_cost,
    )
    return {
        "level_costs": list(costs),
        "six_face_cost": certificate.exact_worst_case_cost,
        "exact_unrestricted_binary_cost": plan.worst_case_cost,
        "retired_seven_face_cost": max(
            certificate.exact_worst_case_cost,
            monotonicity.retired_bypass_face_cost,
        ),
        "retired_face_impossible": monotonicity.lower_face_impossible,
        "analytic_violation_cone": monotonicity.analytic_violation_cone,
        "states_solved": plan.states_solved,
        "matched": plan.worst_case_cost == certificate.exact_worst_case_cost,
    }


def missing_copy_attack():
    costs = (2, 1, 7)
    outcomes = qary_prefix_query_library(2, 3, copies=4)[:-1]
    query_costs = qary_prefix_query_costs(
        2, 3, copies=4, level_costs=costs
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
    holdouts = [exact_case(costs) for costs in HOLDOUTS]
    exhaustive = [exact_case(costs) for costs in product(range(1, 7), repeat=3)]
    attack = missing_copy_attack()
    canonical = json.dumps(exhaustive, sort_keys=True, separators=(",", ":"))
    summary = {
        "holdout_total": len(holdouts),
        "holdout_matches": sum(item["matched"] for item in holdouts),
        "strict_retired_counterexamples": sum(
            item["retired_seven_face_cost"] > item["exact_unrestricted_binary_cost"]
            for item in holdouts
        ),
        "exhaustive_total": len(exhaustive),
        "exhaustive_matches": sum(item["matched"] for item in exhaustive),
        "grid_retired_face_violations": sum(
            item["retired_face_impossible"] for item in exhaustive
        ),
        "analytic_cone_matches": sum(
            item["retired_face_impossible"] == item["analytic_violation_cone"]
            for item in exhaustive
        ),
        "missing_copy_abstained": attack["abstained"],
        "exhaustive_digest": hashlib.sha256(canonical.encode()).hexdigest(),
    }
    summary["passed"] = (
        summary["holdout_matches"] == summary["holdout_total"] == 6
        and summary["strict_retired_counterexamples"] >= 1
        and summary["exhaustive_matches"] == summary["exhaustive_total"] == 216
        and summary["analytic_cone_matches"] == summary["exhaustive_total"]
        and summary["missing_copy_abstained"]
    )
    result = {
        "schema": "theorica.qary-three-level-monotonicity-correction/1",
        "claim": "the retired (0,4,2) face is impossible exactly when c>2a and b>2a+c",
        "corrected_binary_conjecture": "six-face root-respecting maximum",
        "holdouts": holdouts,
        "exhaustive_binary_grid": exhaustive,
        "missing_copy_attack": attack,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
