#!/usr/bin/env python3
"""Independent exact audit; intentionally imports no production code."""
import argparse
import hashlib
import json
from fractions import Fraction
from itertools import product


def direct(matrix):
    (a, b), (c, d) = matrix
    pure = max(min(a, b), min(c, d))
    denominator = (a - c) + (d - b)
    candidates = (Fraction(0), Fraction(1))
    if denominator:
        crossing = (d - c) / denominator
        if 0 < crossing < 1:
            candidates += (crossing,)
    scored = tuple((min(c + weight * (a - c), d + weight * (b - d)), weight)
                   for weight in candidates)
    value, weight = max(scored)
    diagonal = min(a, d) > max(b, c)
    anti_diagonal = min(b, c) > max(a, d)
    pairing = "diagonal" if diagonal else "anti_diagonal" if anti_diagonal else "none"
    if value == pure:
        weight = Fraction(int(min(a, b) >= min(c, d)))
    return value, pure, weight, pairing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with open(args.primary, encoding="utf-8") as handle:
        primary = json.load(handle)
    grid = tuple(Fraction(i, 4) for i in range(-4, 5))
    digest = hashlib.sha256()
    cases = strict = diagonal = anti_diagonal = equality = 0
    for entries in product(grid, repeat=4):
        matrix = (entries[:2], entries[2:])
        value, pure, first_weight, pairing = direct(matrix)
        criterion = (
            min(matrix[0][0], matrix[1][1]) > max(matrix[0][1], matrix[1][0])
            or min(matrix[0][1], matrix[1][0]) > max(matrix[0][0], matrix[1][1])
        )
        assert criterion == (value > pure)
        probabilities = (first_weight, 1 - first_weight)
        cases += 1
        strict += int(value > pure)
        diagonal += int(pairing == "diagonal")
        anti_diagonal += int(pairing == "anti_diagonal")
        equality += int(value == pure)
        digest.update(repr((matrix, probabilities, value, pairing)).encode())
    assert primary["exact_cases"] == cases
    assert primary["strict_cases"] == strict
    assert primary["diagonal_cases"] == diagonal
    assert primary["anti_diagonal_cases"] == anti_diagonal
    assert primary["pure_or_equality_cases"] == equality
    assert primary["value_digest"] == digest.hexdigest()
    assert primary["frozen_prediction"]["status"] == "pass"
    result = {
        "schema": "theorica.two-by-two-randomization-law.audit.v1",
        "status": "pass",
        "independent": True,
        "exact_cases": cases,
        "strict_cases": strict,
        "criterion_mismatches": 0,
        "value_digest": digest.hexdigest(),
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
