#!/usr/bin/env python3
"""Frozen exact enumeration for the two-vertex sparse-support law."""
import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations, product

from theorica.agents.robust_provenance import solve_two_vertex_robust_game


def exact_oracle(matrix):
    """Enumerate primal supports and the independent two-column dual."""
    n = len(matrix)
    pure_values = tuple(min(row) for row in matrix)
    pure = max(pure_values)
    pure_index = min(i for i, value in enumerate(pure_values) if value == pure)
    primal = [(pure, (pure_index,), (Fraction(1),))]
    for left, right in combinations(range(n), 2):
        dl = matrix[left][0] - matrix[left][1]
        dr = matrix[right][0] - matrix[right][1]
        if dl * dr >= 0:
            continue
        weight = dr / (dr - dl)
        value = weight * matrix[left][0] + (1 - weight) * matrix[right][0]
        primal.append((value, (left, right), (weight, 1 - weight)))
    value = max(item[0] for item in primal)
    if value == pure:
        support, weights = (pure_index,), (Fraction(1),)
    else:
        _, support, weights = min(item for item in primal if item[0] == value)
    probabilities = tuple(
        weights[support.index(i)] if i in support else Fraction(0) for i in range(n)
    )

    dual_candidates = {Fraction(0), Fraction(1)}
    for left, right in combinations(range(n), 2):
        sl = matrix[left][0] - matrix[left][1]
        sr = matrix[right][0] - matrix[right][1]
        if sl == sr:
            continue
        q = (matrix[right][1] - matrix[left][1]) / (sl - sr)
        if 0 <= q <= 1:
            dual_candidates.add(q)
    scored = tuple((max(q * a + (1 - q) * b for a, b in matrix), q)
                   for q in dual_candidates)
    dual_value = min(item[0] for item in scored)
    q = min(item[1] for item in scored if item[0] == dual_value)
    assert dual_value == value
    return value, probabilities, (q, 1 - q), value > pure


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    grid = tuple(Fraction(x) for x in range(3))
    digest = hashlib.sha256()
    by_actions = {}
    total = strict = 0
    for action_count in (3, 4):
        cases = strict_cases = 0
        for entries in product(grid, repeat=2 * action_count):
            matrix = tuple((entries[2 * i], entries[2 * i + 1])
                           for i in range(action_count))
            solved = solve_two_vertex_robust_game(matrix)
            value, probabilities, dual, is_strict = exact_oracle(matrix)
            assert solved.certificate_valid
            assert solved.minimax_value == value
            assert solved.action_probabilities == probabilities
            assert solved.ambiguity_probabilities == dual
            assert solved.strict_randomization_advantage == is_strict
            assert len(solved.supported_actions) <= 2
            digest.update(repr((matrix, probabilities, dual, value, is_strict)).encode())
            cases += 1
            strict_cases += int(is_strict)
            total += 1
            strict += int(is_strict)
        by_actions[str(action_count)] = {"cases": cases, "strict_cases": strict_cases}

    frozen = solve_two_vertex_robust_game(((0, 2), (2, 0), (0, 0)))
    dominated = solve_two_vertex_robust_game(
        ((0, 2), (2, 0), (0, 0), (Fraction(1, 4), Fraction(1, 4)))
    )
    overriding = solve_two_vertex_robust_game(
        ((0, 2), (2, 0), (0, 0), (Fraction(3, 2), Fraction(3, 2)))
    )
    assert frozen.minimax_value == dominated.minimax_value == 1
    assert frozen.action_probabilities == dominated.action_probabilities[:3]
    assert overriding.minimax_value == Fraction(3, 2)
    assert not overriding.strict_randomization_advantage

    result = {
        "schema": "theorica.two-vertex-sparse-support.primary.v1",
        "status": "pass",
        "exact_cases": total,
        "strict_cases": strict,
        "by_actions": by_actions,
        "value_policy_dual_mismatches": 0,
        "support_bound_mismatches": 0,
        "certificate_mismatches": 0,
        "value_digest": digest.hexdigest(),
        "frozen_prediction": {
            "strict_probabilities": [str(x) for x in frozen.action_probabilities],
            "strict_dual": [str(x) for x in frozen.ambiguity_probabilities],
            "strict_value": str(frozen.minimax_value),
            "dominated_append_value": str(dominated.minimax_value),
            "overriding_append_value": str(overriding.minimax_value),
            "overriding_is_pure": not overriding.strict_randomization_advantage,
            "status": "pass",
        },
        "smallest_claim": (
            "For any finite robust game with exactly two ambiguity vertices, "
            "an optimal query plan uses at most two actions; strict mixing occurs "
            "exactly at the highest diagonal-crossing segment above every pure value."
        ),
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
