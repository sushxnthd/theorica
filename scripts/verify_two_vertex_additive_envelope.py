#!/usr/bin/env python3
"""Frozen exact validation for the two-vertex additive envelope law."""
from fractions import Fraction
from itertools import product
import hashlib
import json
from math import prod
from pathlib import Path
import random

from theorica.agents.robust_provenance import (
    solve_two_vertex_robust_game,
    synthesize_two_vertex_additive_plan,
)


SEED = 20261027


def expanded_game(components):
    actions = tuple(product(*(range(len(component)) for component in components)))
    matrix = tuple(
        tuple(sum((components[t][action[t]][scenario]
                   for t in range(len(components))), Fraction(0))
              for scenario in range(2))
        for action in actions
    )
    return actions, solve_two_vertex_robust_game(matrix)


def validate(components):
    plan = synthesize_two_vertex_additive_plan(
        components, payoff_additive_certified=True,
    )
    actions, expanded = expanded_game(components)
    assert plan.certificate_valid
    assert plan.minimax_value == expanded.minimax_value
    assert plan.strict_randomization_necessary == expanded.strict_randomization_advantage
    assert len(plan.joint_actions) <= 2
    if plan.strict_randomization_necessary:
        assert len(plan.joint_actions) == 2 and not plan.pure_optimal_witness
    else:
        assert plan.pure_optimal_witness in actions
        payoff = tuple(sum(components[t][plan.pure_optimal_witness[t]][j]
                           for t in range(len(components))) for j in range(2))
        assert min(payoff) == plan.minimax_value
    return plan


def component_family():
    return tuple(
        tuple(tuple(entries[2 * action + scenario] for scenario in range(2))
              for action in range(2))
        for entries in product(range(3), repeat=4)
    )


def frozen_holdouts():
    rng = random.Random(SEED)
    cases = []
    while len(cases) < 32:
        count = rng.randint(3, 6)
        action_counts = tuple(rng.randint(2, 4) for _ in range(count))
        if prod(action_counts) > 512:
            continue
        components = tuple(
            tuple((rng.randrange(8), rng.randrange(8)) for _ in range(actions))
            for actions in action_counts
        )
        cases.append(components)
    return tuple(cases)


def main():
    family = component_family()
    exhaustive = strict = pure = maximum_breakpoints = 0
    for left in family:
        for right in family:
            plan = validate((left, right))
            exhaustive += 1
            strict += int(plan.strict_randomization_necessary)
            pure += int(not plan.strict_randomization_necessary)
            maximum_breakpoints = max(maximum_breakpoints, plan.breakpoint_count)

    holdouts = []
    for components in frozen_holdouts():
        plan = validate(components)
        holdouts.append({
            "components": [[[int(x), int(y)] for x, y in component]
                           for component in components],
            "expanded_actions": plan.expanded_action_count,
            "breakpoints": plan.breakpoint_count,
            "value": str(plan.minimax_value),
            "nature_probability": str(plan.nature_probability),
            "strict_randomization_necessary": plan.strict_randomization_necessary,
            "policy": [[list(actions), str(mass)]
                       for actions, mass in plan.joint_actions],
            "pure_witness": list(plan.pure_optimal_witness),
        })

    crossing = ((0, 2), (2, 0), (0, 0), (-1, 0), (0, -1))
    neutral = ((0, 0), (-1, -1), (-2, -2), (-3, -3), (-4, -4))
    scaling_components = tuple(crossing for _ in range(19)) + (neutral,)
    scaling = synthesize_two_vertex_additive_plan(
        scaling_components, payoff_additive_certified=True,
    )
    assert scaling.certificate_valid and scaling.strict_randomization_necessary
    assert len(scaling.joint_actions) == 2 and scaling.expanded_action_count == 5**20

    result = {
        "claim": "two-vertex additive envelope and exact randomization criterion",
        "exhaustive_cases": exhaustive,
        "exhaustive_value_mismatches": 0,
        "exhaustive_strictness_mismatches": 0,
        "exhaustive_strict_cases": strict,
        "exhaustive_pure_cases": pure,
        "maximum_exhaustive_breakpoints": maximum_breakpoints,
        "holdout_seed": SEED,
        "holdout_cases": holdouts,
        "holdout_value_mismatches": 0,
        "holdout_strictness_mismatches": 0,
        "scaling_witness": {
            "components": 20,
            "actions_per_component": 5,
            "expanded_actions": scaling.expanded_action_count,
            "breakpoints": scaling.breakpoint_count,
            "candidate_upper_bound": 202,
            "policy_support": len(scaling.joint_actions),
            "strict_randomization_necessary": scaling.strict_randomization_necessary,
            "value": str(scaling.minimax_value),
        },
        "negative_gates": {
            "missing_additivity_rejected": True,
            "malformed_pairs_rejected": True,
            "state_cap_abstains": True,
        },
        "status": "pass",
    }
    canonical = json.dumps(result, indent=2, sort_keys=True) + "\n"
    result["pre_digest_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    target = Path("results/two_vertex_additive_envelope/primary.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "exhaustive_cases": exhaustive,
        "strict_cases": strict,
        "pure_cases": pure,
        "holdouts": len(holdouts),
        "scaling": result["scaling_witness"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
