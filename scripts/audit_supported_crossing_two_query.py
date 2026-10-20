#!/usr/bin/env python3
"""Independent all-intersection audit; imports no production code."""
import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations, product


def solve(matrix):
    candidates = {Fraction(0), Fraction(1)}
    for j, k in combinations(range(len(matrix[0])), 2):
        sj = matrix[0][j] - matrix[1][j]
        sk = matrix[0][k] - matrix[1][k]
        if sj != sk:
            x = (matrix[1][k] - matrix[1][j]) / (sj - sk)
            if 0 < x < 1:
                candidates.add(x)
    scored = [(min(x * matrix[0][j] + (1 - x) * matrix[1][j]
                   for j in range(len(matrix[0]))), x) for x in candidates]
    value = max(v for v, _ in scored)
    weight = min(x for v, x in scored if v == value)
    pure = max(min(matrix[0]), min(matrix[1]))
    if value == pure:
        weight = Fraction(int(min(matrix[0]) > min(matrix[1])))
    return value, weight, value > pure


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--primary', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    with open(args.primary, encoding='utf-8') as handle:
        primary = json.load(handle)
    grid = tuple(Fraction(x) for x in range(3))
    digest = hashlib.sha256()
    total = strict = 0
    by_vertices = {}
    for m in (3, 4):
        cases = strict_cases = 0
        for entries in product(grid, repeat=2 * m):
            matrix = (entries[:m], entries[m:])
            value, weight, is_strict = solve(matrix)
            probabilities = (weight, 1 - weight)
            digest.update(repr((matrix, probabilities, value, is_strict)).encode())
            cases += 1
            strict_cases += int(is_strict)
            total += 1
            strict += int(is_strict)
        by_vertices[str(m)] = {'cases': cases, 'strict_cases': strict_cases}
    assert primary['exact_cases'] == total
    assert primary['strict_cases'] == strict
    assert primary['by_vertices'] == by_vertices
    assert primary['value_digest'] == digest.hexdigest()
    assert primary['value_or_policy_mismatches'] == 0
    result = {
        'schema': 'theorica.supported-crossing-two-query.audit.v1',
        'status': 'pass',
        'independent': True,
        'exact_cases': total,
        'strict_cases': strict,
        'by_vertices': by_vertices,
        'mismatches': 0,
        'value_digest': digest.hexdigest(),
    }
    with open(args.output, 'w', encoding='utf-8') as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write('\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
