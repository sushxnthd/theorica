#!/usr/bin/env python3
"""Exact verification of sparse dual certificates for stacked ambiguity."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_common_robust_plan,
    certify_multi_action_plan_from_ambiguous_transcript,
)

OUT = Path("results/stacked_ambiguity_dual/results.json")


def features(family, case):
    if family == "affine":
        start = Fraction(case - 20, 7)
        return tuple((1, start + index) for index in range(3))
    start = 3 + case
    return tuple((1, Fraction(1, start + index)) for index in range(3))


def transcript_case(case, family, action_count):
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
    weights = result.adversary_scenario_weights
    return {
        "case": case,
        "family": f"transcript-{family}",
        "actions": action_count,
        "stacked_value": str(result.stacked_value),
        "gap": str(result.ambiguity_gap),
        "dual_support": len(weights),
        "passed": (
            result.certificate_valid
            and result.version_space_size > 1
            and result.policy_identifiable
            and result.stacked_value == shift
            and result.ambiguity_gap == 0
            and result.stacked_action_probabilities is not None
            and sum((item[2] for item in weights), Fraction(0)) == 1
            and len(weights) <= action_count
            and max(result.adversary_action_payoffs) == shift
        ),
    }


def face_games(action_count, shift, *, extras, case):
    games = []
    for excluded in range(action_count):
        rows = []
        for action in range(action_count):
            critical = shift - (action == excluded)
            values = [critical]
            for extra in range(extras):
                increment = Fraction(
                    1 + ((case + action + 2 * extra) % 7),
                    3 + ((excluded + extra) % 5),
                )
                values.append(critical + increment)
            rows.append(tuple(values))
        games.append(tuple(rows))
    return tuple(games)


def exact_game_case(case, family, action_count, *, extras, shift):
    games = face_games(action_count, shift, extras=extras, case=case)
    result = certify_common_robust_plan(games)
    primal = result.stacked_action_probabilities
    weights = result.adversary_scenario_weights
    primal_floor = min(
        sum(
            (primal[action] * game[action][scenario]
             for action in range(action_count)),
            Fraction(0),
        )
        for game in games
        for scenario in range(len(game[0]))
    )
    dual_ceiling = max(result.adversary_action_payoffs)
    expected_stacked = shift - Fraction(1, action_count)
    passed = (
        result.certificate_valid
        and not result.policy_identifiable
        and result.minimax_value == shift
        and result.stacked_value == expected_stacked
        and result.ambiguity_gap == Fraction(1, action_count)
        and primal_floor == result.stacked_value
        and dual_ceiling == result.stacked_value
        and len(weights) == action_count
        and all(weight == Fraction(1, action_count) for _, _, weight in weights)
        and all(scenario == 0 for _, scenario, _ in weights)
    )
    return {
        "case": case,
        "family": family,
        "actions": action_count,
        "extras_per_completion": extras,
        "games": [
            [[str(value) for value in row] for row in game] for game in games
        ],
        "common_value": str(result.minimax_value),
        "stacked_value": str(result.stacked_value),
        "gap": str(result.ambiguity_gap),
        "stacked_policy": [str(value) for value in primal],
        "dual": [
            {"completion": completion, "scenario": scenario, "weight": str(weight)}
            for completion, scenario, weight in weights
        ],
        "dual_action_payoffs": [str(value) for value in result.adversary_action_payoffs],
        "passed": passed,
    }


def unequal_case(case):
    result = certify_common_robust_plan((((0,), (-1,)), ((case + 1,), (-1,))))
    return {
        "case": case,
        "family": "unequal-value",
        "passed": (
            result.certificate_valid
            and not result.value_identifiable
            and result.ambiguity_gap is None
            and not result.adversary_scenario_weights
        ),
    }


def main():
    opened = [transcript_case(case, "affine", 3 + case % 2) for case in range(40)]
    holdouts = [
        transcript_case(100 + case, "reciprocal", 3 + case % 2)
        for case in range(20)
    ]
    known = [
        exact_game_case(
            case,
            "known-sharp-face",
            3 if case < 10 else 4,
            extras=0,
            shift=Fraction(case - 8, 9),
        )
        for case in range(20)
    ]
    prospective = [
        exact_game_case(
            200 + case,
            "prospective-six-action",
            6,
            extras=0,
            shift=Fraction(case - 4, 7),
        )
        for case in range(10)
    ]
    asymmetric = [
        exact_game_case(
            300 + case,
            "asymmetric-dominated-extra-scenarios",
            3 + case % 2,
            extras=2,
            shift=Fraction(case - 13, 11),
        )
        for case in range(20)
    ]
    unequal = [unequal_case(case) for case in range(20)]
    cases = opened + holdouts + known + prospective + asymmetric + unequal
    exact_cases = known + prospective + asymmetric
    canonical = json.dumps(exact_cases, sort_keys=True, separators=(",", ":"))
    summary = {
        "opened_zero_gap_duals": sum(row["passed"] for row in opened),
        "opened_total": len(opened),
        "holdout_zero_gap_duals": sum(row["passed"] for row in holdouts),
        "holdout_total": len(holdouts),
        "known_sharp_duals": sum(row["passed"] for row in known),
        "known_sharp_total": len(known),
        "prospective_six_action_duals": sum(row["passed"] for row in prospective),
        "prospective_six_action_total": len(prospective),
        "asymmetric_extra_scenario_duals": sum(row["passed"] for row in asymmetric),
        "asymmetric_extra_scenario_total": len(asymmetric),
        "unequal_value_abstentions": sum(row["passed"] for row in unequal),
        "unequal_value_total": len(unequal),
        "exact_case_digest": hashlib.sha256(canonical.encode()).hexdigest(),
        "passed": all(row["passed"] for row in cases),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {"schema": "theorica.stacked-ambiguity-dual/1", "summary": summary,
             "cases": cases},
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
