#!/usr/bin/env python3
"""Frozen exact experiment for affine-scenario query complexity."""
from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from pathlib import Path

from theorica.agents.robust_provenance import (
    reconstruct_affine_scenario_payoffs,
    synthesize_rank_one_scenario_quotient_plan,
    synthesize_rank_three_scenario_polytope_plan,
    synthesize_rank_two_scenario_hull_plan,
)

SEED = 202610241711
HOLDOUT_SEEDS = tuple(910_003 + 7_919 * i for i in range(30))
HOLDOUT_COUNTS = (41, 64, 97, 127, 193)
OUT = Path("results/affine_scenario_query_complexity/primary.json")


def descriptors(dimension: int, count: int):
    if dimension == 1:
        return ((Fraction(0),), (Fraction(1),)) + tuple(
            (Fraction(index, count + 1),) for index in range(2, count)
        )
    basis = [(Fraction(0),) * dimension]
    basis.extend(tuple(Fraction(i == j) for i in range(dimension))
                 for j in range(dimension))
    points = list(basis)
    denominator = 4
    while len(points) < count:
        if dimension == 2:
            candidates = ((Fraction(a, denominator), Fraction(b, denominator))
                          for a in range(1, denominator)
                          for b in range(1, denominator - a))
        else:
            candidates = ((Fraction(a, denominator), Fraction(b, denominator),
                           Fraction(c, denominator))
                          for a in range(1, denominator)
                          for b in range(1, denominator)
                          for c in range(1, denominator - a - b))
        for point in candidates:
            if point not in points:
                points.append(point)
                if len(points) == count:
                    break
        denominator += 1
    return tuple(points)


def make_game(dimension: int, count: int, seed: int):
    rng = random.Random(seed)
    points = descriptors(dimension, count)
    component_count = 2 + seed % 4
    coefficients = []
    for component in range(component_count):
        action_count = 2 + (component + seed) % 2
        actions = []
        for action in range(action_count):
            values = [rng.randint(-5, 5) for _ in range(dimension + 1)]
            if component == 0 and action < dimension:
                values = [0] + [int(index == action) for index in range(dimension)]
            actions.append(tuple(Fraction(value) for value in values))
        coefficients.append(tuple(actions))
    table = tuple(tuple(tuple(
        action[0] + sum((action[index + 1] * point[index]
                         for index in range(dimension)), Fraction(0))
        for point in points
    ) for action in component) for component in coefficients)
    return points, table


def route(dimension, table):
    if dimension == 1:
        return synthesize_rank_one_scenario_quotient_plan(
            table, payoff_additive_certified=True)
    if dimension == 2:
        return synthesize_rank_two_scenario_hull_plan(
            table, payoff_additive_certified=True)
    return synthesize_rank_three_scenario_polytope_plan(
        table, payoff_additive_certified=True)


def evaluate_family(dimension: int, count: int, seed: int):
    points, table = make_game(dimension, count, seed)
    calls = []

    def oracle(index):
        calls.append(index)
        return tuple(tuple(action[index] for action in component)
                     for component in table)

    reconstruction = reconstruct_affine_scenario_payoffs(
        points, oracle, payoff_affine_certified=True)
    expected = route(dimension, table)
    observed = route(dimension, reconstruction.component_payoff_vectors)
    passed = (
        reconstruction.certificate_valid
        and reconstruction.component_payoff_vectors == table
        and reconstruction.query_count == dimension + 1
        and calls == list(reconstruction.query_indices)
        and len(set(calls)) == len(calls)
        and expected.certificate_valid
        and observed.certificate_valid
        and expected.minimax_value == observed.minimax_value
        and expected.strict_randomization_necessary
        == observed.strict_randomization_necessary
        and expected.joint_actions == observed.joint_actions
    )
    return {
        "dimension": dimension,
        "scenario_count": count,
        "seed": seed,
        "query_indices": list(reconstruction.query_indices),
        "query_count": reconstruction.query_count,
        "unqueried_count": count - reconstruction.query_count,
        "minimax_value": str(observed.minimax_value),
        "strict_randomization": observed.strict_randomization_necessary,
        "passed": passed,
    }


def lower_bound_witness(dimension: int, offset: int):
    translation = tuple(Fraction(offset + index, 7) for index in range(dimension))
    queried = []
    for index in range(dimension):
        point = list(translation)
        if index < dimension - 1:
            point[index] += 1
        queried.append(tuple(point))
    hidden = list(translation)
    hidden[-1] += 1
    points = tuple(queried) + (tuple(hidden),)
    zero_transcript = tuple(Fraction(0) for _ in queried)
    alternative_transcript = tuple(
        -(point[-1] - translation[-1]) for point in queried
    )
    alternative_values = tuple(
        -(point[-1] - translation[-1]) for point in points
    )
    return {
        "dimension": dimension,
        "queried": dimension,
        "transcripts_equal": zero_transcript == alternative_transcript,
        "zero_value": "0",
        "alternative_value": str(min(alternative_values)),
        "values_differ": min(alternative_values) != 0,
        "passed": (zero_transcript == alternative_transcript
                   and min(alternative_values) < 0),
    }


def main():
    opened = []
    for dimension in (1, 2, 3):
        for case in range(40):
            opened.append(evaluate_family(
                dimension, 9 + case % 32, SEED + dimension * 10_000 + case))
    holdouts = []
    for index, seed in enumerate(HOLDOUT_SEEDS):
        dimension = 1 + index % 3
        count = HOLDOUT_COUNTS[(index // 3) % len(HOLDOUT_COUNTS)]
        holdouts.append(evaluate_family(dimension, count, seed))
    lower_bounds = [
        lower_bound_witness(dimension, offset)
        for dimension in (1, 2, 3) for offset in range(20)
    ]
    payload = {
        "protocol_seed": SEED,
        "holdout_seeds": list(HOLDOUT_SEEDS),
        "opened": opened,
        "holdouts": holdouts,
        "lower_bound_witnesses": lower_bounds,
        "summary": {
            "opened_passed": sum(item["passed"] for item in opened),
            "opened_total": len(opened),
            "holdouts_passed": sum(item["passed"] for item in holdouts),
            "holdouts_total": len(holdouts),
            "lower_bounds_passed": sum(item["passed"] for item in lower_bounds),
            "lower_bounds_total": len(lower_bounds),
            "max_scenario_count": max(item["scenario_count"] for item in holdouts),
            "max_query_count": max(item["query_count"] for item in opened + holdouts),
            "strict_randomization_cases": sum(
                item["strict_randomization"] for item in opened + holdouts),
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(canonical.encode()).hexdigest()
    payload["passed"] = (
        payload["summary"]["opened_passed"] == len(opened)
        and payload["summary"]["holdouts_passed"] == len(holdouts)
        and payload["summary"]["lower_bounds_passed"] == len(lower_bounds)
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"digest": payload["digest"], "passed": payload["passed"],
                      **payload["summary"]}, indent=2, sort_keys=True))
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
