#!/usr/bin/env python3
"""Primary exact verification of adaptive decision queries with bounded lies."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_common_robust_plan,
    plan_adaptive_decision_queries_with_lies,
)

OUT = Path("results/adaptive_decision_lies/results.json")


def unique_mixing_game(probability):
    probability = Fraction(probability)
    return (
        (1 - probability, probability - 1),
        (-probability, probability),
    )


def unique_games(count):
    return tuple(
        unique_mixing_game(Fraction(index + 1, count + 1))
        for index in range(count)
    )


def repeated(row, copies):
    return tuple(tuple(row) for _ in range(copies))


def prefix_tree_queries(depth, copies=3):
    count = 1 << depth
    rows = []
    for level in range(depth):
        for prefix in range(1 << level):
            row = []
            for completion in range(count):
                observed_prefix = completion >> (depth - level)
                if observed_prefix == prefix:
                    row.append((completion >> (depth - level - 1)) & 1)
                else:
                    row.append(0)
            rows.extend((tuple(row),) * copies)
    return tuple(rows)


def face_games(actions):
    return tuple(
        tuple((Fraction(-1 if action == excluded else 0),) for action in range(actions))
        for excluded in range(actions)
    )


def validate_tree(plan, games, outcomes):
    if plan.root is None:
        return plan.worst_case_depth is None
    budget = plan.corruption_budget

    def visit(node, remaining, depth):
        feasible = tuple(
            index for index, count in enumerate(node.lie_counts) if count <= budget
        )
        if feasible != node.feasible_completion_indices:
            return False, depth
        if node.query_index is None:
            certificate = certify_common_robust_plan(
                tuple(games[index] for index in feasible)
            )
            valid = (
                certificate.certificate_valid
                and certificate.policy_identifiable
                and node.action_probabilities == certificate.action_probabilities
                and node.minimax_value == certificate.minimax_value
            )
            return valid, depth
        if node.query_index not in remaining:
            return False, depth
        query = node.query_index
        next_remaining = tuple(item for item in remaining if item != query)
        alphabet = sorted(
            set(outcomes[query]),
            key=lambda value: (type(value).__name__, repr(value)),
        )
        expected = {}
        for answer in alphabet:
            counts = tuple(
                min(budget + 1, count + (outcomes[query][index] != answer))
                for index, count in enumerate(node.lie_counts)
            )
            if any(count <= budget for count in counts):
                expected[answer] = counts
        children = dict(node.children)
        if set(children) != set(expected):
            return False, depth
        checks = []
        for answer, child in node.children:
            if child.lie_counts != expected[answer]:
                return False, depth
            checks.append(visit(child, next_remaining, depth + 1))
        return all(valid for valid, _ in checks), max(level for _, level in checks)

    valid, depth = visit(plan.root, tuple(range(len(outcomes))), 0)
    return valid and depth == plan.worst_case_depth


def serialize_tree(node):
    if node is None:
        return None
    return {
        "lie_counts": list(node.lie_counts),
        "feasible_completions": list(node.feasible_completion_indices),
        "query_index": node.query_index,
        "action_probabilities": (
            None
            if node.action_probabilities is None
            else [str(value) for value in node.action_probabilities]
        ),
        "minimax_value": (
            None if node.minimax_value is None else str(node.minimax_value)
        ),
        "children": [
            {"answer": answer, "node": serialize_tree(child)}
            for answer, child in node.children
        ],
    }


def repetition_case(budget):
    games = unique_games(2)
    outcomes = repeated((0, 1), 2 * budget + 1)
    plan = plan_adaptive_decision_queries_with_lies(
        games, outcomes, corruption_budget=budget
    )
    return {
        "family": "two-class-repetition",
        "budget": budget,
        "queries": len(outcomes),
        "adaptive_depth": plan.worst_case_depth,
        "states_solved": plan.states_solved,
        "tree": serialize_tree(plan.root),
        "passed": (
            plan.certificate_valid
            and plan.worst_case_depth == 2 * budget + 1
            and validate_tree(plan, games, outcomes)
        ),
    }


def missing_copy_case(budget):
    games = unique_games(2)
    outcomes = repeated((0, 1), 2 * budget)
    plan = plan_adaptive_decision_queries_with_lies(
        games, outcomes, corruption_budget=budget
    )
    return {
        "family": "missing-copy-attack",
        "budget": budget,
        "queries": len(outcomes),
        "adaptive_depth": plan.worst_case_depth,
        "reason": plan.reason,
        "passed": plan.root is None and plan.worst_case_depth is None,
    }


def prefix_case(depth, family):
    games = unique_games(1 << depth)
    outcomes = prefix_tree_queries(depth)
    plan = plan_adaptive_decision_queries_with_lies(
        games, outcomes, corruption_budget=1
    )
    fixed_lower_bound = 3 * (1 << (depth - 1))
    return {
        "family": family,
        "depth": depth,
        "completions": len(games),
        "available_query_instances": len(outcomes),
        "adaptive_depth": plan.worst_case_depth,
        "constructive_upper_bound": 3 * depth,
        "fixed_schedule_lower_bound": fixed_lower_bound,
        "queries_saved_against_fixed_lower_bound": (
            None
            if plan.worst_case_depth is None
            else fixed_lower_bound - plan.worst_case_depth
        ),
        "states_solved": plan.states_solved,
        "tree": serialize_tree(plan.root),
        "passed": (
            plan.certificate_valid
            and plan.worst_case_depth is not None
            and plan.worst_case_depth <= 3 * depth
            and plan.worst_case_depth < fixed_lower_bound
            and validate_tree(plan, games, outcomes)
        ),
    }


def higher_order_case(actions):
    games = face_games(actions)
    pairwise = all(
        certify_common_robust_plan((games[left], games[right])).policy_identifiable
        for left in range(actions)
        for right in range(left + 1, actions)
    )
    row = tuple(0 if index == 0 else 1 for index in range(actions))
    outcomes = repeated(row, 3)
    plan = plan_adaptive_decision_queries_with_lies(
        games, outcomes, corruption_budget=1
    )
    return {
        "family": "higher-order-policy-conflict",
        "actions": actions,
        "pairwise_conflict_edges": 0 if pairwise else None,
        "adaptive_depth": plan.worst_case_depth,
        "tree": serialize_tree(plan.root),
        "passed": (
            pairwise
            and plan.certificate_valid
            and plan.worst_case_depth == 3
            and validate_tree(plan, games, outcomes)
        ),
    }


def main():
    repetition = [repetition_case(budget) for budget in (0, 1, 2)]
    missing = [missing_copy_case(budget) for budget in (1, 2)]
    opened = [prefix_case(depth, "opened-prefix-tree") for depth in (2, 3)]
    prospective = [prefix_case(4, "prospective-prefix-tree")]
    higher_order = [higher_order_case(actions) for actions in range(3, 7)]
    cases = repetition + missing + opened + prospective + higher_order
    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":"))
    summary = {
        "repetition_passed": sum(case["passed"] for case in repetition),
        "repetition_total": len(repetition),
        "missing_copy_abstentions": sum(case["passed"] for case in missing),
        "missing_copy_total": len(missing),
        "opened_passed": sum(case["passed"] for case in opened),
        "opened_total": len(opened),
        "prospective_passed": sum(case["passed"] for case in prospective),
        "prospective_total": len(prospective),
        "prospective_adaptive_depth": prospective[0]["adaptive_depth"],
        "prospective_fixed_lower_bound": prospective[0][
            "fixed_schedule_lower_bound"
        ],
        "higher_order_passed": sum(case["passed"] for case in higher_order),
        "higher_order_total": len(higher_order),
        "case_digest": hashlib.sha256(canonical.encode()).hexdigest(),
        "passed": all(case["passed"] for case in cases),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "schema": "theorica.adaptive-decision-lies/1",
                "summary": summary,
                "cases": cases,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
