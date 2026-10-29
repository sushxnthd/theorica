#!/usr/bin/env python3
"""Frozen exact experiment for the feature-rank query law."""
from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from pathlib import Path

from theorica.agents.robust_provenance import (
    reconstruct_feature_span_scenario_payoffs,
    synthesize_rank_one_scenario_quotient_plan,
    synthesize_rank_three_scenario_polytope_plan,
    synthesize_rank_two_scenario_hull_plan,
)

SEED = 202610242218
HOLDOUT_SEEDS = tuple(1_400_009 + 10_007 * index for index in range(40))
HOLDOUT_COUNTS = (53, 79, 113, 167, 257)
OUT = Path("results/feature_rank_query_complexity/primary.json")


def simplex_points(dimension, count):
    if dimension == 1:
        return ((Fraction(0),), (Fraction(1),)) + tuple(
            (Fraction(index, count + 1),) for index in range(2, count))
    points = [(Fraction(0),) * dimension]
    points.extend(tuple(Fraction(i == j) for i in range(dimension))
                  for j in range(dimension))
    denominator = 4
    while len(points) < count:
        candidates = (
            ((Fraction(a, denominator), Fraction(b, denominator))
             for a in range(1, denominator)
             for b in range(1, denominator - a))
            if dimension == 2 else
            ((Fraction(a, denominator), Fraction(b, denominator),
              Fraction(c, denominator))
             for a in range(1, denominator)
             for b in range(1, denominator)
             for c in range(1, denominator - a - b))
        )
        for point in candidates:
            if point not in points:
                points.append(point)
                if len(points) == count:
                    break
        denominator += 1
    return tuple(points)


def feature_rows(rank, count, redundant):
    base = tuple((Fraction(1),) + point
                 for point in simplex_points(rank - 1, count))
    if not redundant:
        return base
    return tuple(row + (
        sum(row, Fraction(0)),
        2 * row[0] - row[1],
        row[-1],
    ) for row in base)


def make_table(rank, rows, seed):
    rng = random.Random(seed)
    base_rows = tuple(row[:rank] for row in rows)
    components = []
    for component in range(2 + seed % 4):
        actions = []
        for action in range(2 + (component + seed) % 2):
            coefficients = [Fraction(rng.randint(-5, 5)) for _ in range(rank)]
            if component == 0 and action < rank - 1:
                coefficients = [Fraction(0)] + [
                    Fraction(index == action) for index in range(rank - 1)
                ]
            actions.append(tuple(
                sum((coefficient * value for coefficient, value
                     in zip(coefficients, row)), Fraction(0))
                for row in base_rows
            ))
        components.append(tuple(actions))
    return tuple(components)


def route(rank, table):
    if rank == 2:
        return synthesize_rank_one_scenario_quotient_plan(
            table, payoff_additive_certified=True)
    if rank == 3:
        return synthesize_rank_two_scenario_hull_plan(
            table, payoff_additive_certified=True)
    return synthesize_rank_three_scenario_polytope_plan(
        table, payoff_additive_certified=True)


def evaluate(rank, count, seed, redundant):
    rows = feature_rows(rank, count, redundant)
    table = make_table(rank, rows, seed)
    calls = []

    def oracle(index):
        calls.append(index)
        return tuple(tuple(action[index] for action in component)
                     for component in table)

    reconstruction = reconstruct_feature_span_scenario_payoffs(
        rows, oracle, payoff_in_feature_span_certified=True)
    expected = route(rank, table)
    observed = route(rank, reconstruction.component_payoff_vectors)
    passed = (
        reconstruction.certificate_valid
        and reconstruction.feature_rank == rank
        and reconstruction.query_count == rank
        and calls == list(reconstruction.query_indices)
        and len(set(calls)) == rank
        and reconstruction.component_payoff_vectors == table
        and expected.certificate_valid and observed.certificate_valid
        and expected.minimax_value == observed.minimax_value
        and expected.strict_randomization_necessary
        == observed.strict_randomization_necessary
        and expected.joint_actions == observed.joint_actions
    )
    return {
        "rank": rank,
        "feature_width": len(rows[0]),
        "redundant": redundant,
        "scenario_count": count,
        "seed": seed,
        "query_indices": list(reconstruction.query_indices),
        "pivot_columns": list(reconstruction.pivot_columns),
        "query_count": reconstruction.query_count,
        "unqueried_count": count - rank,
        "minimax_value": str(observed.minimax_value),
        "strict_randomization": observed.strict_randomization_necessary,
        "passed": passed,
    }


