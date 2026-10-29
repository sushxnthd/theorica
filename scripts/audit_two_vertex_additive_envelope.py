#!/usr/bin/env python3
"""Independent Fraction-only audit of the two-vertex additive envelope law."""
from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
from pathlib import Path


def expanded_value_and_strict(components):
    rows = tuple(
        tuple(sum((Fraction(components[t][action[t]][scenario])
                   for t in range(len(components))), Fraction(0))
              for scenario in range(2))
        for action in product(*(range(len(component)) for component in components))
    )
    pure = max(min(row) for row in rows)
    crossing = pure
    for left, right in combinations(rows, 2):
        left_delta = left[0] - left[1]
        right_delta = right[0] - right[1]
        if left_delta * right_delta >= 0:
            continue
        mass = right_delta / (right_delta - left_delta)
        value = mass * left[0] + (1 - mass) * right[0]
        crossing = max(crossing, value)
    return crossing, crossing > pure


def independent_envelope(components):
    components = tuple(tuple(tuple(Fraction(x) for x in action)
                             for action in component) for component in components)
    candidates = {Fraction(0), Fraction(1)}
    for component in components:
        for left, right in combinations(component, 2):
            denominator = (left[0] - left[1]) - (right[0] - right[1])
            if denominator:
                point = (right[1] - left[1]) / denominator
                if 0 <= point <= 1:
                    candidates.add(point)
    line = lambda action, p: p * action[0] + (1 - p) * action[1]
    dual = lambda p: sum(max(line(action, p) for action in component)
                         for component in components)
    probability = min(candidates, key=lambda p: (dual(p), p))
    value = dual(probability)
    tied = tuple(tuple(action for action in component
                       if line(action, probability)
                       == max(line(other, probability) for other in component))
                 for component in components)
    reachable = {Fraction(0)}
    for component in tied:
        reachable = {old + action[0] - action[1]
                     for old in reachable for action in component}
    strict = 0 < probability < 1 and Fraction(0) not in reachable
    return value, probability, strict, len(candidates)


def component_family():
    return tuple(
        tuple(tuple(entries[2 * action + scenario] for scenario in range(2))
              for action in range(2))
        for entries in product(range(3), repeat=4)
    )


def main():
    path = Path("results/two_vertex_additive_envelope/primary.json")
    data = json.loads(path.read_text())
    checks = {}

    without_digest = dict(data)
    reported = without_digest.pop("pre_digest_sha256")
    canonical = json.dumps(without_digest, indent=2, sort_keys=True) + "\n"
    checks["primary_digest_recomputed"] = (
        hashlib.sha256(canonical.encode()).hexdigest() == reported
    )

    cases = strict = pure = mismatches = 0
    family = component_family()
    for left in family:
        for right in family:
            components = (left, right)
            expanded_value, expanded_strict = expanded_value_and_strict(components)
            value, _, is_strict, _ = independent_envelope(components)
            mismatches += int(value != expanded_value or is_strict != expanded_strict)
            strict += int(is_strict)
            pure += int(not is_strict)
            cases += 1
    checks["exhaustive_digest_reproduced"] = (
        cases == data["exhaustive_cases"] == 6561
        and strict == data["exhaustive_strict_cases"]
        and pure == data["exhaustive_pure_cases"]
        and mismatches == 0
    )

    holdout_mismatches = policy_failures = 0
    for row in data["holdout_cases"]:
        components = row["components"]
        expanded_value, expanded_strict = expanded_value_and_strict(components)
        value, probability, is_strict, breakpoints = independent_envelope(components)
        holdout_mismatches += int(
            value != Fraction(row["value"])
            or probability != Fraction(row["nature_probability"])
            or is_strict != row["strict_randomization_necessary"]
            or breakpoints != row["breakpoints"]
            or expanded_value != value
            or expanded_strict != is_strict
        )
        realized = []
        for scenario in range(2):
            realized.append(sum(
                Fraction(mass) * sum(Fraction(components[t][actions[t]][scenario])
                                     for t in range(len(components)))
                for actions, mass in row["policy"]
            ))
        policy_failures += int(min(realized) != value or len(row["policy"]) > 2)
    checks["prospective_holdouts_exact"] = (
        len(data["holdout_cases"]) == 32
        and holdout_mismatches == policy_failures == 0
    )

    scaling = data["scaling_witness"]
    checks["exponential_scaling_witness"] = (
        scaling["expanded_actions"] == 5**20
        and scaling["candidate_upper_bound"] == 202
        and scaling["breakpoints"] <= 202
        and scaling["policy_support"] == 2
        and scaling["strict_randomization_necessary"]
    )
    checks["fail_closed_gates_recorded"] = all(data["negative_gates"].values())
    checks["reported_status_consistent"] = (
        data["status"] == "pass"
        and data["exhaustive_value_mismatches"] == 0
        and data["exhaustive_strictness_mismatches"] == 0
        and data["holdout_value_mismatches"] == 0
        and data["holdout_strictness_mismatches"] == 0
    )
    assert all(checks.values()), checks
    result = {
        "protocol": "theorica.two-vertex-additive-envelope.audit.v1",
        "checks": checks,
        "exhaustive_cases": cases,
        "exhaustive_strict_cases": strict,
        "holdout_cases": len(data["holdout_cases"]),
        "status": "pass",
    }
    target = Path("results/two_vertex_additive_envelope/independent_audit.json")
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
