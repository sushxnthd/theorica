#!/usr/bin/env python3
"""Independent Fraction-only audit of decision-identifiable list decoding."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

OUT = Path("results/decision_identifiable_list_decoding/independent_audit.json")


def solve_square(rows, rhs):
    n = len(rows)
    matrix = [
        [Fraction(value) for value in rows[i]] + [Fraction(rhs[i])]
        for i in range(n)
    ]
    for column in range(n):
        pivot = next((row for row in range(column, n) if matrix[row][column]), None)
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        scale = matrix[column][column]
        matrix[column] = [value / scale for value in matrix[column]]
        for row in range(n):
            if row == column:
                continue
            scale = matrix[row][column]
            matrix[row] = [
                matrix[row][j] - scale * matrix[column][j] for j in range(n + 1)
            ]
    return tuple(row[-1] for row in matrix)


def action_candidates(features, observations, action):
    rank = len(features[0])
    candidates = {}
    for basis in combinations(range(len(features)), rank):
        coefficients = solve_square(
            tuple(features[index] for index in basis),
            tuple(observations[index][action] for index in basis),
        )
        if coefficients is None:
            continue
        prediction = tuple(
            sum((a * b for a, b in zip(row, coefficients)), Fraction(0))
            for row in features
        )
        disagreements = frozenset(
            index for index in range(len(features))
            if prediction[index] != observations[index][action]
        )
        if len(disagreements) <= 1:
            candidates[prediction] = disagreements
    return tuple(candidates.items())


def game_solution(game):
    lines = tuple((left - right, right) for left, right in zip(*game))
    candidates = {Fraction(0), Fraction(1)}
    for first, second in combinations(lines, 2):
        if first[0] == second[0]:
            continue
        crossing = (second[1] - first[1]) / (first[0] - second[0])
        if 0 <= crossing <= 1:
            candidates.add(crossing)
    payoff = lambda p: min(slope * p + intercept for slope, intercept in lines)
    value = max(payoff(p) for p in candidates)
    lower, upper = Fraction(0), Fraction(1)
    for slope, intercept in lines:
        if slope > 0:
            lower = max(lower, (value - intercept) / slope)
        elif slope < 0:
            upper = min(upper, (value - intercept) / slope)
    return value, (lower, upper)


def classify(features, observations):
    candidates = (action_candidates(features, observations, 0),
                  action_candidates(features, observations, 1))
    games = []
    for left, right in product(*candidates):
        if len(left[1] | right[1]) <= 1 and (left[0], right[0]) not in games:
            games.append((left[0], right[0]))
    solutions = tuple(game_solution(game) for game in games)
    values = {solution[0] for solution in solutions}
    lower = max(solution[1][0] for solution in solutions)
    upper = min(solution[1][1] for solution in solutions)
    return len(games), len(values) == 1, len(values) == 1 and lower <= upper


def main():
    transcript = []
    positive = attacks = 0
    for case in range(40):
        shift, delta = Fraction(3 * case - 41, 7), Fraction(case + 1, 11)
        features = ((1, 0), (1, 1), (1, 2))
        observations = ((shift, shift), (shift, shift), (shift, shift + delta))
        result = classify(features, observations)
        positive += int(result[0] == 3 and result[1] and result[2])
        transcript.append(("affine", case, result))
    for case in range(20):
        index = 100 + case
        shift, delta = Fraction(3 * index - 41, 7), Fraction(index + 1, 11)
        features = tuple((1, x, x * x) for x in range(4))
        observations = ((shift, shift),) * 3 + ((shift, shift + delta),)
        result = classify(features, observations)
        positive += int(result[0] == 4 and result[1] and result[2])
        transcript.append(("quadratic", case, result))
    for case in range(20):
        shift, scale = Fraction(case - 13, 5), Fraction(case + 2, 9)
        features = ((1, 0), (1, 1), (1, 2))
        unequal = ((shift, shift), (shift, shift),
                   (shift + scale, shift + scale))
        first = classify(features, unequal)
        attacks += int(not first[1] and not first[2])
        base = ((-2, -1), (-1, -1), (-2, 0))
        disjoint = tuple(tuple(shift + scale * value for value in row) for row in base)
        second = classify(features, disjoint)
        attacks += int(second[1] and not second[2])
        transcript.extend((("unequal", case, first), ("disjoint", case, second)))
    result = {
        "schema": "theorica.decision-identifiable-list-decoding-audit/1",
        "production_imports": 0,
        "positive_cases": positive,
        "positive_total": 60,
        "attacks_rejected": attacks,
        "attack_total": 40,
        "digest": hashlib.sha256(json.dumps(transcript, default=str).encode()).hexdigest(),
        "passed": positive == 60 and attacks == 40,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
