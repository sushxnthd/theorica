"""Independent Fraction-only audit; intentionally imports no THEORICA code."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "results" / "four_vertex_additive_arrangement" / "primary.json"
OUT = ROOT / "results" / "four_vertex_additive_arrangement" / "independent_audit.json"
PERMUTATIONS = tuple(permutations(range(4)))


def solve3(rows, rhs):
    determinant = (
        rows[0][0] * (rows[1][1] * rows[2][2] - rows[1][2] * rows[2][1])
        - rows[0][1] * (rows[1][0] * rows[2][2] - rows[1][2] * rows[2][0])
        + rows[0][2] * (rows[1][0] * rows[2][1] - rows[1][1] * rows[2][0])
    )
    if determinant == 0:
        return None
    answers = []
    for column in range(3):
        replaced = [list(row) for row in rows]
        for row in range(3):
            replaced[row][column] = rhs[row]
        numerator = (
            replaced[0][0] * (replaced[1][1] * replaced[2][2]
                               - replaced[1][2] * replaced[2][1])
            - replaced[0][1] * (replaced[1][0] * replaced[2][2]
                                - replaced[1][2] * replaced[2][0])
            + replaced[0][2] * (replaced[1][0] * replaced[2][1]
                                - replaced[1][1] * replaced[2][0])
        )
        answers.append(numerator / determinant)
    return tuple(answers)


def envelope_value(groups):
    groups = tuple(tuple(tuple(Fraction(x) for x in row) for row in group)
                   for group in groups)
    ties = set()
    for group in groups:
        for left, right in combinations(group, 2):
            row = tuple((left[i] - left[3]) - (right[i] - right[3])
                        for i in range(3))
            if any(row):
                ties.add((row, right[3] - left[3]))
    facets = (
        ((Fraction(1), 0, 0), Fraction(0)),
        ((0, Fraction(1), 0), Fraction(0)),
        ((0, 0, Fraction(1)), Fraction(0)),
        ((Fraction(1), Fraction(1), Fraction(1)), Fraction(1)),
    )
    points = set()
    for selected in combinations(tuple(ties) + facets, 3):
        point = solve3(tuple(item[0] for item in selected),
                       tuple(item[1] for item in selected))
        if point is not None and all(x >= 0 for x in point) and sum(point) <= 1:
            points.add(point)

    def score(point):
        last = 1 - sum(point)
        return sum(max(sum((point[i] * row[i] for i in range(3)), Fraction(0))
                           + last * row[3] for row in group) for group in groups)

    return min(score(point) for point in points)


def expanded(components):
    return tuple(
        tuple(sum(components[t][choice[t]][scenario]
                  for t in range(len(components))) for scenario in range(4))
        for choice in product(*(range(len(component)) for component in components))
    )


def canonical(four):
    representatives = []
    for permutation in PERMUTATIONS:
        transformed = tuple(tuple(vector[i] for i in permutation) for vector in four)
        representatives.append(tuple(sorted((
            tuple(sorted((transformed[0], transformed[1]))),
            tuple(sorted((transformed[2], transformed[3]))),
        ))))
    return min(representatives)


def main():
    primary = json.loads(PRIMARY.read_text())
    vectors = tuple(product(range(2), repeat=4))
    ordered = tuple(product(vectors, repeat=4))
    keys = {canonical(case) for case in ordered}
    cache = {}
    local_global_mismatches = 0
    for components in keys:
        joint = expanded(components)
        local = envelope_value(components)
        global_value = envelope_value((joint,))
        local_global_mismatches += int(local != global_value)
        cache[components] = (global_value, max(min(row) for row in joint) < global_value)

    strict = 0
    digest = hashlib.sha256()
    for case in ordered:
        value, randomized = cache[canonical(case)]
        strict += int(randomized)
        digest.update(f"{value}|{int(randomized)}\n".encode())

    holdout_checks = []
    for item in primary["holdouts"]:
        components = tuple(tuple(tuple(action) for action in component)
                           for component in item["components"])
        value = envelope_value((expanded(components),))
        holdout_checks.append(str(value) == item["value"])

    checks = {
        "opened_case_count": len(ordered) == 65536 == primary["opened"]["cases"],
        "symmetry_class_count": len(keys) == 652
            == primary["opened"]["symmetry_reduced_solver_calls"],
        "component_global_agreement": local_global_mismatches == 0,
        "strict_count": strict == primary["opened"]["strict_randomization_cases"],
        "pure_count": len(ordered) - strict == primary["opened"]["pure_optimal_cases"],
        "holdout_values": len(holdout_checks) == 40 and all(holdout_checks),
        "primary_certificates": primary["opened"]["mismatches"] == 0
            and primary["holdout_summary"]["mismatches"] == 0
            and primary["opened"]["max_support"] <= 4
            and primary["holdout_summary"]["max_support"] <= 4,
        "scaling_certificate": primary["scaling_witness"]["valid"]
            and primary["scaling_witness"]["expanded_actions"] == 4**18
            and primary["scaling_witness"]["arrangement_candidates"]
            <= primary["scaling_witness"]["candidate_upper_bound"],
    }
    result = {
        "schema": "four-vertex-additive-arrangement-audit-v1",
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
