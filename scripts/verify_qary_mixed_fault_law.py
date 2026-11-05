#!/usr/bin/env python3
"""Exact verification of the q-ary substitution-erasure law."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_faults,
    qary_prefix_query_library,
)

OUT = Path("results/qary_mixed_fault_law/results.json")
OPENED = ((2, 1, 1, 1), (3, 1, 2, 1), (3, 2, 1, 0), (2, 2, 0, 2))
PROSPECTIVE = ((3, 2, 1, 1), (2, 3, 1, 2), (4, 2, 2, 1), (3, 3, 1, 1))


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


def tree_depth(node):
    if node is None or node.query_index is None:
        return 0
    return 1 + max(tree_depth(child) for _, child in node.children)


def case(arity, depth, corruptions, erasures, role):
    copies = 2 * corruptions + erasures + 1
    outcomes = qary_prefix_query_library(arity, depth, copies=copies)
    plan = plan_adaptive_decision_queries_with_faults(
        games(arity, depth),
        outcomes,
        corruption_budget=corruptions,
        erasure_budget=erasures,
    )
    predicted = (corruptions + 1) * depth + corruptions + erasures
    fixed_lower = copies * arity ** (depth - 1)
    replayed_depth = tree_depth(plan.root)
    return {
        "role": role,
        "arity": arity,
        "depth": depth,
        "corruption_budget": corruptions,
        "erasure_budget": erasures,
        "copies_per_prefix": copies,
        "completions": arity**depth,
        "query_instances": len(outcomes),
        "exact_adaptive_depth": plan.worst_case_depth,
        "replayed_tree_depth": replayed_depth,
        "predicted_depth": predicted,
        "fixed_schedule_lower_bound": fixed_lower,
        "queries_saved_against_fixed_lower_bound": fixed_lower - predicted,
        "states_solved": plan.states_solved,
        "passed": (
            plan.certificate_valid
            and plan.worst_case_depth == predicted
            and replayed_depth == predicted
        ),
    }


def missing_copy_case():
    arity, depth, corruptions, erasures = 3, 2, 1, 1
    outcomes = qary_prefix_query_library(
        arity, depth, copies=2 * corruptions + erasures + 1
    )[:-1]
    plan = plan_adaptive_decision_queries_with_faults(
        games(arity, depth),
        outcomes,
        corruption_budget=corruptions,
        erasure_budget=erasures,
    )
    return {
        "arity": arity,
        "depth": depth,
        "corruption_budget": corruptions,
        "erasure_budget": erasures,
        "remaining_query_instances": len(outcomes),
        "exact_adaptive_depth": plan.worst_case_depth,
        "reason": plan.reason,
        "states_solved": plan.states_solved,
        "passed": plan.root is None and plan.worst_case_depth is None,
    }


def main():
    cases = [case(*parameters, "opened") for parameters in OPENED]
    cases += [case(*parameters, "prospective") for parameters in PROSPECTIVE]
    attack = missing_copy_case()
    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":"))
    result = {
        "schema": "theorica.qary-mixed-fault-law/1",
        "claim": "D_q(m;t,s)=(t+1)m+t+s for q-ary prefix queries",
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
