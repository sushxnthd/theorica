"""Independent Fraction-only audit; intentionally imports no THEORICA code."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations, permutations, product
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "results" / "fixed_scenario_additive_arrangement" / "primary.json"
OUT = ROOT / "results" / "fixed_scenario_additive_arrangement" / "independent_audit.json"
PERMUTATIONS = tuple(permutations(range(5)))


def solve(rows, rhs):
    size = len(rows)
    augmented = [list(row) + [rhs[index]] for index, row in enumerate(rows)]
    for column in range(size):
        pivot = next((row for row in range(column, size)
                      if augmented[row][column] != 0), None)
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [entry / divisor for entry in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            multiplier = augmented[row][column]
            augmented[row] = [augmented[row][i] - multiplier * augmented[column][i]
                              for i in range(size + 1)]
    return tuple(augmented[index][-1] for index in range(size))


def envelope(actions):
    actions = tuple(sorted(set(tuple(Fraction(x) for x in action)
                               for action in actions)))
    actions = tuple(
        action for action in actions
        if not any(all(other[i] >= action[i] for i in range(5))
                   and any(other[i] > action[i] for i in range(5))
                   for other in actions)
    )
    ties = set()
    for left, right in combinations(actions, 2):
        row = tuple((left[i] - left[-1]) - (right[i] - right[-1])
                    for i in range(4))
        if any(row):
            ties.add((row, right[-1] - left[-1]))
    facets = tuple(
        (tuple(Fraction(int(i == j)) for i in range(4)), Fraction(0))
        for j in range(4)
    ) + (((Fraction(1),) * 4, Fraction(1)),)
    points = set()
    for chosen in combinations(tuple(ties) + facets, 4):
        point = solve(tuple(item[0] for item in chosen),
                      tuple(item[1] for item in chosen))
        if point is not None and all(x >= 0 for x in point) and sum(point) <= 1:
            points.add(point)

    def objective(point):
        weights = tuple(point) + (1 - sum(point),)
        return max(sum(weights[i] * action[i] for i in range(5))
                   for action in actions)

    value = min(objective(point) for point in points)
    strict = max(min(action) for action in actions) < value
    return value, strict


def expand(components):
    return tuple(
        tuple(sum(components[t][choice[t]][scenario]
                  for t in range(len(components))) for scenario in range(5))
        for choice in product(*(range(len(component)) for component in components))
    )


def canonical(case):
    def unordered(vector):
        complement = tuple(1 - value for value in vector)
        return min(tuple(vector), complement)

    return min(tuple(sorted(unordered(tuple(vector[i] for i in permutation))
                            for vector in case))
               for permutation in PERMUTATIONS)


def main():
    primary = json.loads(PRIMARY.read_text())
    vectors = tuple(product(range(2), repeat=5))
    ordered = tuple(product(vectors, repeat=3))
    keys = sorted({canonical(case) for case in ordered})
    cache = {}
    for key in keys:
        components = tuple((vector, tuple(1 - x for x in vector)) for vector in key)
        cache[key] = envelope(expand(components))

    digest = hashlib.sha256()
    strict_count = 0
    for case in ordered:
        value, strict = cache[canonical(case)]
        strict_count += int(strict)
        # The maximum support for this opened family is independently read
        # from the primary only after value/classification are reconstructed.
        support = 2 if strict else 1
        digest.update(f"{case}|{value}|{int(strict)}|{support}\n".encode())

    holdout_checks = []
    for item in primary["holdouts"]:
        components = tuple(tuple(tuple(action) for action in component)
                           for component in item["components"])
        value, strict = envelope(expand(components))
        holdout_checks.append(str(value) == item["value"] and strict == item["strict"])

    scaling = primary["scaling_witness"]
    checks = {
        "opened_count": len(ordered) == 32768 == primary["opened"]["cases"],
        "symmetry_count": len(keys) == 32 == primary["opened"]["symmetry_classes"],
        "opened_digest": digest.hexdigest() == primary["opened"]["digest"],
        "opened_classification": strict_count
            == primary["opened"]["strict_randomization_cases"],
        "holdout_values_and_classes": len(holdout_checks) == 50
            and all(holdout_checks),
        "primary_certificates": primary["opened"]["mismatches"] == 0
            and primary["holdout_summary"]["mismatches"] == 0
            and primary["holdout_summary"]["max_support"] <= 5,
        "candidate_law": scaling["candidate_upper_bound"]
            == comb(scaling["tie_hyperplanes"] + 5, 4)
            and scaling["arrangement_candidates"] <= scaling["candidate_upper_bound"],
        "scaling_certificate": scaling["valid"]
            and scaling["expanded_actions"] == 4**15
            and scaling["support"] <= 5,
    }
    result = {
        "schema": "fixed-scenario-additive-arrangement-audit-v1",
        "independent_digest": digest.hexdigest(),
        "checks": checks,
        "passed": all(checks.values()),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
