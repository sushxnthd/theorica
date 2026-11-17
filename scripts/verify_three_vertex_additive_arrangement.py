#!/usr/bin/env python3
"""Frozen exact evaluation for the three-vertex additive arrangement law."""
from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import random

from theorica.agents.robust_provenance import synthesize_three_vertex_additive_plan


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "three_vertex_additive_arrangement" / "primary.json"


def solve2(rows, rhs):
    determinant = rows[0][0] * rows[1][1] - rows[0][1] * rows[1][0]
    if determinant == 0:
        return None
    return (
        (rhs[0] * rows[1][1] - rows[0][1] * rhs[1]) / determinant,
        (rows[0][0] * rhs[1] - rhs[0] * rows[1][0]) / determinant,
    )


def expanded_value(actions):
    """Independent expanded-game dual enumeration."""
    actions = tuple(tuple(Fraction(value) for value in action) for action in actions)
    lines = set()
    for p, q in combinations(actions, 2):
        a = (p[0] - p[2]) - (q[0] - q[2])
        b = (p[1] - p[2]) - (q[1] - q[2])
        c = q[2] - p[2]
        if a or b:
            lines.add((a, b, c))
    points = {(Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)),
              (Fraction(0), Fraction(1))}
    inside = lambda p: p[0] >= 0 and p[1] >= 0 and p[0] + p[1] <= 1
    for a, b, c in lines:
        options = []
        if b:
            options.append((Fraction(0), c / b))
        if a:
            options.append((c / a, Fraction(0)))
        if a != b:
            x = (c - b) / (a - b)
            options.append((x, 1 - x))
        points.update(p for p in options if inside(p))
    for left, right in combinations(lines, 2):
        point = solve2(((left[0], left[1]), (right[0], right[1])),
                       (left[2], right[2]))
        if point is not None and inside(point):
            points.add(point)
    def objective(point):
        x, y = point
        return max(x*p[0] + y*p[1] + (1-x-y)*p[2] for p in actions)
    point = min(points, key=lambda p: (objective(p), p))
    value = objective(point)
    pure_value = max(min(action) for action in actions)
    return value, pure_value < value


def expanded_actions(components):
    return tuple(tuple(sum(components[t][choice[t]][s]
                           for t in range(len(components)))
                       for s in range(3))
                 for choice in product(*(range(len(c)) for c in components)))


def record(components):
    exact, strict = expanded_value(expanded_actions(components))
    plan = synthesize_three_vertex_additive_plan(
        components, payoff_additive_certified=True,
    )
    return {
        "value": str(exact),
        "strict": strict,
        "production_value": str(plan.minimax_value),
        "production_strict": plan.strict_randomization_necessary,
        "support": len(plan.joint_actions),
        "valid": plan.certificate_valid,
        "candidates": plan.arrangement_candidate_count,
        "expanded_actions": plan.expanded_action_count,
    }


def main():
    triples = tuple(product(range(3), repeat=3))
    total = mismatches = strict_cases = max_support = 0
    digest = hashlib.sha256()
    for four in product(triples, repeat=4):
        components = ((four[0], four[1]), (four[2], four[3]))
        item = record(components)
        total += 1
        strict_cases += int(item["strict"])
        max_support = max(max_support, item["support"])
        mismatch = not (
            item["value"] == item["production_value"]
            and item["strict"] == item["production_strict"]
            and item["valid"]
        )
        mismatches += int(mismatch)
        digest.update(json.dumps([components, item], sort_keys=True).encode())

    rng = random.Random(20261028)
    holdouts = []
    targets = {False: 18, True: 18}
    seen = set()
    while any(targets.values()):
        shape = rng.choice(((3, 3), (2, 4, 3), (4, 2, 2, 3)))
        components = tuple(tuple(tuple(rng.randrange(-3, 8) for _ in range(3))
                                 for _ in range(actions)) for actions in shape)
        key = repr(components)
        if key in seen:
            continue
        seen.add(key)
        item = record(components)
        strict = item["strict"]
        if not targets[strict]:
            continue
        targets[strict] -= 1
        item["components"] = components
        holdouts.append(item)

    scaling = tuple(
        tuple((t + a, (2*t + a) % 9, (t + 3*a) % 11) for a in range(4))
        for t in range(18)
    )
    scaling_plan = synthesize_three_vertex_additive_plan(
        scaling, payoff_additive_certified=True,
    )
    result = {
        "schema": "three-vertex-additive-arrangement-v1",
        "seed": 20261028,
        "opened": {
            "cases": total,
            "mismatches": mismatches,
            "strict_randomization_cases": strict_cases,
            "pure_optimal_cases": total - strict_cases,
            "max_support": max_support,
            "digest": digest.hexdigest(),
        },
        "holdouts": holdouts,
        "holdout_summary": {
            "cases": len(holdouts),
            "mismatches": sum(not (x["value"] == x["production_value"]
                                    and x["strict"] == x["production_strict"]
                                    and x["valid"]) for x in holdouts),
            "strict_randomization_cases": sum(x["strict"] for x in holdouts),
            "pure_optimal_cases": sum(not x["strict"] for x in holdouts),
            "max_support": max(x["support"] for x in holdouts),
        },
        "scaling_witness": {
            "components": 18,
            "actions_per_component": 4,
            "expanded_actions": scaling_plan.expanded_action_count,
            "tie_lines": scaling_plan.tie_line_count,
            "arrangement_candidates": scaling_plan.arrangement_candidate_count,
            "support": len(scaling_plan.joint_actions),
            "value": str(scaling_plan.minimax_value),
            "valid": scaling_plan.certificate_valid,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"opened": result["opened"],
                      "holdout_summary": result["holdout_summary"],
                      "scaling_witness": result["scaling_witness"]},
                     indent=2, sort_keys=True))
    if mismatches or result["holdout_summary"]["mismatches"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
