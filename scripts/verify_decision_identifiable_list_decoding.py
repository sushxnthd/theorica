#!/usr/bin/env python3
"""Frozen exact verification of decision-identifiable list decoding."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    certify_two_action_plan_from_ambiguous_transcript,
    reconstruct_corruption_resilient_feature_payoffs,
)

OUT = Path("results/decision_identifiable_list_decoding/results.json")


def encode(value):
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    raise TypeError(type(value).__name__)


def solve(features, observations):
    return certify_two_action_plan_from_ambiguous_transcript(
        features,
        tuple(range(len(features))),
        observations,
        payoff_in_feature_span_certified=True,
        corruption_budget=1,
    )


def unique_baseline_abstains(features, observations):
    calls = []

    def oracle(index):
        calls.append(index)
        return ((observations[index][0], observations[index][1]),)

    try:
        reconstruct_corruption_resilient_feature_payoffs(
            features,
            oracle,
            payoff_in_feature_span_certified=True,
            corruption_budget=1,
            max_query_count=len(features),
        )
    except ValueError:
        return not calls
    return False


def positive_case(case, *, quadratic):
    shift = Fraction(3 * case - 41, 7)
    delta = Fraction(case + 1, 11)
    if quadratic:
        features = tuple((1, x, x * x) for x in range(4))
        observations = ((shift, shift),) * 3 + ((shift, shift + delta),)
        family = "prospective_quadratic"
    else:
        features = ((1, 0), (1, 1), (1, 2))
        observations = ((shift, shift), (shift, shift), (shift, shift + delta))
        family = "opened_affine"
    result = solve(features, observations)
    passed = (
        result.certificate_valid
        and not result.model_identifiable
        and result.value_identifiable
        and result.policy_identifiable
        and result.minimax_value == shift
        and result.action_probabilities == (1, 0)
        and unique_baseline_abstains(features, observations)
    )
    return {
        "case": case,
        "family": family,
        "version_space_size": result.version_space_size,
        "value": result.minimax_value,
        "policy": result.action_probabilities,
        "unique_model_baseline_abstained": unique_baseline_abstains(features, observations),
        "passed": passed,
    }


def attack_case(case, *, disjoint):
    shift = Fraction(case - 13, 5)
    scale = Fraction(case + 2, 9)
    features = ((1, 0), (1, 1), (1, 2))
    if disjoint:
        base = ((-2, -1), (-1, -1), (-2, 0))
        observations = tuple(
            tuple(shift + scale * value for value in row) for row in base
        )
        expected_reason = "ambiguous_transcript_has_disjoint_optimal_policy_sets"
        family = "equal_value_disjoint_policy"
    else:
        observations = (
            (shift, shift),
            (shift, shift),
            (shift + scale, shift + scale),
        )
        expected_reason = "ambiguous_transcript_has_multiple_robust_values"
        family = "unequal_value"
    result = solve(features, observations)
    return {
        "case": case,
        "family": family,
        "version_space_size": result.version_space_size,
        "value_identifiable": result.value_identifiable,
        "policy_identifiable": result.policy_identifiable,
        "reason": result.reason,
        "passed": (
            result.certificate_valid
            and not result.policy_identifiable
            and result.action_probabilities is None
            and result.reason == expected_reason
        ),
    }


def main():
    opened = [positive_case(case, quadratic=False) for case in range(40)]
    holdouts = [positive_case(100 + case, quadratic=True) for case in range(20)]
    unequal = [attack_case(case, disjoint=False) for case in range(20)]
    disjoint = [attack_case(100 + case, disjoint=True) for case in range(20)]
    cases = opened + holdouts + unequal + disjoint
    canonical = json.dumps(cases, default=encode, sort_keys=True, separators=(",", ":"))
    summary = {
        "opened_decision_identifiable": sum(row["passed"] for row in opened),
        "opened_total": len(opened),
        "prospective_holdouts_passed": sum(row["passed"] for row in holdouts),
        "prospective_holdouts_total": len(holdouts),
        "unique_decoder_abstentions": sum(
            row["unique_model_baseline_abstained"] for row in opened + holdouts
        ),
        "unequal_value_attacks_rejected": sum(row["passed"] for row in unequal),
        "disjoint_policy_attacks_rejected": sum(row["passed"] for row in disjoint),
        "attack_total": len(unequal) + len(disjoint),
        "digest": hashlib.sha256(canonical.encode()).hexdigest(),
        "passed": all(row["passed"] for row in cases),
    }
    result = {"schema": "theorica.decision-identifiable-list-decoding/1",
              "summary": summary, "cases": cases}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, default=encode, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
