"""Frozen exact evaluation of the affine-rank-one scenario quotient law."""
from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

from theorica.agents.robust_provenance import (
    synthesize_rank_one_scenario_quotient_plan,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "rank_one_scenario_quotient" / "primary.json"
SEED = 20261024
HOLDOUT_SIZES = (9, 13, 21, 34, 64)


def expand(components):
    return tuple(
        tuple(sum((components[t][choice[t]][scenario]
                   for t in range(len(components))), Fraction(0))
              for scenario in range(len(components[0][0])))
        for choice in product(*(range(len(component)) for component in components))
    )


def two_scenario_envelope(actions, left, right):
    pairs = tuple(sorted(set((Fraction(action[left]), Fraction(action[right]))
                             for action in actions)))
    candidates = {Fraction(0), Fraction(1)}
    for first, second in combinations(pairs, 2):
        denominator = (first[0] - first[1]) - (second[0] - second[1])
        if denominator:
            probability = (second[1] - first[1]) / denominator
            if 0 <= probability <= 1:
                candidates.add(probability)

    def score(probability):
        return max(probability * a + (1 - probability) * b for a, b in pairs)

    value = min(score(probability) for probability in candidates)
    pure = max(min(a, b) for a, b in pairs)
    return value, pure < value


def affine_certificate(components):
    profiles = tuple(action for component in components for action in component)
    count = len(profiles[0])
    anchor = next((profile for profile in profiles
                   if any(value != profile[0] for value in profile[1:])), None)
    if anchor is None:
        return 0, (0, 0)
    witness = next(i for i in range(1, count) if anchor[i] != anchor[0])
    for profile in profiles:
        slope = Fraction(profile[witness] - profile[0], anchor[witness] - anchor[0])
        intercept = Fraction(profile[0]) - slope * anchor[0]
        if any(intercept + slope * anchor[i] != profile[i] for i in range(count)):
            raise ValueError("affine dimension above one")
    low = min(range(count), key=lambda i: (anchor[i], i))
    high = min(range(count), key=lambda i: (-anchor[i], i))
    return 1, (low, high)


def make_components(coordinates, coefficient_groups):
    return tuple(
        tuple(tuple(Fraction(intercept) + Fraction(slope) * z for z in coordinates)
              for intercept, slope in group)
        for group in coefficient_groups
    )


def opened_cases():
    rng = random.Random(SEED - 1)
    cases = []
    hand = (
        (((0, 1), (0, -1)),),
        (((3, 0), (1, 0)),),
        (((0, 1), (0, -1)), ((2, 1), (2, -1))),
        (((1, 2), (-2, -1), (0, 0)), ((3, -2), (-1, 2))),
    )
    for scenario_count in range(3, 7):
        for ordering in range(4):
            coordinates = [Fraction(i - scenario_count // 2) for i in range(scenario_count)]
            random.Random(SEED + 31 * scenario_count + ordering).shuffle(coordinates)
            for group in hand:
                cases.append(make_components(tuple(coordinates), group))
        for _ in range(60):
            coordinates = list(range(-scenario_count, scenario_count + 1))
            rng.shuffle(coordinates)
            coordinates = tuple(Fraction(value) for value in coordinates[:scenario_count])
            groups = []
            for _component in range(2 + rng.randrange(2)):
                actions = []
                for _action in range(2 + rng.randrange(2)):
                    actions.append((rng.randrange(-4, 5), rng.randrange(-3, 4)))
                groups.append(tuple(actions))
            cases.append(make_components(coordinates, tuple(groups)))
    return tuple(cases)


def holdout_cases():
    rng = random.Random(SEED)
    cases = []
    for scenario_count in HOLDOUT_SIZES:
        for _ in range(10):
            coordinates = list(range(-2 * scenario_count, 2 * scenario_count + 1))
            rng.shuffle(coordinates)
            coordinates = tuple(Fraction(value) for value in coordinates[:scenario_count])
            groups = []
            for _component in range(3):
                groups.append(tuple(
                    (rng.randrange(-7, 8), rng.choice((-3, -2, -1, 0, 1, 2, 3)))
                    for _action in range(2)
                ))
            cases.append(make_components(coordinates, tuple(groups)))
    return tuple(cases)


def evaluate(components):
    dimension, endpoints = affine_certificate(components)
    actions = expand(components)
    exact, strict = two_scenario_envelope(actions, *endpoints)
    plan = synthesize_rank_one_scenario_quotient_plan(
        components, payoff_additive_certified=True,
    )
    realized = tuple(
        sum((mass * sum((components[t][choice[t]][scenario]
                         for t in range(len(components))), Fraction(0))
             for choice, mass in plan.joint_actions), Fraction(0))
        for scenario in range(len(components[0][0]))
    )
    passed = (
        plan.certificate_valid
        and plan.affine_dimension == dimension
        and set(plan.endpoint_indices) == set(endpoints)
        and plan.minimax_value == exact
        and plan.strict_randomization_necessary == strict
        and len(plan.joint_actions) <= 2
        and min(realized) == exact
    )
    return {
        "value": str(exact),
        "strict": strict,
        "support": len(plan.joint_actions),
        "scenarios": len(components[0][0]),
        "expanded_actions": len(actions),
        "passed": passed,
    }


def digest_cases(items):
    digest = hashlib.sha256()
    for item in items:
        digest.update((json.dumps(item, sort_keys=True) + "\n").encode())
    return digest.hexdigest()


def main():
    opened = [evaluate(case) for case in opened_cases()]
    holdouts = [evaluate(case) for case in holdout_cases()]

    false_accepts = 0
    for scenario_count in range(3, 13):
        coordinates = tuple(Fraction(i) for i in range(scenario_count))
        for perturbation in range(1, 11):
            second = [2 * z + 3 for z in coordinates]
            second[1 + perturbation % (scenario_count - 2)] += perturbation
            attack = ((coordinates, tuple(second)),)
            try:
                synthesize_rank_one_scenario_quotient_plan(
                    attack, payoff_additive_certified=True,
                )
            except ValueError as error:
                if "affine dimension above one" not in str(error):
                    raise
            else:
                false_accepts += 1

    endpoint_attack = (((1, 0, 1), (1, 1, 0)),)
    attack_actions = expand(endpoint_attack)
    actual_attack, _ = two_scenario_envelope(attack_actions, 1, 2)
    endpoint_heuristic, _ = two_scenario_envelope(attack_actions, 0, 2)
    production_rejected_attack = False
    try:
        synthesize_rank_one_scenario_quotient_plan(
            endpoint_attack, payoff_additive_certified=True,
        )
    except ValueError:
        production_rejected_attack = True

    coordinates = tuple(Fraction(i) for i in range(-32, 32))
    scaling_components = tuple(
        (
            tuple(coordinates),
            tuple(-z for z in coordinates),
            tuple(Fraction(-100) for _ in coordinates),
            tuple(Fraction(-101) for _ in coordinates),
        )
        for _ in range(20)
    )
    scaling = synthesize_rank_one_scenario_quotient_plan(
        scaling_components, payoff_additive_certified=True,
    )

    checks = {
        "opened_exact": bool(opened) and all(item["passed"] for item in opened),
        "opened_has_mixed_and_pure": any(item["strict"] for item in opened)
            and any(not item["strict"] for item in opened),
        "holdouts_exact": len(holdouts) == 50
            and all(item["passed"] for item in holdouts),
        "holdout_sizes_unseen": sorted(set(item["scenarios"] for item in holdouts))
            == list(HOLDOUT_SIZES),
        "rank_two_zero_false_accepts": false_accepts == 0,
        "endpoint_heuristic_falsified": actual_attack == Fraction(1, 2)
            and endpoint_heuristic == 1 and production_rejected_attack,
        "scaling_certificate": scaling.certificate_valid
            and scaling.scenario_count == 64
            and scaling.expanded_action_count == 4 ** 20
            and scaling.effective_scenario_count == 2
            and len(scaling.joint_actions) <= 2,
    }
    result = {
        "schema": "rank-one-scenario-quotient-v1",
        "seed": SEED,
        "opened": {
            "cases": len(opened),
            "strict": sum(item["strict"] for item in opened),
            "max_support": max(item["support"] for item in opened),
            "digest": digest_cases(opened),
        },
        "holdouts": {
            "cases": len(holdouts),
            "sizes": list(HOLDOUT_SIZES),
            "strict": sum(item["strict"] for item in holdouts),
            "max_support": max(item["support"] for item in holdouts),
            "digest": digest_cases(holdouts),
        },
        "falsification": {
            "rank_two_attacks": 100,
            "false_accepts": false_accepts,
            "endpoint_attack_actual": str(actual_attack),
            "endpoint_heuristic_claim": str(endpoint_heuristic),
            "production_rejected": production_rejected_attack,
        },
        "scaling": {
            "components": 20,
            "actions_per_component": 4,
            "scenarios": scaling.scenario_count,
            "expanded_actions": scaling.expanded_action_count,
            "effective_scenarios": scaling.effective_scenario_count,
            "support": len(scaling.joint_actions),
            "value": str(scaling.minimax_value),
            "valid": scaling.certificate_valid,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
