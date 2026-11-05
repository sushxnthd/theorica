"""Frozen exact evaluation for the four-vertex additive arrangement law."""
from __future__ import annotations

import hashlib
import json
import os
import random
from fractions import Fraction
from itertools import combinations, permutations, product
from multiprocessing import Pool
from pathlib import Path

from theorica.agents.robust_provenance import synthesize_four_vertex_additive_plan

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "four_vertex_additive_arrangement" / "primary.json"
SCENARIO_PERMUTATIONS = tuple(permutations(range(4)))


def solve3(rows, rhs):
    a = [list(rows[i]) + [rhs[i]] for i in range(3)]
    for column in range(3):
        pivot = next((i for i in range(column, 3) if a[i][column]), None)
        if pivot is None:
            return None
        a[column], a[pivot] = a[pivot], a[column]
        scale = a[column][column]
        a[column] = [value / scale for value in a[column]]
        for row in range(3):
            if row == column:
                continue
            scale = a[row][column]
            a[row] = [a[row][i] - scale * a[column][i] for i in range(4)]
    return tuple(row[-1] for row in a)


def expanded_value(actions):
    actions = tuple(tuple(Fraction(value) for value in action) for action in actions)
    ties = set()
    for left, right in combinations(actions, 2):
        row = tuple((left[i] - left[3]) - (right[i] - right[3]) for i in range(3))
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
        if point is not None and all(value >= 0 for value in point) \
                and sum(point) <= 1:
            points.add(point)

    def score(point):
        last = 1 - sum(point)
        return max(sum((point[i] * action[i] for i in range(3)), Fraction(0))
                   + last * action[3] for action in actions)

    point = min(points, key=lambda q: (score(q), q))
    value = score(point)
    return value, max(min(action) for action in actions) < value


def expanded_actions(components):
    return tuple(
        tuple(sum((components[t][choice[t]][s] for t in range(len(components))),
                  Fraction(0)) for s in range(4))
        for choice in product(*(range(len(component)) for component in components))
    )


def record(components):
    joint = expanded_actions(components)
    exact, strict = expanded_value(joint)
    plan = synthesize_four_vertex_additive_plan(
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
        "candidate_bound": plan.candidate_upper_bound,
        "expanded_actions": plan.expanded_action_count,
    }


def canonical_components(four):
    representatives = []
    for permutation in SCENARIO_PERMUTATIONS:
        transformed = tuple(
            tuple(vector[i] for i in permutation) for vector in four
        )
        representatives.append(tuple(sorted((
            tuple(sorted((transformed[0], transformed[1]))),
            tuple(sorted((transformed[2], transformed[3]))),
        ))))
    return min(representatives)


def opened_record(components):
    return components, record(components)


def main():
    vectors = tuple(product(range(2), repeat=4))
    total = mismatches = strict_cases = max_support = 0
    digest = hashlib.sha256()
    ordered_cases = tuple(product(vectors, repeat=4))
    canonical_cases = sorted({canonical_components(case) for case in ordered_cases})
    workers = min(8, os.cpu_count() or 1)
    with Pool(workers) as pool:
        cache = dict(pool.imap(opened_record, canonical_cases, chunksize=32))
    for case in ordered_cases:
        components = ((case[0], case[1]), (case[2], case[3]))
        item = cache[canonical_components(case)]
        total += 1
        strict_cases += int(item["strict"])
        max_support = max(max_support, item["support"])
        mismatch = not (
            item["value"] == item["production_value"]
            and item["strict"] == item["production_strict"]
            and item["valid"]
            and item["candidates"] <= item["candidate_bound"]
        )
        mismatches += int(mismatch)
        digest.update(json.dumps([components, item], sort_keys=True).encode())

    rng = random.Random(20261023)
    targets = {False: 20, True: 20}
    holdouts = []
    seen = set()
    while any(targets.values()):
        shape = rng.choice(((3, 2), (2, 2, 2), (3, 2, 2)))
        components = tuple(
            tuple(tuple(rng.randrange(-4, 9) for _ in range(4))
                  for _ in range(actions))
            for actions in shape
        )
        key = repr(components)
        if key in seen:
            continue
        seen.add(key)
        item = record(components)
        if not targets[item["strict"]]:
            continue
        targets[item["strict"]] -= 1
        item["components"] = components
        holdouts.append(item)

    scaling = (
        tuple(tuple(4 if i == action else 0 for i in range(4))
              for action in range(4)),
    ) + tuple(
        tuple((level, level, level, level) for level in range(component + 4,
                                                               component, -1))
        for component in range(1, 18)
    )
    scaling_plan = synthesize_four_vertex_additive_plan(
        scaling, payoff_additive_certified=True,
    )
    result = {
        "schema": "four-vertex-additive-arrangement-v1",
        "seed": 20261023,
        "opened": {
            "cases": total,
            "symmetry_reduced_solver_calls": len(canonical_cases),
            "mismatches": mismatches,
            "strict_randomization_cases": strict_cases,
            "pure_optimal_cases": total - strict_cases,
            "max_support": max_support,
            "digest": digest.hexdigest(),
        },
        "holdouts": holdouts,
        "holdout_summary": {
            "cases": len(holdouts),
            "mismatches": sum(not (
                item["value"] == item["production_value"]
                and item["strict"] == item["production_strict"]
                and item["valid"]
            ) for item in holdouts),
            "strict_randomization_cases": sum(item["strict"] for item in holdouts),
            "pure_optimal_cases": sum(not item["strict"] for item in holdouts),
            "max_support": max(item["support"] for item in holdouts),
        },
        "scaling_witness": {
            "components": 18,
            "actions_per_component": 4,
            "expanded_actions": scaling_plan.expanded_action_count,
            "tie_hyperplanes": scaling_plan.tie_hyperplane_count,
            "arrangement_candidates": scaling_plan.arrangement_candidate_count,
            "candidate_upper_bound": scaling_plan.candidate_upper_bound,
            "support": len(scaling_plan.joint_actions),
            "value": str(scaling_plan.minimax_value),
            "valid": scaling_plan.certificate_valid,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "opened": result["opened"],
        "holdout_summary": result["holdout_summary"],
        "scaling_witness": result["scaling_witness"],
    }, indent=2, sort_keys=True))
    if mismatches or result["holdout_summary"]["mismatches"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
