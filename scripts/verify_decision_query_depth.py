#!/usr/bin/env python3
"""Exact primary verification of optimal decision-identifying query trees."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from math import ceil, log2
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_common_robust_plan,
    plan_decision_identifying_queries,
)

OUT = Path("results/decision_query_depth/results.json")


def unique_mixing_game(probability):
    """Two-action game with value zero and unique optimal first-action mass p."""
    p = Fraction(probability)
    return ((1 - p, p - 1), (-p, p))


def coordinate_outcomes(dimension):
    return tuple(
        tuple((completion >> (dimension - query - 1)) & 1
              for completion in range(1 << dimension))
        for query in range(dimension)
    )


def indexed_outcomes(completion_count):
    dimension = ceil(log2(completion_count))
    return tuple(
        tuple((completion >> (dimension - query - 1)) & 1
              for completion in range(completion_count))
        for query in range(dimension)
    )


def leaf_states(node):
    if node.query_index is None:
        return (node.completion_indices,)
    return tuple(
        leaf
        for _, child in node.children
        for leaf in leaf_states(child)
    )


def valid_tree(plan, games, outcomes):
    if plan.root is None:
        return plan.worst_case_depth is None

    def check(node, depth):
        if node.query_index is None:
            certificate = certify_common_robust_plan(
                tuple(games[index] for index in node.completion_indices)
            )
            return (
                certificate.certificate_valid
                and certificate.policy_identifiable
                and node.action_probabilities == certificate.action_probabilities
                and node.minimax_value == certificate.minimax_value
            ), depth
        expected = {}
        for completion in node.completion_indices:
            expected.setdefault(outcomes[node.query_index][completion], []).append(completion)
        actual = {outcome: child.completion_indices for outcome, child in node.children}
        if actual != {outcome: tuple(members) for outcome, members in expected.items()}:
            return False, depth
        checked = [check(child, depth + 1) for _, child in node.children]
        return all(valid for valid, _ in checked), max(item[1] for item in checked)

    valid, depth = check(plan.root, 0)
    return valid and depth == plan.worst_case_depth


def coordinate_case(dimension, family):
    count = 1 << dimension
    games = tuple(unique_mixing_game(Fraction(index + 1, count + 1))
                  for index in range(count))
    outcomes = coordinate_outcomes(dimension)
    plan = plan_decision_identifying_queries(games, outcomes)
    leaves = leaf_states(plan.root)
    passed = (
        plan.certificate_valid
        and plan.worst_case_depth == dimension
        and len(leaves) == count
        and all(len(leaf) == 1 for leaf in leaves)
        and valid_tree(plan, games, outcomes)
    )
    return {
        "family": family,
        "dimension": dimension,
        "completions": count,
        "decision_depth": plan.worst_case_depth,
        "unique_model_depth": dimension,
        "states_solved": plan.states_solved,
        "passed": passed,
    }


def opened_indexed_case(completion_count):
    games = tuple(
        unique_mixing_game(Fraction(index + 1, completion_count + 1))
        for index in range(completion_count)
    )
    outcomes = indexed_outcomes(completion_count)
    expected = ceil(log2(completion_count))
    plan = plan_decision_identifying_queries(games, outcomes)
    return {
        "family": "opened-binary-feature-code",
        "completions": completion_count,
        "decision_depth": plan.worst_case_depth,
        "unique_model_depth": expected,
        "passed": (
            plan.worst_case_depth == expected
            and valid_tree(plan, games, outcomes)
        ),
    }


def saving_case(dimension):
    count = 1 << dimension
    games = tuple(
        unique_mixing_game(Fraction(1, 3) if index < count // 2 else Fraction(2, 3))
        for index in range(count)
    )
    outcomes = coordinate_outcomes(dimension)
    plan = plan_decision_identifying_queries(games, outcomes)
    return {
        "family": "decision-quotient-saving",
        "dimension": dimension,
        "completions": count,
        "decision_depth": plan.worst_case_depth,
        "unique_model_depth": dimension,
        "queries_saved": dimension - plan.worst_case_depth,
        "passed": (
            plan.worst_case_depth == 1
            and plan.root.query_index == 0
            and valid_tree(plan, games, outcomes)
        ),
    }


def missing_coordinate_case(dimension):
    count = 1 << dimension
    games = tuple(unique_mixing_game(Fraction(index + 1, count + 1))
                  for index in range(count))
    outcomes = coordinate_outcomes(dimension)[:-1]
    plan = plan_decision_identifying_queries(games, outcomes)
    return {
        "family": "missing-coordinate-attack",
        "dimension": dimension,
        "completions": count,
        "decision_depth": plan.worst_case_depth,
        "reason": plan.reason,
        "passed": (
            plan.root is None
            and plan.worst_case_depth is None
            and plan.reason == "available_queries_cannot_identify_a_common_robust_policy"
        ),
    }


def controls_case(dimension):
    count = 1 << dimension
    games = tuple(unique_mixing_game(Fraction(index + 1, count + 1))
                  for index in range(count))
    coordinates = coordinate_outcomes(dimension)
    outcomes = coordinates + (coordinates[0], tuple(0 for _ in range(count)))
    plan = plan_decision_identifying_queries(games, outcomes)
    return {
        "family": "redundant-and-constant-controls",
        "dimension": dimension,
        "decision_depth": plan.worst_case_depth,
        "passed": (
            plan.worst_case_depth == dimension
            and valid_tree(plan, games, outcomes)
        ),
    }


def sharp_face_games(action_count):
    return tuple(
        tuple(
            (Fraction(-1 if action == excluded else 0),)
            for action in range(action_count)
        )
        for excluded in range(action_count)
    )


def higher_order_case(action_count):
    games = sharp_face_games(action_count)
    outcomes = (tuple(0 if index == 0 else 1 for index in range(action_count)),)
    plan = plan_decision_identifying_queries(games, outcomes)
    pairwise_compatible = all(
        certify_common_robust_plan((games[left], games[right])).policy_identifiable
        for left in range(action_count)
        for right in range(left + 1, action_count)
    )
    return {
        "family": "higher-order-policy-conflict",
        "actions": action_count,
        "decision_depth": plan.worst_case_depth,
        "pairwise_conflict_edges": 0 if pairwise_compatible else None,
        "passed": (
            pairwise_compatible
            and plan.worst_case_depth == 1
            and valid_tree(plan, games, outcomes)
        ),
    }


def main():
    opened = [opened_indexed_case(count) for count in range(2, 9)]
    prospective = [coordinate_case(dimension, "prospective-coordinate")
                   for dimension in (5, 6)]
    savings = [saving_case(dimension) for dimension in range(2, 7)]
    missing = [missing_coordinate_case(dimension) for dimension in range(2, 7)]
    controls = [controls_case(dimension) for dimension in range(2, 6)]
    higher_order = [higher_order_case(actions) for actions in range(3, 7)]
    cases = opened + prospective + savings + missing + controls + higher_order
    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":"))
    summary = {
        "opened_passed": sum(case["passed"] for case in opened),
        "opened_total": len(opened),
        "prospective_passed": sum(case["passed"] for case in prospective),
        "prospective_total": len(prospective),
        "saving_cases_passed": sum(case["passed"] for case in savings),
        "saving_cases_total": len(savings),
        "missing_coordinate_abstentions": sum(case["passed"] for case in missing),
        "missing_coordinate_total": len(missing),
        "control_cases_passed": sum(case["passed"] for case in controls),
        "control_cases_total": len(controls),
        "higher_order_cases_passed": sum(case["passed"] for case in higher_order),
        "higher_order_cases_total": len(higher_order),
        "aggregate_queries_saved": sum(case["queries_saved"] for case in savings),
        "case_digest": hashlib.sha256(canonical.encode()).hexdigest(),
        "passed": all(case["passed"] for case in cases),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {"schema": "theorica.decision-query-depth/1", "summary": summary, "cases": cases},
        indent=2,
        sort_keys=True,
    ) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
