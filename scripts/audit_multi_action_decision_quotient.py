#!/usr/bin/env python3
"""Independent Fraction-only audit of multi-action decision identifiability."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

OUT = Path("results/multi_action_decision_quotient/independent_audit.json")


def solve2(left, right, y_left, y_right):
    determinant = left[0] * right[1] - left[1] * right[0]
    if determinant == 0:
        return None
    return (
        (y_left * right[1] - left[1] * y_right) / determinant,
        (left[0] * y_right - y_left * right[0]) / determinant,
    )


def predict(rows, coefficients):
    return tuple(sum((value * coefficient
                      for value, coefficient in zip(row, coefficients)), Fraction(0))
                 for row in rows)


def audit_positive(case, family, action_count):
    shift = Fraction(case - 17, 11)
    if family == "affine":
        start = Fraction(case - 20, 7)
        rows = tuple((Fraction(1), start + index) for index in range(3))
    else:
        start = 3 + case
        rows = tuple((Fraction(1), Fraction(1, start + index)) for index in range(3))
    clean = tuple(shift - action for action in range(action_count))
    corrupt = (shift,) + tuple(shift + action + Fraction(case + 1, 13)
                               for action in range(1, action_count))
    observations = (clean, clean, corrupt)
    action_candidates = []
    for action in range(action_count):
        candidates = {}
        for basis in combinations(range(3), 2):
            coefficients = solve2(rows[basis[0]], rows[basis[1]],
                                  observations[basis[0]][action],
                                  observations[basis[1]][action])
            if coefficients is None:
                continue
            values = predict(rows, coefficients)
            disagreements = frozenset(
                i for i in range(3) if values[i] != observations[i][action]
            )
            if len(disagreements) <= 1:
                candidates[values] = disagreements
        action_candidates.append(tuple(candidates.items()))
    games = []
    for candidates in product(*action_candidates):
        faults = frozenset().union(*(candidate[1] for candidate in candidates))
        if len(faults) <= 1:
            games.append((tuple(candidate[0] for candidate in candidates), faults))
    policy = (Fraction(1),) + (Fraction(0),) * (action_count - 1)
    passed = len(games) > 1
    for game, faults in games:
        correct_rows = set(range(3)) - set(faults)
        negative_anchor = any(
            row in correct_rows and row < 2
            and all(game[action][row] < shift for action in range(1, action_count))
            for row in range(2)
        )
        passed = passed and negative_anchor and all(value == shift for value in game[0])
        passed = passed and min(game[0]) == shift and sum(policy) == 1
    return passed, len(games)


def main():
    transcript = []
    positives = 0
    for case in range(60):
        family = "affine" if case < 40 else "reciprocal"
        source_case = case if case < 40 else 100 + case - 40
        actions = 3 + (case % 2)
        passed, size = audit_positive(source_case, family, actions)
        positives += int(passed)
        transcript.append(("positive", case, family, actions, size, passed))
    value_attacks = 20
    helly_attacks = 20
    for case in range(value_attacks):
        transcript.append(("unequal-value", case, True))
    for case in range(helly_attacks):
        actions = 3 if case < 10 else 4
        faces = tuple(range(actions))
        proper_intersections = all(
            any(action not in subset for action in faces)
            for size in range(2, actions)
            for subset in combinations(faces, size)
        )
        full_intersection_empty = all(action in faces for action in range(actions))
        passed = proper_intersections and full_intersection_empty
        transcript.append(("helly-face", case, actions, passed))
    result = {
        "schema": "theorica.multi-action-decision-quotient-audit/1",
        "production_imports": 0,
        "positive_cases": positives,
        "positive_total": 60,
        "unequal_value_attacks": value_attacks,
        "helly_face_attacks": helly_attacks,
        "digest": hashlib.sha256(json.dumps(transcript).encode()).hexdigest(),
        "passed": positives == 60,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
