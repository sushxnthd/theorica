#!/usr/bin/env python3
"""Prospective exact check of the q-ary two-level insurance law."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_qary_two_level_insurance,
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_two_level_insurance/results.json")
OPENED = ((2, 1, 1), (2, 1, 3), (2, 3, 1))
PROSPECTIVE = ((3, 2, 7), (4, 5, 3), (5, 9, 4), (3, 6, 6), (4, 8, 4))


def games(arity):
    count = arity**2
    return tuple(
        (
            (1 - (p := Fraction(index + 1, count + 1)), p - 1),
            (-p, p),
        )
        for index in range(count)
    )


def run_case(arity, root_cost, child_cost, role):
    outcomes = qary_prefix_query_library(arity, 2, copies=4)
    costs = qary_prefix_query_costs(
        arity,
        2,
        copies=4,
        level_costs=(root_cost, child_cost),
    )
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(arity),
        outcomes,
        query_costs=costs,
        corruption_budget=1,
        erasure_budget=1,
    )
    theorem = certify_qary_two_level_insurance(arity, root_cost, child_cost)
    return {
        "role": role,
        "arity": arity,
        "root_cost": root_cost,
        "child_cost": child_cost,
        "completions": arity**2,
        "query_instances": len(outcomes),
        "adversary_lower_bounds": list(theorem.adversary_lower_bounds),
        "active_regime": theorem.active_regime,
        "formula_cost": theorem.exact_worst_case_cost,
        "exact_cost": plan.worst_case_cost,
        "exact_depth": plan.worst_case_depth,
        "states_solved": plan.states_solved,
        "certificate_valid": plan.certificate_valid,
        "formula_matched": plan.worst_case_cost == theorem.exact_worst_case_cost,
        "fixed_child_schedule_lower_bound": 4 * arity * child_cost,
    }


def missing_copy_attack():
    arity, root_cost, child_cost = 3, 2, 7
    outcomes = qary_prefix_query_library(arity, 2, copies=4)[:-1]
    costs = qary_prefix_query_costs(
        arity,
        2,
        copies=4,
        level_costs=(root_cost, child_cost),
    )[:-1]
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(arity),
        outcomes,
        query_costs=costs,
        corruption_budget=1,
        erasure_budget=1,
    )
    return {
        "arity": arity,
        "root_cost": root_cost,
        "child_cost": child_cost,
        "remaining_query_instances": len(outcomes),
        "exact_cost": plan.worst_case_cost,
        "reason": plan.reason,
        "abstained": plan.root is None and plan.worst_case_cost is None,
    }


def main():
    cases = [run_case(*parameters, "opened") for parameters in OPENED]
    cases += [run_case(*parameters, "prospective") for parameters in PROSPECTIVE]
    attack = missing_copy_attack()
    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":"))
    summary = {
        "case_total": len(cases),
        "cases_completed": sum(item["certificate_valid"] for item in cases),
        "formula_matches": sum(item["formula_matched"] for item in cases),
        "prospective_matches": sum(
            item["formula_matched"] for item in cases if item["role"] == "prospective"
        ),
        "regimes_observed": sorted({item["active_regime"] for item in cases}),
        "missing_copy_abstained": attack["abstained"],
        "case_digest": hashlib.sha256(canonical.encode()).hexdigest(),
    }
    summary["passed"] = (
        summary["cases_completed"] == summary["case_total"]
        and summary["formula_matches"] == summary["case_total"]
        and summary["prospective_matches"] == len(PROSPECTIVE)
        and len(summary["regimes_observed"]) == 3
        and summary["missing_copy_abstained"]
    )
    result = {
        "schema": "theorica.qary-two-level-insurance/1",
        "claim": "C_q(a,b)=max(2a+4b,3a+3b,4a+b)",
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
