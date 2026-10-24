#!/usr/bin/env python3
"""Frozen exact validation for the coupled-additive minimax correction."""
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path
import random

from theorica.agents.robust_provenance import synthesize_coupled_additive_plan


def solve(rows, rhs):
    n = len(rows)
    a = [list(rows[i]) + [rhs[i]] for i in range(n)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col]), None)
        if pivot is None:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        a[col] = [x / scale for x in a[col]]
        for row in range(n):
            if row == col or not a[row][col]:
                continue
            scale = a[row][col]
            a[row] = [a[row][j] - scale * a[col][j] for j in range(n + 1)]
    return tuple(a[i][-1] for i in range(n))


def expanded_value(matrices, vertices):
    actions = tuple(product(*(range(len(matrix)) for matrix in matrices)))
    payoff = tuple(tuple(sum(matrices[t][action[t]][vertex[t]]
                               for t in range(len(matrices))) for vertex in vertices)
                   for action in actions)
    d = len(actions)
    planes = []
    for action in range(d - 1):
        row = [Fraction(0)] * d
        row[action] = 1
        planes.append((tuple(row), Fraction(0)))
    planes.append((tuple([Fraction(1)] * (d - 1) + [Fraction(0)]), Fraction(1)))
    for j in range(len(vertices)):
        row = [Fraction(0)] * d
        base = Fraction(payoff[-1][j])
        for action in range(d - 1):
            row[action] = -(Fraction(payoff[action][j]) - base)
        row[-1] = 1
        planes.append((tuple(row), base))
    best = None
    for chosen in combinations(range(len(planes)), d):
        x = solve(tuple(planes[i][0] for i in chosen),
                  tuple(planes[i][1] for i in chosen))
        if x is None:
            continue
        masses = x[:-1] + (Fraction(1) - sum(x[:-1], Fraction(0)),)
        if any(mass < 0 for mass in masses):
            continue
        floor = min(sum(masses[a] * payoff[a][j] for a in range(d))
                    for j in range(len(vertices)))
        if x[-1] <= floor and (best is None or x[-1] > best):
            best = x[-1]
    assert best is not None
    return best


def games():
    return tuple(tuple(tuple(entries[2 * r + c] for c in range(2)) for r in range(2))
                 for entries in product(range(3), repeat=4))


def validate(matrices, vertices):
    plan = synthesize_coupled_additive_plan(
        matrices, vertices, payoff_additive_certified=True,
    )
    assert plan.certificate_valid
    assert plan.minimax_value == expanded_value(matrices, vertices)
    assert (plan.coupling_bonus == 0) == plan.rectangular_value_survives
    assert (plan.coupling_bonus == 0) == bool(plan.zero_bonus_nature_witness)
    assert len(plan.joint_components) <= plan.support_bound
    return plan


def main():
    family = games()
    universe = tuple(product(range(2), repeat=2))
    subsets = tuple(tuple(universe[i] for i in range(4) if mask & (1 << i))
                    for mask in range(1, 16))
    cases = zero = strict = proper_zero = proper_strict = 0
    maximum_bonus = Fraction(0)
    maximum_support = 0
    buckets = {size: {"cases": 0, "zero_bonus": 0, "strict_bonus": 0}
               for size in range(1, 5)}
    for left in family:
        for right in family:
            for vertices in subsets:
                plan = validate((left, right), vertices)
                cases += 1
                is_zero = plan.coupling_bonus == 0
                zero += int(is_zero)
                strict += int(not is_zero)
                proper_zero += int(is_zero and len(vertices) < 4)
                proper_strict += int(not is_zero and len(vertices) < 4)
                maximum_bonus = max(maximum_bonus, plan.coupling_bonus)
                maximum_support = max(maximum_support, len(plan.joint_components))
                buckets[len(vertices)]["cases"] += 1
                buckets[len(vertices)]["zero_bonus"] += int(is_zero)
                buckets[len(vertices)]["strict_bonus"] += int(not is_zero)

    rng = random.Random(20261026)
    holdouts = []
    holdout_universe = tuple(product(range(2), repeat=3))
    for _ in range(32):
        matrices = tuple(tuple(tuple(rng.randrange(5) for _ in range(2))
                               for _ in range(2)) for _ in range(3))
        vertices = tuple(sorted(rng.sample(holdout_universe, rng.randrange(2, 5))))
        plan = validate(matrices, vertices)
        holdouts.append({
            "value": str(plan.minimax_value),
            "rectangular_baseline": str(plan.rectangular_baseline_value),
            "coupling_bonus": str(plan.coupling_bonus),
            "expanded_actions": plan.expanded_action_count,
            "reduced_variables": plan.reduced_variable_count,
            "policy_support": len(plan.joint_components),
        })

    crossing = ((0, 2), (2, 0))
    scaling = synthesize_coupled_additive_plan(
        tuple(crossing for _ in range(6)), ((0,) * 6, (1,) * 6),
        payoff_additive_certified=True,
    )
    assert scaling.certificate_valid and scaling.minimax_value == 6
    assert scaling.expanded_action_count == 64 and scaling.reduced_variable_count == 7
    assert (cases, zero, strict, proper_zero, proper_strict) == (
        98415, 60903, 37512, 54342, 37512,
    )

    result = {
        "claim": "coupled-additive marginal minimax law and exact zero-bonus criterion",
        "exhaustive_cases": cases,
        "expanded_value_mismatches": 0,
        "criterion_mismatches": 0,
        "zero_bonus_cases": zero,
        "strict_bonus_cases": strict,
        "proper_nonrectangular_zero_bonus_cases": proper_zero,
        "proper_nonrectangular_strict_bonus_cases": proper_strict,
        "maximum_coupling_bonus": str(maximum_bonus),
        "maximum_policy_support": maximum_support,
        "by_coupled_vertex_count": buckets,
        "prospective_seed": 20261026,
        "prospective_cases": holdouts,
        "scaling_witness": {
            "expanded_actions": 64, "reduced_variables": 7,
            "value": str(scaling.minimax_value),
        },
        "status": "pass",
    }
    target = Path("results/coupled_additive_minimax/primary.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
