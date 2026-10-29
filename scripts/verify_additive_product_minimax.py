#!/usr/bin/env python3
"""Frozen exact validation for the additive rectangular-product law."""
from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import random

from theorica.agents.robust_provenance import synthesize_additive_product_plan


def matrices(rows: int, columns: int, alphabet: range):
    for entries in product(alphabet, repeat=rows * columns):
        yield tuple(tuple(entries[r * columns + c] for c in range(columns))
                    for r in range(rows))


def expanded_payoff(component_matrices):
    action_ranges = tuple(range(len(matrix)) for matrix in component_matrices)
    vertex_ranges = tuple(range(len(matrix[0])) for matrix in component_matrices)
    actions = tuple(product(*action_ranges))
    vertices = tuple(product(*vertex_ranges))
    return actions, vertices, tuple(
        tuple(sum(component_matrices[t][action[t]][vertex[t]]
                  for t in range(len(component_matrices))) for vertex in vertices)
        for action in actions
    )


def validate(component_matrices):
    plan = synthesize_additive_product_plan(
        component_matrices,
        payoff_additive_certified=True,
        ambiguity_rectangular_certified=True,
    )
    actions, vertices, matrix = expanded_payoff(plan.component_payoff_matrices)
    joint = {action: mass for action, mass in plan.joint_components}
    realized = tuple(sum(joint.get(action, 0) * matrix[i][j]
                         for i, action in enumerate(actions)) for j in range(len(vertices)))
    assert plan.certificate_valid
    assert min(realized) == plan.minimax_value
    assert plan.best_pure_value == max(min(row) for row in matrix)
    assert plan.randomized_gain == sum(
        (plan.component_values[t] - plan.component_best_pure_values[t]
         for t in range(len(component_matrices))), Fraction(0)
    )
    assert plan.strict_randomization_advantage == any(
        plan.component_values[t] > plan.component_best_pure_values[t]
        for t in range(len(component_matrices))
    )
    assert len(plan.joint_components) <= plan.support_bound
    return plan


def main():
    alphabet = range(3)
    games_2x2 = tuple(matrices(2, 2, alphabet))
    strict_pairs = 0
    max_support = 0
    for left in games_2x2:
        for right in games_2x2:
            plan = validate((left, right))
            strict_pairs += int(plan.strict_randomization_advantage)
            max_support = max(max_support, len(plan.joint_components))

    mixed = (
        (((0, 3, 1), (3, 0, 1)), ((0, 2), (2, 0), (1, 1))),
        (((1, 0, 3), (0, 2, 1)), ((2, 0), (0, 2), (1, 1))),
        (((0, 2), (2, 0), (1, 1)), ((0, 4, 1), (4, 0, 1))),
    )
    mixed_summaries = []
    for family in mixed:
        plan = validate(family)
        mixed_summaries.append({
            "value": str(plan.minimax_value),
            "best_pure": str(plan.best_pure_value),
            "support": len(plan.joint_components),
            "bound": plan.support_bound,
        })

    rng = random.Random(20261025)
    holdout_summaries = []
    for _ in range(24):
        family = tuple(tuple(tuple(rng.randrange(5) for _ in range(2)) for _ in range(2))
                       for _ in range(3))
        plan = validate(family)
        holdout_summaries.append({
            "value": str(plan.minimax_value),
            "strict": plan.strict_randomization_advantage,
            "support": len(plan.joint_components),
            "bound": plan.support_bound,
        })

    # Frozen assumption-boundary witnesses.
    crossing = ((0, 2), (2, 0))
    component_sum = validate((crossing, crossing)).minimax_value
    _, _, rectangular_matrix = expanded_payoff((crossing, crossing))
    # With only joint ambiguity vertex (0,0), the value is 4 rather than 2.
    nonrectangular_value = max(row[0] for row in rectangular_matrix)
    assert component_sum == 2 and nonrectangular_value == 4
    # Zero additive factors plus parity interaction has value 1/2, not 0.
    parity_rows = tuple(tuple(Fraction(int((a[0] ^ a[1]) == (b[0] ^ b[1])))
                              for b in product(range(2), repeat=2))
                        for a in product(range(2), repeat=2))
    parity_plan = synthesize_additive_product_plan(
        (((0, 0), (0, 0)), ((0, 0), (0, 0))),
        payoff_additive_certified=True, ambiguity_rectangular_certified=True,
    )
    assert parity_plan.minimax_value == 0
    # Uniform actions guarantee 1/2; uniform vertices cap every action at 1/2.
    assert min(sum(row[j] for row in parity_rows) / 4 for j in range(4)) == Fraction(1, 2)
    assert max(sum(row) / 4 for row in parity_rows) == Fraction(1, 2)

    result = {
        "claim": "additive rectangular-product minimax law",
        "exhaustive_two_factor_2x2_cases": len(games_2x2) ** 2,
        "strict_pairs": strict_pairs,
        "maximum_realized_joint_support": max_support,
        "selected_mixed_dimension_cases": mixed_summaries,
        "frozen_three_factor_seed": 20261025,
        "frozen_three_factor_cases": holdout_summaries,
        "assumption_boundaries": {
            "nonrectangular_component_sum": str(component_sum),
            "nonrectangular_actual_value": str(nonrectangular_value),
            "cross_term_additive_prediction": "0",
            "cross_term_uniform_lower_bound": "1/2",
        },
        "status": "pass",
    }
    target = Path("results/additive_product_minimax/primary.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
