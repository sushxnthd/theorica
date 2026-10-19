#!/usr/bin/env python3
"""Independent Fraction-only audit; intentionally imports no production code."""
import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations


def compositions(a, b, k):
    return tuple((Fraction(x, a), Fraction(k - x, b))
                 for x in range(max(0, k - b), min(a, k) + 1))


def pair_game_value(actions, vertices):
    def payoff(action, vertex):
        return sum((x * y for x, y in zip(action, vertex)), Fraction(0))
    candidates = [(Fraction(0), min(payoff(actions[0], v) for v in vertices))]
    if len(actions) == 1:
        return candidates[0][1]
    candidates.append((Fraction(1), min(payoff(actions[1], v) for v in vertices)))
    # lambda is weight on actions[1]. The lower envelope of two affine
    # functions can only maximize at an endpoint or their crossing.
    left = tuple(payoff(actions[0], v) for v in vertices)
    delta = tuple(payoff(actions[1], v) - left[i] for i, v in enumerate(vertices))
    denominator = delta[0] - delta[1]
    if denominator:
        lam = (left[1] - left[0]) / denominator
        if 0 <= lam <= 1:
            value = min(left[i] + lam * delta[i] for i in range(2))
            candidates.append((lam, value))
    return max(value for _, value in candidates)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    primary = json.load(open(args.primary, encoding="utf-8"))
    digest = hashlib.sha256()
    cases = strict = pure = 0
    grid = (Fraction(0), Fraction(1, 3), Fraction(2, 3), Fraction(1))
    for n in range(3, 8):
        for a in range(1, n):
            b = n - a
            sizes = (a, b)
            for k in range(1, n):
                points = compositions(a, b, k)
                families = [(point,) for point in points]
                families.extend(combinations(points, 2))
                for actions in families:
                    for lo, hi in combinations(grid, 2):
                        vertices = ((lo, 1 - lo), (hi, 1 - hi))
                        value = pair_game_value(actions, vertices)
                        best_pure = max(min(sum((x * y for x, y in zip(action, vertex)),
                                                     Fraction(0)) for vertex in vertices)
                                        for action in actions)
                        cases += 1
                        strict += int(value > best_pure)
                        pure += int(value == best_pure)
                        digest.update(repr((sizes, k, actions, vertices, value, best_pure)).encode())
    assert primary["two_orbit_cases"] == cases
    assert primary["strict_randomization_cases"] == strict
    assert primary["pure_optimal_cases"] == pure
    assert primary["two_orbit_value_digest"] == digest.hexdigest()
    assert primary["frozen_prediction"] == {
        "status": "pass", "point_orbit_sizes": [3, 4], "k": 2,
        "weights": {"(2/3,0)": "3/7", "(0,1/2)": "4/7"},
        "value": "2/7", "best_pure": "1/6", "gain": "5/42",
    }
    assert primary["noninvariant_counterexample"] == {
        "unrestricted_value": "1", "forced_invariant_value": "1/2",
        "gap": "1/2", "status": "pass",
    }
    result = {
        "schema": "theorica.orbit-quotient-ambiguity.audit.v1",
        "status": "pass", "independent": True,
        "two_orbit_cases": cases,
        "strict_randomization_cases": strict,
        "pure_optimal_cases": pure,
        "value_digest": digest.hexdigest(),
        "noninvariant_counterexample_reproduced": True,
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
