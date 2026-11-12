#!/usr/bin/env python3
"""Open the frozen first-action-conditioned ancestor-bypass holdouts."""

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

OUT = Path("results/qary_three_level_ancestor_bypass/results.json")
HOLDOUTS = (
    (1, 1, 97),
    (1, 97, 49),
    (1, 97, 1),
    (97, 1, 48),
    (97, 49, 1),
    (97, 1, 1),
    (7, 31, 53),
    (53, 31, 7),
    (11, 47, 29),
    (47, 11, 29),
    (29, 47, 11),
    (29, 11, 47),
)
LEVEL_INDICES = {
    "unrestricted": None,
    "root": tuple(range(4)),
    "middle": tuple(range(4, 12)),
    "leaf": tuple(range(12, 28)),
}


def games():
    return tuple(
        (
            (1 - (p := Fraction(index + 1, 9)), p - 1),
            (-p, p),
        )
        for index in range(8)
    )


def query_level(index):
    if index < 4:
        return "root"
    if index < 12:
        return "middle"
    return "leaf"


def solve(costs, level, feasible_bound):
    kwargs = {}
    if level in ("unrestricted", "root"):
        kwargs["known_feasible_cost_upper_bound"] = feasible_bound
    if LEVEL_INDICES[level] is not None:
        kwargs["allowed_initial_query_indices"] = LEVEL_INDICES[level]
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
        **kwargs,
    )
    first_index = None if plan.root is None else plan.root.query_index
    return {
        "exact_cost": plan.worst_case_cost,
        "first_query_index": first_index,
        "first_query_level": (
            None if first_index is None else query_level(first_index)
        ),
        "states_solved": plan.states_solved,
        "compatibility_states_solved": plan.compatibility_states_solved,
        "certificate_valid": plan.certificate_valid,
    }


def exact_case(costs):
    certificate = certify_qary_three_level_insurance(2, *costs)
    conditioned = {
        level: solve(costs, level, certificate.exact_worst_case_cost)
        for level in LEVEL_INDICES
    }
    unrestricted = conditioned["unrestricted"]["exact_cost"]
    root = conditioned["root"]["exact_cost"]
    return {
        "level_costs": list(costs),
        "six_face_cost": certificate.exact_worst_case_cost,
        "active_faces": list(certificate.active_faces),
        "conditioned": conditioned,
        "descendant_ties": [
            level
            for level in ("middle", "leaf")
            if conditioned[level]["exact_cost"] == unrestricted
        ],
        "strict_ancestor_bypass": (
            unrestricted is not None and root is not None and unrestricted < root
        ),
        "matched": (
            unrestricted == root == certificate.exact_worst_case_cost
            and all(
                item["certificate_valid"] and item["exact_cost"] is not None
                for item in conditioned.values()
            )
        ),
    }


def missing_copy_attack():
    costs = (97, 1, 48)
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
    holdouts = [exact_case(costs) for costs in HOLDOUTS]
    attack = missing_copy_attack()
    middle_penalties = [
        item["conditioned"]["middle"]["exact_cost"]
        - item["conditioned"]["unrestricted"]["exact_cost"]
        for item in holdouts
    ]
    leaf_penalties = [
        item["conditioned"]["leaf"]["exact_cost"]
        - item["conditioned"]["unrestricted"]["exact_cost"]
        for item in holdouts
    ]
    summary = {
        "holdout_total": len(holdouts),
        "holdout_matches": sum(item["matched"] for item in holdouts),
        "strict_ancestor_bypass_count": sum(
            item["strict_ancestor_bypass"] for item in holdouts
        ),
        "middle_first_ties": sum(
            "middle" in item["descendant_ties"] for item in holdouts
        ),
        "leaf_first_ties": sum(
            "leaf" in item["descendant_ties"] for item in holdouts
        ),
        "minimum_middle_first_penalty": min(middle_penalties),
        "maximum_middle_first_penalty": max(middle_penalties),
        "minimum_leaf_first_penalty": min(leaf_penalties),
        "maximum_leaf_first_penalty": max(leaf_penalties),
        "missing_copy_abstained": attack["abstained"],
    }
    summary["passed"] = (
        summary["holdout_matches"] == summary["holdout_total"] == 12
        and summary["strict_ancestor_bypass_count"] == 0
        and summary["missing_copy_abstained"]
    )
    result = {
        "schema": "theorica.qary-three-level-ancestor-bypass/1",
        "claim": "root-first conditioning matches unrestricted exact cost on frozen rays",
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
