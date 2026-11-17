#!/usr/bin/env python3
"""Exact verification of the multi-action decision quotient and Helly witness."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_common_robust_plan,
    certify_multi_action_plan_from_ambiguous_transcript,
)

OUT = Path("results/multi_action_decision_quotient/results.json")


def features(family, case):
    if family == "affine":
        start = Fraction(case - 20, 7)
        return tuple((1, start + index) for index in range(3))
    start = 3 + case
    return tuple((1, Fraction(1, start + index)) for index in range(3))


def positive(case, family, action_count):
    shift = Fraction(case - 17, 11)
    clean = tuple(shift - action for action in range(action_count))
    corrupted = (shift,) + tuple(
        shift + action + Fraction(case + 1, 13)
        for action in range(1, action_count)
    )
    observed = (clean, clean, corrupted)
    result = certify_multi_action_plan_from_ambiguous_transcript(
        features(family, case),
        (0, 1, 2),
        observed,
        payoff_in_feature_span_certified=True,
        corruption_budget=1,
    )
    passed = (
        result.certificate_valid
        and result.policy_identifiable
        and not result.model_identifiable
        and result.version_space_size > 1
        and result.minimax_value == shift
        and result.action_probabilities == (Fraction(1),)
        + (Fraction(0),) * (action_count - 1)
        and result.finite_list_minimum_distance == 2
    )
    return {
        "case": case,
        "family": family,
        "actions": action_count,
        "version_space_size": result.version_space_size,
        "candidate_combinations_tested": result.candidate_combinations_tested,
        "passed": passed,
    }


def unequal_value(case, action_count):
    low = tuple((Fraction(0),) if action == 0 else (Fraction(-action),)
                for action in range(action_count))
    high = tuple((Fraction(1),) if action == 0 else (Fraction(-action),)
                 for action in range(action_count))
    result = certify_common_robust_plan((low, high))
    return {
        "case": case,
        "actions": action_count,
        "witness": result.impossibility_witness,
        "passed": result.certificate_valid
        and not result.value_identifiable
        and result.impossibility_witness == (0, 1),
    }


def face_game(action_count, excluded):
    return tuple((Fraction(-1 if action == excluded else 0),)
                 for action in range(action_count))


def disjoint(case, action_count):
    games = tuple(face_game(action_count, excluded)
                  for excluded in range(action_count))
    result = certify_common_robust_plan(games)
    pairwise_or_local = all(
        certify_common_robust_plan(tuple(games[index] for index in subset)).policy_identifiable
        for size in range(2, action_count)
        for subset in combinations(range(action_count), size)
    )
    return {
        "case": case,
        "actions": action_count,
        "witness": result.impossibility_witness,
        "all_proper_subfamilies_intersect": pairwise_or_local,
        "passed": result.certificate_valid
        and result.value_identifiable
        and not result.policy_identifiable
        and pairwise_or_local
        and len(result.impossibility_witness) == action_count,
    }


def main():
    positives = [positive(case, "affine", 3 + (case % 2)) for case in range(40)]
    holdouts = [positive(100 + case, "reciprocal", 3 + (case % 2))
                for case in range(20)]
    value_attacks = [unequal_value(case, 3 + (case % 2)) for case in range(20)]
    policy_attacks = [disjoint(case, 3 if case < 10 else 4) for case in range(20)]
    transcript = positives + holdouts + value_attacks + policy_attacks
    canonical = json.dumps(transcript, sort_keys=True, separators=(",", ":"))
    summary = {
        "opened_positive_passed": sum(row["passed"] for row in positives),
        "opened_positive_total": len(positives),
        "prospective_reciprocal_passed": sum(row["passed"] for row in holdouts),
        "prospective_reciprocal_total": len(holdouts),
        "unequal_value_attacks_rejected": sum(row["passed"] for row in value_attacks),
        "unequal_value_attack_total": len(value_attacks),
        "disjoint_policy_attacks_rejected": sum(row["passed"] for row in policy_attacks),
        "disjoint_policy_attack_total": len(policy_attacks),
        "sharp_three_action_witnesses": sum(
            row["passed"] and row["actions"] == 3 for row in policy_attacks
        ),
        "sharp_four_action_witnesses": sum(
            row["passed"] and row["actions"] == 4 for row in policy_attacks
        ),
        "digest": hashlib.sha256(canonical.encode()).hexdigest(),
        "passed": all(row["passed"] for row in transcript),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"schema": "theorica.multi-action-decision-quotient/1",
                               "summary": summary, "cases": transcript},
                              indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
