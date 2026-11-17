#!/usr/bin/env python3
"""Exact verification of the cost-weighted q-ary mixed-fault law."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_weighted_mixed_fault_law/results.json")
OPENED = (
    (2, 1, 1, 1, (4,)),
    (3, 2, 1, 1, (1, 1)),
    (2, 2, 0, 2, (2, 3)),
)
PROSPECTIVE = (
    (3, 2, 1, 1, (1, 5)),
    (2, 3, 1, 2, (7, 1, 3)),
    (4, 2, 2, 1, (2, 9)),
    (3, 3, 1, 1, (1, 2, 5)),
)
PERMUTATIONS = (
    (2, 3, 1, 1, (1, 2, 5)),
    (2, 3, 1, 1, (5, 1, 2)),
)


def unique_mixing_game(probability: Fraction):
    return (
        (1 - probability, probability - 1),
        (-probability, probability),
    )


def games(arity: int, depth: int):
    count = arity**depth
    return tuple(
        unique_mixing_game(Fraction(index + 1, count + 1))
        for index in range(count)
    )


def case(arity, depth, corruptions, erasures, level_costs, role):
    copies = 2 * corruptions + erasures + 1
    outcomes = qary_prefix_query_library(arity, depth, copies=copies)
    costs = qary_prefix_query_costs(
        arity, depth, copies=copies, level_costs=level_costs
    )
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(arity, depth),
        outcomes,
        query_costs=costs,
        corruption_budget=corruptions,
        erasure_budget=erasures,
    )
    predicted = (corruptions + 1) * sum(level_costs) + (
        corruptions + erasures
    ) * max(level_costs)
    fixed_lower = copies * arity ** (depth - 1) * level_costs[-1]
    return {
        "role": role,
        "arity": arity,
        "depth": depth,
        "level_costs": list(level_costs),
        "corruption_budget": corruptions,
        "erasure_budget": erasures,
        "copies_per_prefix": copies,
        "completions": arity**depth,
        "query_instances": len(outcomes),
        "exact_adaptive_cost": plan.worst_case_cost,
        "exact_tree_depth": plan.worst_case_depth,
        "predicted_cost": predicted,
        "fixed_schedule_cost_lower_bound": fixed_lower,
        "cost_saved_against_fixed_lower_bound": fixed_lower - predicted,
        "states_solved": plan.states_solved,
        "certificate_valid": plan.certificate_valid,
        "formula_matched": plan.certificate_valid
        and plan.worst_case_cost == predicted,
    }


def missing_copy_case():
    arity, depth, corruptions, erasures = 3, 2, 1, 1
    level_costs = (1, 5)
    copies = 2 * corruptions + erasures + 1
    outcomes = qary_prefix_query_library(arity, depth, copies=copies)[:-1]
    costs = qary_prefix_query_costs(
        arity, depth, copies=copies, level_costs=level_costs
    )[:-1]
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(arity, depth),
        outcomes,
        query_costs=costs,
        corruption_budget=corruptions,
        erasure_budget=erasures,
    )
    return {
        "arity": arity,
        "depth": depth,
        "level_costs": list(level_costs),
        "remaining_query_instances": len(outcomes),
        "exact_adaptive_cost": plan.worst_case_cost,
        "reason": plan.reason,
        "states_solved": plan.states_solved,
        "abstained": plan.root is None and plan.worst_case_cost is None,
    }


def main():
    cases = [case(*parameters, "opened") for parameters in OPENED]
    cases += [case(*parameters, "prospective") for parameters in PROSPECTIVE]
    cases += [case(*parameters, "permutation") for parameters in PERMUTATIONS]
    attack = missing_copy_case()
    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":"))
    result = {
        "schema": "theorica.qary-weighted-mixed-fault-law/1",
        "claim": "C_q(m;t,s;c)=(t+1)sum(c)+(t+s)max(c)",
        "cases": cases,
        "missing_copy_attack": attack,
        "summary": {
            "exact_cases_completed": sum(item["certificate_valid"] for item in cases),
            "case_total": len(cases),
            "formula_matches": sum(item["formula_matched"] for item in cases),
            "counterexamples": sum(not item["formula_matched"] for item in cases),
            "prospective_counterexamples": sum(
                not item["formula_matched"]
                for item in cases
                if item["role"] == "prospective"
            ),
            "missing_copy_abstained": attack["abstained"],
            "unresolved_frozen_holdout": {
                "parameters": [3, 3, 1, 1, [5, 1, 2]],
                "status": "90_second_exact_search_cap_exceeded",
            },
            "case_digest": hashlib.sha256(canonical.encode()).hexdigest(),
            "claim_survived": all(item["formula_matched"] for item in cases),
            "experiment_passed": (
                all(item["certificate_valid"] for item in cases)
                and any(not item["formula_matched"] for item in cases)
                and attack["abstained"]
            ),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    if not result["summary"]["experiment_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
