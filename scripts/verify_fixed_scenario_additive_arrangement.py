"""Frozen exact five-scenario test of the generic additive arrangement law."""
from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

from theorica.agents.robust_provenance import synthesize_fixed_scenario_additive_plan

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "fixed_scenario_additive_arrangement" / "primary.json"
PERMUTATIONS = tuple(permutations(range(5)))


def solve(rows, rhs):
    n = len(rows)
    matrix = [list(rows[i]) + [rhs[i]] for i in range(n)]
    for column in range(n):
        pivot = next((row for row in range(column, n) if matrix[row][column]), None)
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        scale = matrix[column][column]
        matrix[column] = [value / scale for value in matrix[column]]
        for row in range(n):
            if row == column or matrix[row][column] == 0:
                continue
            scale = matrix[row][column]
            matrix[row] = [matrix[row][i] - scale * matrix[column][i]
                           for i in range(n + 1)]
    return tuple(matrix[row][-1] for row in range(n))


def exact_expanded_value(actions):
    actions = tuple(sorted(set(
        tuple(Fraction(value) for value in action) for action in actions
    )))
    actions = tuple(
        action for action in actions
        if not any(
            all(other[i] >= action[i] for i in range(5))
            and any(other[i] > action[i] for i in range(5))
            for other in actions
        )
    )
    dimension = 4
    ties = set()
    for left, right in combinations(actions, 2):
        row = tuple((left[i] - left[-1]) - (right[i] - right[-1])
                    for i in range(dimension))
        if any(row):
            ties.add((row, right[-1] - left[-1]))
    facets = tuple(
        (tuple(Fraction(int(i == j)) for i in range(dimension)), Fraction(0))
        for j in range(dimension)
    ) + ((tuple(Fraction(1) for _ in range(dimension)), Fraction(1)),)
    points = set()
    for selected in combinations(tuple(ties) + facets, dimension):
        point = solve(tuple(item[0] for item in selected),
                      tuple(item[1] for item in selected))
        if point is not None and all(value >= 0 for value in point) \
                and sum(point) <= 1:
            points.add(point)
    if not points:
        raise RuntimeError("expanded arrangement has no feasible point")

    def score(point):
        last = 1 - sum(point)
        return max(sum((point[i] * action[i] for i in range(dimension)),
                       Fraction(0)) + last * action[-1] for action in actions)

    point = min(points, key=lambda candidate: (score(candidate), candidate))
    value = score(point)
    return value, max(min(action) for action in actions) < value


def expanded_actions(components):
    return tuple(
        tuple(sum((components[t][choice[t]][scenario]
                   for t in range(len(components))), Fraction(0))
              for scenario in range(5))
        for choice in product(*(range(len(component)) for component in components))
    )


def canonical(contrasts):
    def action_unordered(vector):
        complement = tuple(1 - value for value in vector)
        return min(tuple(vector), complement)

    return min(
        tuple(sorted(action_unordered(tuple(vector[i] for i in permutation))
                     for vector in contrasts))
        for permutation in PERMUTATIONS
    )


def evaluate(components):
    joint = expanded_actions(components)
    exact, strict = exact_expanded_value(joint)
    plan = synthesize_fixed_scenario_additive_plan(
        components, payoff_additive_certified=True,
    )
    return {
        "value": str(exact),
        "strict": strict,
        "production_value": str(plan.minimax_value),
        "production_strict": plan.strict_randomization_necessary,
        "support": len(plan.joint_actions),
        "valid": plan.certificate_valid,
        "candidates": plan.arrangement_candidate_count,
        "candidate_bound": plan.candidate_upper_bound,
        "expanded_actions": plan.expanded_action_count,
    }


def frozen_holdouts():
    rng = random.Random(20261024)
    cases = []
    for index in range(25):
        scale = 5 + index % 4
        basis = tuple(tuple(scale if i == j else 0 for i in range(5))
                      for j in range(5))
        offset = ((index % 7,) * 5,)
        cases.append(("strict", (basis, offset)))
    for index in range(25):
        components = []
        for actions in (3, 2):
            dominant = tuple(8 + index % 5 for _ in range(5))
            alternatives = tuple(tuple(rng.randrange(-4, 8) for _ in range(5))
                                 for _ in range(actions - 1))
            components.append((dominant,) + alternatives)
        cases.append(("pure", tuple(components)))
    return tuple(cases)


def main():
    vectors = tuple(product(range(2), repeat=5))
    ordered = tuple(product(vectors, repeat=3))
    keys = sorted({canonical(case) for case in ordered})
    cache = {
        key: evaluate(tuple((vector, tuple(1 - value for value in vector))
                            for vector in key))
        for key in keys
    }
    digest = hashlib.sha256()
    mismatches = strict_cases = max_support = 0
    for case in ordered:
        item = cache[canonical(case)]
        mismatch = not (
            item["value"] == item["production_value"]
            and item["strict"] == item["production_strict"]
            and item["valid"]
            and item["support"] <= 5
            and item["candidates"] <= item["candidate_bound"]
        )
        mismatches += int(mismatch)
        strict_cases += int(item["strict"])
        max_support = max(max_support, item["support"])
        digest.update(f"{case}|{item['value']}|{int(item['strict'])}|"
                      f"{item['support']}\n".encode())

    holdouts = []
    for expected, components in frozen_holdouts():
        item = evaluate(components)
        item["expected_class"] = expected
        item["components"] = components
        item["passed"] = (
            item["value"] == item["production_value"]
            and item["strict"] == item["production_strict"]
            and item["valid"]
            and item["support"] <= 5
            and ((expected == "strict") == item["strict"])
        )
        holdouts.append(item)

    scaling = (
        tuple(tuple(4 if i == action else 0 for i in range(5))
              for action in range(4)),
    ) + tuple(
        tuple(tuple(level for _ in range(5))
              for level in range(component + 4, component, -1))
        for component in range(1, 15)
    )
    scaling_plan = synthesize_fixed_scenario_additive_plan(
        scaling, payoff_additive_certified=True,
    )
    result = {
        "schema": "fixed-scenario-additive-arrangement-v1",
        "seed": 20261024,
        "opened": {
            "cases": len(ordered),
            "symmetry_classes": len(keys),
            "mismatches": mismatches,
            "strict_randomization_cases": strict_cases,
            "pure_optimal_cases": len(ordered) - strict_cases,
            "max_support": max_support,
            "digest": digest.hexdigest(),
        },
        "holdouts": holdouts,
        "holdout_summary": {
            "cases": len(holdouts),
            "mismatches": sum(not item["passed"] for item in holdouts),
            "strict_randomization_cases": sum(item["strict"] for item in holdouts),
            "pure_optimal_cases": sum(not item["strict"] for item in holdouts),
            "max_support": max(item["support"] for item in holdouts),
        },
        "scaling_witness": {
            "scenarios": 5,
            "components": 15,
            "actions_per_component": 4,
            "expanded_actions": scaling_plan.expanded_action_count,
            "tie_hyperplanes": scaling_plan.tie_hyperplane_count,
            "arrangement_candidates": scaling_plan.arrangement_candidate_count,
            "candidate_upper_bound": scaling_plan.candidate_upper_bound,
            "support": len(scaling_plan.joint_actions),
            "value": str(scaling_plan.minimax_value),
            "valid": scaling_plan.certificate_valid,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "opened": result["opened"],
        "holdout_summary": result["holdout_summary"],
        "scaling_witness": result["scaling_witness"],
    }, indent=2, sort_keys=True))
    if mismatches or result["holdout_summary"]["mismatches"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
