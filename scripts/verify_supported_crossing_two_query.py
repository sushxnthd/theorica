#!/usr/bin/env python3
"""Frozen exact enumeration for the two-action supported-crossing law."""
import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations, product

from theorica.agents.robust_provenance import solve_two_action_robust_game


def brute(matrix):
    candidates = {Fraction(0), Fraction(1)}
    for left, right in combinations(range(len(matrix[0])), 2):
        s_left = matrix[0][left] - matrix[1][left]
        s_right = matrix[0][right] - matrix[1][right]
        if s_left != s_right:
            crossing = (matrix[1][right] - matrix[1][left]) / (s_left - s_right)
            if 0 < crossing < 1:
                candidates.add(crossing)
    scored = tuple((min(
        weight * matrix[0][j] + (1 - weight) * matrix[1][j]
        for j in range(len(matrix[0]))
    ), weight) for weight in candidates)
    value = max(item[0] for item in scored)
    weight = min(item[1] for item in scored if item[0] == value)
    endpoint_values = (min(matrix[1]), min(matrix[0]))
    if value == max(endpoint_values):
        weight = Fraction(int(endpoint_values[1] > endpoint_values[0]))
    return value, weight


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    grid = tuple(Fraction(x) for x in range(3))
    digest = hashlib.sha256()
    by_vertices = {}
    total = strict = 0
    for vertex_count in (3, 4):
        cases = strict_cases = 0
        for entries in product(grid, repeat=2 * vertex_count):
            matrix = (entries[:vertex_count], entries[vertex_count:])
            solved = solve_two_action_robust_game(matrix)
            value, weight = brute(matrix)
            assert solved.certificate_valid
            assert solved.minimax_value == value
            assert solved.action_probabilities[0] == weight
            assert solved.strict_randomization_advantage == (value > solved.best_pure_value)
            if solved.strict_randomization_advantage:
                assert len(solved.supported_vertices) == 2
            cases += 1
            strict_cases += int(solved.strict_randomization_advantage)
            total += 1
            strict += int(solved.strict_randomization_advantage)
            digest.update(repr((matrix, solved.action_probabilities,
                                solved.minimax_value,
                                solved.strict_randomization_advantage)).encode())
        by_vertices[str(vertex_count)] = {'cases': cases, 'strict_cases': strict_cases}

    frozen = solve_two_action_robust_game((
        (Fraction(1, 2), Fraction(1, 6), Fraction(1)),
        (Fraction(1, 8), Fraction(3, 8), Fraction(1)),
    ))
    assert frozen.action_probabilities == (Fraction(3, 7), Fraction(4, 7))
    assert frozen.minimax_value == Fraction(2, 7)
    assert frozen.best_pure_value == Fraction(1, 6)
    assert frozen.supported_vertices == (0, 1)
    undercut = solve_two_action_robust_game((
        (Fraction(1, 2), Fraction(1, 6), Fraction(0)),
        (Fraction(1, 8), Fraction(3, 8), Fraction(0)),
    ))
    assert not undercut.strict_randomization_advantage and undercut.minimax_value == 0

    # Every strict 2x2 grid game survives addition of a constant slack vertex.
    slack_cases = 0
    for entries in product(grid, repeat=4):
        base = (entries[:2], entries[2:])
        solved = solve_two_action_robust_game(base)
        if not solved.strict_randomization_advantage:
            continue
        slack_value = solved.minimax_value + 1
        extended = solve_two_action_robust_game((
            base[0] + (slack_value,), base[1] + (slack_value,),
        ))
        assert extended.minimax_value == solved.minimax_value
        assert extended.action_probabilities == solved.action_probabilities
        assert extended.strict_randomization_advantage
        slack_cases += 1

    result = {
        'schema': 'theorica.supported-crossing-two-query.primary.v1',
        'status': 'pass',
        'exact_cases': total,
        'strict_cases': strict,
        'by_vertices': by_vertices,
        'value_or_policy_mismatches': 0,
        'certificate_mismatches': 0,
        'slack_vertex_preservation_cases': slack_cases,
        'value_digest': digest.hexdigest(),
        'frozen_prediction': {
            'first_action_probability': str(frozen.action_probabilities[0]),
            'value': str(frozen.minimax_value),
            'best_pure': str(frozen.best_pure_value),
            'supported_vertices': list(frozen.supported_vertices),
            'undercut_value': str(undercut.minimax_value),
            'status': 'pass',
        },
        'smallest_claim': (
            'For two query actions and finitely many ambiguity vertices, strict '
            'randomization occurs exactly at an interior lower-envelope crossing '
            'supported by all remaining vertices with active slopes bracketing zero.'
        ),
    }
    with open(args.output, 'w', encoding='utf-8') as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write('\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
