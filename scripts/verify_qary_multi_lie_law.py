#!/usr/bin/env python3
"""Exact verification of the q-ary multiple-lie law."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_lies,
    qary_prefix_query_library,
)

OUT = Path("results/qary_multi_lie_law/results.json")
OPENED = (
    (2, 1, 2),
    (3, 1, 2),
    (2, 2, 2),
    (3, 2, 2),
    (4, 2, 2),
    (5, 2, 2),
    (2, 3, 2),
    (2, 2, 3),
    (3, 2, 3),
)
PROSPECTIVE = ((3, 3, 2), (4, 2, 3), (2, 3, 3))


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


def case(arity: int, depth: int, budget: int, role: str):
    outcomes = qary_prefix_query_library(arity, depth, copies=2 * budget + 1)
    plan = plan_adaptive_decision_queries_with_lies(
        games(arity, depth), outcomes, corruption_budget=budget
    )
    predicted = (budget + 1) * depth + budget
    fixed_lower = (2 * budget + 1) * arity ** (depth - 1)
    return {
        "role": role,
        "arity": arity,
        "depth": depth,
        "corruption_budget": budget,
        "completions": arity**depth,
        "query_instances": len(outcomes),
        "exact_adaptive_depth": plan.worst_case_depth,
        "predicted_depth": predicted,
        "fixed_schedule_lower_bound": fixed_lower,
        "queries_saved_against_fixed_lower_bound": fixed_lower - predicted,
        "states_solved": plan.states_solved,
        "passed": plan.certificate_valid and plan.worst_case_depth == predicted,
    }


def missing_copy_case():
    arity, depth, budget = 3, 2, 2
    outcomes = qary_prefix_query_library(arity, depth, copies=2 * budget + 1)[:-1]
    plan = plan_adaptive_decision_queries_with_lies(
        games(arity, depth), outcomes, corruption_budget=budget
    )
    return {
        "arity": arity,
        "depth": depth,
        "corruption_budget": budget,
        "remaining_query_instances": len(outcomes),
        "exact_adaptive_depth": plan.worst_case_depth,
        "reason": plan.reason,
        "passed": plan.root is None and plan.worst_case_depth is None,
    }


def main():
    cases = [case(*parameters, "opened") for parameters in OPENED]
    cases += [case(*parameters, "prospective") for parameters in PROSPECTIVE]
    attack = missing_copy_case()
    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":"))
    result = {
        "schema": "theorica.qary-multi-lie-law/1",
        "claim": "D_q(m,t)=(t+1)m+t for the q-ary prefix-query family",
        "cases": cases,
        "missing_copy_attack": attack,
        "summary": {
            "cases_passed": sum(item["passed"] for item in cases),
            "case_total": len(cases),
            "prospective_passed": sum(
                item["passed"] for item in cases if item["role"] == "prospective"
            ),
            "missing_copy_abstained": attack["passed"],
            "case_digest": hashlib.sha256(canonical.encode()).hexdigest(),
            "passed": all(item["passed"] for item in cases) and attack["passed"],
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    if not result["summary"]["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
