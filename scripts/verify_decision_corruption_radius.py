#!/usr/bin/env python3
"""Primary exact verification of the decision corruption-radius law."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from math import ceil, log2
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_common_robust_plan,
    certify_decision_query_corruption_radius,
)

OUT = Path("results/decision_corruption_radius/results.json")


def unique_mixing_game(probability):
    p = Fraction(probability)
    return ((1 - p, p - 1), (-p, p))


def indexed_outcomes(count):
    width = ceil(log2(count))
    return tuple(
        tuple((completion >> (width - query - 1)) & 1
              for completion in range(count))
        for query in range(width)
    )


def repeated(outcomes, repetitions):
    return tuple(row for row in outcomes for _ in range(repetitions))


def unique_games(count):
    return tuple(
        unique_mixing_game(Fraction(index + 1, count + 1))
        for index in range(count)
    )


def code_case(count, family):
    result = certify_decision_query_corruption_radius(
        unique_games(count),
        repeated(indexed_outcomes(count), 3),
        corruption_budget=1,
    )
    return {
        "family": family,
        "completions": count,
        "queries": result.query_count,
        "decision_radius": result.decision_radius,
        "max_certified_corruptions": result.max_certified_corruptions,
        "passed": (
            result.certificate_valid
            and result.decision_radius == 2
            and result.max_certified_corruptions == 1
            and result.robust_to_budget
        ),
    }


def missing_repetition_case(dimension):
    count = 1 << dimension
    result = certify_decision_query_corruption_radius(
        unique_games(count), indexed_outcomes(count), corruption_budget=1
    )
    return {
        "family": "missing-repetition-attack",
        "dimension": dimension,
        "completions": count,
        "decision_radius": result.decision_radius,
        "attack_center": list(result.closest_incompatible_center),
        "passed": (
            result.certificate_valid
            and result.decision_radius == 1
            and not result.robust_to_budget
            and len(result.incompatibility_witness) == 2
        ),
    }


def saving_case(dimension):
    count = 1 << dimension
    games = tuple(
        unique_mixing_game(Fraction(1, 3) if index < count // 2 else Fraction(2, 3))
        for index in range(count)
    )
    decision_bit = tuple(0 if index < count // 2 else 1 for index in range(count))
    result = certify_decision_query_corruption_radius(
        games, (decision_bit,) * 3, corruption_budget=1
    )
    unique_queries = 3 * dimension
    return {
        "family": "decision-quotient-saving",
        "dimension": dimension,
        "completions": count,
        "decision_queries": result.query_count,
        "unique_model_queries": unique_queries,
        "queries_saved": unique_queries - result.query_count,
        "decision_radius": result.decision_radius,
        "passed": (
            result.certificate_valid
            and result.decision_radius == 2
            and result.robust_to_budget
            and result.query_count == 3
        ),
    }


def face_games(actions):
    return tuple(
        tuple((Fraction(-1 if action == excluded else 0),) for action in range(actions))
        for excluded in range(actions)
    )


def unit_outcomes(actions, repetitions):
    base = tuple(
        tuple(int(completion == query) for completion in range(actions))
        for query in range(actions)
    )
    return repeated(base, repetitions)


def higher_order_case(actions, repetitions, family):
    games = face_games(actions)
    pairwise_compatible = all(
        certify_common_robust_plan((games[left], games[right])).policy_identifiable
        for left in range(actions)
        for right in range(left + 1, actions)
    )
    result = certify_decision_query_corruption_radius(
        games,
        unit_outcomes(actions, repetitions),
        corruption_budget=1 if repetitions == 1 else repetitions - 1,
    )
    return {
        "family": family,
        "actions": actions,
        "queries": result.query_count,
        "decision_radius": result.decision_radius,
        "pairwise_conflict_edges": 0 if pairwise_compatible else None,
        "witness_size": len(result.incompatibility_witness),
        "passed": (
            pairwise_compatible
            and result.certificate_valid
            and result.decision_radius == repetitions
            and result.robust_to_budget == (repetitions > 1)
            and len(result.incompatibility_witness) == actions
        ),
    }


def main():
    opened = [code_case(count, "opened-binary-code") for count in range(2, 17)]
    prospective = [
        code_case(1 << dimension, "prospective-coordinate-code")
        for dimension in (5, 6)
    ]
    missing = [missing_repetition_case(dimension) for dimension in range(2, 7)]
    savings = [saving_case(dimension) for dimension in (5, 6)]
    higher_negative = [
        higher_order_case(actions, 1, "higher-order-unit-code")
        for actions in range(3, 7)
    ]
    higher_positive = [
        higher_order_case(actions, 3, "higher-order-tripled-unit-code")
        for actions in range(3, 7)
    ]
    cases = opened + prospective + missing + savings + higher_negative + higher_positive
    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":"))
    summary = {
        "opened_passed": sum(case["passed"] for case in opened),
        "opened_total": len(opened),
        "prospective_passed": sum(case["passed"] for case in prospective),
        "prospective_total": len(prospective),
        "missing_repetition_attacks": sum(case["passed"] for case in missing),
        "missing_repetition_total": len(missing),
        "saving_cases_passed": sum(case["passed"] for case in savings),
        "saving_cases_total": len(savings),
        "aggregate_queries_saved": sum(case["queries_saved"] for case in savings),
        "higher_order_negative_passed": sum(case["passed"] for case in higher_negative),
        "higher_order_negative_total": len(higher_negative),
        "higher_order_positive_passed": sum(case["passed"] for case in higher_positive),
        "higher_order_positive_total": len(higher_positive),
        "case_digest": hashlib.sha256(canonical.encode()).hexdigest(),
        "passed": all(case["passed"] for case in cases),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {"schema": "theorica.decision-corruption-radius/1", "summary": summary,
         "cases": cases},
        indent=2,
        sort_keys=True,
    ) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
