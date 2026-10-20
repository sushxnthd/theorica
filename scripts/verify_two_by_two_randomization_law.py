#!/usr/bin/env python3
"""Exact exhaustive verification of the protected-pairing criterion."""
import argparse
import hashlib
import json
from fractions import Fraction
from itertools import product

from theorica.agents.robust_provenance import solve_two_by_two_robust_game


def direct_value(matrix):
    (a, b), (c, d) = matrix
    candidates = (Fraction(0), Fraction(1))
    denominator = (a - c) + (d - b)
    if denominator:
        crossing = (d - c) / denominator
        if 0 < crossing < 1:
            candidates += (crossing,)
    scored = tuple((
        min(c + weight * (a - c), d + weight * (b - d)), weight
    ) for weight in candidates)
    return max(scored)[0]


def encode_matrix(matrix):
    return [[str(value) for value in row] for row in matrix]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    grid = tuple(Fraction(i, 4) for i in range(-4, 5))
    digest = hashlib.sha256()
    cases = strict = diagonal = anti_diagonal = equality = 0
    for entries in product(grid, repeat=4):
        matrix = (entries[:2], entries[2:])
        result = solve_two_by_two_robust_game(matrix)
        brute_value = direct_value(matrix)
        assert result.certificate_valid
        assert result.minimax_value == brute_value
        assert result.strict_randomization_advantage == (
            brute_value > result.best_pure_value
        )
        cases += 1
        strict += int(result.strict_randomization_advantage)
        diagonal += int(result.protected_pairing == "diagonal")
        anti_diagonal += int(result.protected_pairing == "anti_diagonal")
        equality += int(
            not result.strict_randomization_advantage
            and result.minimax_value == result.best_pure_value
        )
        digest.update(repr((matrix, result.action_probabilities,
                            result.minimax_value, result.protected_pairing)).encode())

    frozen_matrix = (
        (Fraction(1, 2), Fraction(1, 6)),
        (Fraction(1, 8), Fraction(3, 8)),
    )
    frozen = solve_two_by_two_robust_game(frozen_matrix)
    assert frozen.protected_pairing == "diagonal"
    assert frozen.action_probabilities == (Fraction(3, 7), Fraction(4, 7))
    assert frozen.minimax_value == Fraction(2, 7)
    assert frozen.best_pure_value == Fraction(1, 6)
    assert frozen.randomized_gain == Fraction(5, 42)

    result = {
        "schema": "theorica.two-by-two-randomization-law.primary.v1",
        "status": "pass",
        "exact_cases": cases,
        "strict_cases": strict,
        "diagonal_cases": diagonal,
        "anti_diagonal_cases": anti_diagonal,
        "pure_or_equality_cases": equality,
        "certificate_mismatches": 0,
        "value_digest": digest.hexdigest(),
        "minimality": {
            "one_action_strict_advantage_possible": False,
            "one_vertex_strict_advantage_possible": False,
            "two_by_two_witness": [["1", "0"], ["0", "1"]],
        },
        "frozen_prediction": {
            "matrix": encode_matrix(frozen_matrix),
            "protected_pairing": frozen.protected_pairing,
            "first_action_probability": str(frozen.action_probabilities[0]),
            "value": str(frozen.minimax_value),
            "best_pure": str(frozen.best_pure_value),
            "gain": str(frozen.randomized_gain),
            "status": "pass",
        },
        "smallest_claim": (
            "A two-action, two-vertex robust query game has strict randomized "
            "advantage iff one diagonal pairing strictly dominates both entries "
            "outside it; the exact policy and value then follow from the unique "
            "interior crossing."
        ),
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
