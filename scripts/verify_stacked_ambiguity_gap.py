#!/usr/bin/env python3
"""Exact verification of the stacked ambiguity-gap law."""

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

OUT = Path("results/stacked_ambiguity_gap/results.json")


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
    result = certify_multi_action_plan_from_ambiguous_transcript(
        features(family, case),
        (0, 1, 2),
        (clean, clean, corrupted),
        payoff_in_feature_span_certified=True,
        corruption_budget=1,
    )
    return {
        "case": case,
        "family": family,
        "actions": action_count,
        "version_space_size": result.version_space_size,
        "passed": result.certificate_valid
        and result.version_space_size > 1
        and result.policy_identifiable
        and result.stacked_value == shift
        and result.ambiguity_gap == 0
        and not result.scenario_witness,
    }


def face_game(action_count, excluded):
    return tuple(
        (Fraction(-1 if action == excluded else 0),)
        for action in range(action_count)
    )


def disjoint(case, action_count, prospective=False):
    games = tuple(face_game(action_count, excluded) for excluded in range(action_count))
    result = certify_common_robust_plan(games)
    proper = all(
        certify_common_robust_plan(tuple(games[index] for index in subset)).ambiguity_gap
        == 0
        for size in range(1, action_count)
        for subset in combinations(range(action_count), size)
    )
    return {
        "case": case,
        "actions": action_count,
        "prospective": prospective,
        "gap": str(result.ambiguity_gap),
        "stacked_value": str(result.stacked_value),
        "witness": result.scenario_witness,
        "all_proper_subfamilies_zero_gap": proper,
        "passed": result.certificate_valid
        and not result.policy_identifiable
        and result.stacked_value == Fraction(-1, action_count)
        and result.ambiguity_gap == Fraction(1, action_count)
        and len(result.scenario_witness) == action_count
        and proper,
    }


def unequal(case):
    result = certify_common_robust_plan((((0,), (-1,)), ((case + 1,), (-1,))))
    return {
        "case": case,
        "passed": result.certificate_valid
        and not result.value_identifiable
        and result.ambiguity_gap is None,
    }


def main():
    positives = [positive(case, "affine", 3 + case % 2) for case in range(40)]
    holdouts = [
        positive(100 + case, "reciprocal", 3 + case % 2) for case in range(20)
    ]
    attacks = [disjoint(case, 3 if case < 10 else 4) for case in range(20)]
    prospective = [disjoint(200 + case, 5, prospective=True) for case in range(10)]
    unequal_cases = [unequal(case) for case in range(20)]
    cases = positives + holdouts + attacks + prospective + unequal_cases
    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":"))
    summary = {
        "opened_zero_gap": sum(row["passed"] for row in positives),
        "opened_total": len(positives),
        "holdout_zero_gap": sum(row["passed"] for row in holdouts),
        "holdout_total": len(holdouts),
        "known_attacks_positive_gap": sum(row["passed"] for row in attacks),
        "known_attack_total": len(attacks),
        "prospective_five_action_passed": sum(row["passed"] for row in prospective),
        "prospective_five_action_total": len(prospective),
        "unequal_value_abstentions": sum(row["passed"] for row in unequal_cases),
        "unequal_value_total": len(unequal_cases),
        "digest": hashlib.sha256(canonical.encode()).hexdigest(),
        "passed": all(row["passed"] for row in cases),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({"schema": "theorica.stacked-ambiguity-gap/1", "summary": summary,
                    "cases": cases}, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
