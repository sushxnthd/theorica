#!/usr/bin/env python3
"""Prospective exact check of the q-ary three-level insurance law."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_qary_three_level_insurance,
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_three_level_insurance/results.json")
HOLDOUTS = (
    (2, 1, 7, 2),
    (2, 7, 2, 1),
    (2, 2, 1, 7),
    (2, 3, 6, 2),
    (2, 6, 3, 2),
    (2, 2, 4, 5),
    (3, 2, 2, 2),
    (3, 1, 2, 3),
)


def games(arity):
    count = arity**3
    return tuple(
        (
            (1 - (p := Fraction(index + 1, count + 1)), p - 1),
            (-p, p),
        )
        for index in range(count)
    )


def run_case(arity, a, b, c):
    outcomes = qary_prefix_query_library(arity, 3, copies=4)
    costs = qary_prefix_query_costs(arity, 3, copies=4, level_costs=(a, b, c))
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(arity), outcomes, query_costs=costs,
        corruption_budget=1, erasure_budget=1,
    )
    theorem = certify_qary_three_level_insurance(arity, a, b, c)
    return {
        "arity": arity,
        "level_costs": [a, b, c],
        "completions": arity**3,
        "query_instances": len(outcomes),
        "adversary_lower_bounds": list(theorem.adversary_lower_bounds),
        "active_faces": list(theorem.active_faces),
        "formula_cost": theorem.exact_worst_case_cost,
        "exact_cost": plan.worst_case_cost,
        "exact_depth": plan.worst_case_depth,
        "states_solved": plan.states_solved,
        "certificate_valid": plan.certificate_valid,
        "formula_matched": plan.worst_case_cost == theorem.exact_worst_case_cost,
        "fixed_leaf_schedule_lower_bound": 4 * arity**2 * c,
    }


def missing_copy_attack():
    arity, costs = 2, (2, 1, 7)
    outcomes = qary_prefix_query_library(arity, 3, copies=4)[:-1]
    query_costs = qary_prefix_query_costs(
        arity, 3, copies=4, level_costs=costs
    )[:-1]
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(arity), outcomes, query_costs=query_costs,
        corruption_budget=1, erasure_budget=1,
    )
    return {
        "arity": arity,
        "level_costs": list(costs),
        "remaining_query_instances": len(outcomes),
        "exact_cost": plan.worst_case_cost,
        "reason": plan.reason,
        "abstained": plan.root is None and plan.worst_case_cost is None,
    }


def main():
    cases = [run_case(*parameters) for parameters in HOLDOUTS]
    attack = missing_copy_attack()
    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":"))
    summary = {
        "case_total": len(cases),
        "cases_completed": sum(item["certificate_valid"] for item in cases),
        "formula_matches": sum(item["formula_matched"] for item in cases),
        "arities_observed": sorted({item["arity"] for item in cases}),
        "active_faces_observed": sorted(
            {face for item in cases for face in item["active_faces"]}
        ),
        "missing_copy_abstained": attack["abstained"],
        "case_digest": hashlib.sha256(canonical.encode()).hexdigest(),
    }
    summary["passed"] = (
        summary["cases_completed"] == summary["case_total"]
        and summary["formula_matches"] == summary["case_total"]
        and summary["arities_observed"] == [2, 3]
        and len(summary["active_faces_observed"]) >= 4
        and summary["missing_copy_abstained"]
    )
    result = {
        "schema": "theorica.qary-three-level-insurance/1",
        "claim": "C_q(a,b,c)=max(4b+2c,2a+2b+4c,2a+3b+3c,2a+4b+c,3a+2b+3c,3a+3b+c,4a+b+c)",
        "pre_freeze_timeouts": [[3, 1, 5, 1], [3, 5, 1, 1]],
        "cases": cases,
        "missing_copy_attack": attack,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
