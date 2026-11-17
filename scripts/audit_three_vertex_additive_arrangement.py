#!/usr/bin/env python3
"""Independent Fraction-only audit; intentionally imports no THEORICA code."""
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "results" / "three_vertex_additive_arrangement" / "primary.json"
OUT = ROOT / "results" / "three_vertex_additive_arrangement" / "independent_audit.json"


def intersection(left, right):
    determinant = left[0] * right[1] - left[1] * right[0]
    if determinant == 0:
        return None
    return ((left[2] * right[1] - left[1] * right[2]) / determinant,
            (left[0] * right[2] - left[2] * right[0]) / determinant)


def envelope_value(actions, local_groups=None):
    actions = tuple(tuple(Fraction(x) for x in row) for row in actions)
    groups = (actions,) if local_groups is None else tuple(
        tuple(tuple(Fraction(x) for x in row) for row in group)
        for group in local_groups
    )
    ties = set()
    for group in groups:
        for p, q in combinations(group, 2):
            line = ((p[0]-p[2])-(q[0]-q[2]),
                    (p[1]-p[2])-(q[1]-q[2]), q[2]-p[2])
            if line[0] or line[1]:
                ties.add(line)
    points = {(Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)),
              (Fraction(0), Fraction(1))}
    def keep(point):
        if point is not None and point[0] >= 0 and point[1] >= 0 \
                and point[0] + point[1] <= 1:
            points.add(point)
    for a, b, c in ties:
        keep((Fraction(0), c/b) if b else None)
        keep((c/a, Fraction(0)) if a else None)
        keep(((c-b)/(a-b), 1-(c-b)/(a-b)) if a != b else None)
    for left, right in combinations(ties, 2):
        keep(intersection(left, right))
    def score(point):
        x, y = point
        return sum(max(x*p[0] + y*p[1] + (1-x-y)*p[2] for p in group)
                   for group in groups)
    return min(score(point) for point in points)


def expanded(components):
    return tuple(tuple(sum(components[t][choice[t]][s]
                           for t in range(len(components))) for s in range(3))
                 for choice in product(*(range(len(c)) for c in components)))


def main():
    primary = json.loads(PRIMARY.read_text())
    triples = tuple(product(range(3), repeat=3))
    cases = mismatches = strict = 0
    for four in product(triples, repeat=4):
        components = ((four[0], four[1]), (four[2], four[3]))
        joint = expanded(components)
        local = envelope_value(joint, components)
        global_value = envelope_value(joint)
        best_pure = max(min(row) for row in joint)
        cases += 1
        mismatches += int(local != global_value)
        strict += int(best_pure < global_value)

    holdout_checks = []
    for item in primary["holdouts"]:
        components = tuple(tuple(tuple(action) for action in component)
                           for component in item["components"])
        value = envelope_value(expanded(components))
        holdout_checks.append(str(value) == item["value"])
    checks = {
        "opened_case_count": cases == 531441 == primary["opened"]["cases"],
        "opened_local_global_agreement": mismatches == 0,
        "strict_count": strict == primary["opened"]["strict_randomization_cases"],
        "pure_count": cases-strict == primary["opened"]["pure_optimal_cases"],
        "holdout_values": all(holdout_checks) and len(holdout_checks) == 36,
        "primary_zero_mismatches": primary["opened"]["mismatches"] == 0
            and primary["holdout_summary"]["mismatches"] == 0,
        "support_bound": primary["opened"]["max_support"] <= 3
            and primary["holdout_summary"]["max_support"] <= 3,
        "scaling_certificate": primary["scaling_witness"]["valid"]
            and primary["scaling_witness"]["expanded_actions"] == 4**18,
    }
    result = {"schema": "three-vertex-additive-arrangement-audit-v1",
              "checks": checks, "passed": all(checks.values())}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