def polynomial_witness(degree, offset):
    count = 8
    xs = tuple(Fraction(index - 3 + offset, 5) for index in range(count))
    base = tuple(tuple(x ** power for power in range(degree + 1)) for x in xs)
    rows = tuple(row + (row[1] + 2 * row[-1], row[0]) for row in base)
    coefficients = tuple(Fraction((offset + 2) * (index + 1) - 5)
                         for index in range(degree + 1))
    values = tuple(sum((coefficient * value for coefficient, value
                        in zip(coefficients, row)), Fraction(0))
                   for row in base)
    calls = []
    reconstruction = reconstruct_feature_span_scenario_payoffs(
        rows,
        lambda index: calls.append(index) or ((values[index],),),
        payoff_in_feature_span_certified=True,
    )
    first_slope = (values[1] - values[0]) / (xs[1] - xs[0])
    affine_invalid = any(
        values[0] + first_slope * (x - xs[0]) != value
        for x, value in zip(xs[2:], values[2:])
    )
    return {
        "degree": degree,
        "feature_rank": reconstruction.feature_rank,
        "feature_width": reconstruction.feature_width,
        "query_count": reconstruction.query_count,
        "affine_certificate_invalid": affine_invalid,
        "passed": (
            reconstruction.component_payoff_vectors == ((values,),)
            and reconstruction.query_count == degree + 1
            and len(calls) == degree + 1
            and affine_invalid
        ),
    }


def lower_bound(rank, offset):
    rows = []
    for index in range(rank):
        row = [Fraction(0)] * rank
        row[index] = 1
        rows.append(tuple(row) + (Fraction(index + offset),))
    queried = tuple(range(rank - 1))
    zero = tuple(Fraction(0) for _ in queried)
    alternative = tuple(-rows[index][rank - 1] for index in queried)
    all_values = tuple(-row[rank - 1] for row in rows)
    return {
        "rank": rank,
        "queried": rank - 1,
        "feature_width": rank + 1,
        "transcripts_equal": zero == alternative,
        "zero_value": "0",
        "alternative_value": str(min(all_values)),
        "values_differ": min(all_values) < 0,
        "passed": zero == alternative and min(all_values) < 0,
    }


def main():
    opened = []
    for case in range(160):
        rank = 2 + case % 3
        opened.append(evaluate(
            rank,
            9 + case % 40,
            SEED + case * 97,
            redundant=case % 2 == 0,
        ))
    holdouts = []
    for index, seed in enumerate(HOLDOUT_SEEDS):
        holdouts.append(evaluate(
            2 + index % 3,
            HOLDOUT_COUNTS[(index // 3) % len(HOLDOUT_COUNTS)],
            seed,
            redundant=index % 2 == 1,
        ))
    polynomial = [polynomial_witness(degree, offset)
                  for degree in (2, 3) for offset in range(4)]
    lower_bounds = [lower_bound(rank, offset)
                    for rank in (2, 3, 4) for offset in range(30)]
    summary = {
        "opened_passed": sum(item["passed"] for item in opened),
        "opened_total": len(opened),
        "holdouts_passed": sum(item["passed"] for item in holdouts),
        "holdouts_total": len(holdouts),
        "polynomial_passed": sum(item["passed"] for item in polynomial),
        "polynomial_total": len(polynomial),
        "lower_bounds_passed": sum(item["passed"] for item in lower_bounds),
        "lower_bounds_total": len(lower_bounds),
        "strict_randomization_cases": sum(
            item["strict_randomization"] for item in opened + holdouts),
        "max_scenario_count": max(item["scenario_count"] for item in holdouts),
        "max_feature_width": max(item["feature_width"] for item in opened),
        "max_query_count": max(item["query_count"] for item in opened),
    }
    payload = {
        "protocol_seed": SEED,
        "holdout_seeds": list(HOLDOUT_SEEDS),
        "opened": opened,
        "holdouts": holdouts,
        "polynomial_witnesses": polynomial,
        "lower_bound_witnesses": lower_bounds,
        "summary": summary,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(canonical.encode()).hexdigest()
    payload["passed"] = all((
        summary["opened_passed"] == summary["opened_total"],
        summary["holdouts_passed"] == summary["holdouts_total"],
        summary["polynomial_passed"] == summary["polynomial_total"],
        summary["lower_bounds_passed"] == summary["lower_bounds_total"],
    ))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"digest": payload["digest"], "passed": payload["passed"],
                      **summary}, indent=2, sort_keys=True))
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
