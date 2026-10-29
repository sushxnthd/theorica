"""Frozen prospective evaluation of the tight rank-three nature-support law."""

from __future__ import annotations

import hashlib
import json
import random
from fractions import Fraction
from pathlib import Path

from verify_rank_three_scenario_polytope import (
    exact_game,
    expand,
    hull_indices,
    make_case,
    make_coordinates,
)

from theorica.agents.robust_provenance import (
    compress_rank_three_nature_certificate,
    synthesize_rank_three_scenario_polytope_plan,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "rank_three_nature_support"
PRIMARY_OUT = OUT_DIR / "primary.json"
CASES_OUT = OUT_DIR / "cases.json"
SEED = 20261027


def encode_fraction(value):
    return str(Fraction(value))


def encode_points(points):
    return [[encode_fraction(value) for value in point] for point in points]


def opened_cases():
    rng = random.Random(SEED - 1)
    return tuple(
        make_case(9 + (index * 3 + vertices) % 12, vertices, rng,
                  pure=index % 5 == 0)
        for vertices in range(4, 9)
        for index in range(16)
    )


def holdout_cases():
    rng = random.Random(SEED)
    ambient_sizes = (9, 12, 16, 20, 24)
    return tuple(
        make_case(ambient, vertices, rng, pure=index == 0)
        for ambient, vertices in zip(ambient_sizes, range(4, 9), strict=True)
        for index in range(6)
    )


def evaluate(case):
    coordinates, components = case
    extremes = hull_indices(coordinates)
    exact_value, strict = exact_game(expand(components, extremes))
    plan = synthesize_rank_three_scenario_polytope_plan(
        components,
        payoff_additive_certified=True,
    )
    dual_value = sum(
        max(
            sum((plan.nature_probabilities[scenario] * action[scenario]
                 for scenario in range(len(coordinates))), Fraction(0))
            for action in component
        )
        for component in components
    )
    support = sum(weight > 0 for weight in plan.nature_probabilities)
    passed = (
        plan.certificate_valid
        and plan.minimax_value == exact_value == dual_value
        and plan.strict_randomization_necessary == strict
        and plan.support_bound == 4
        and support <= 4
        and sum(plan.nature_probabilities, Fraction(0)) == 1
        and all(weight >= 0 for weight in plan.nature_probabilities)
    )
    record = {
        "ambient": len(coordinates),
        "vertices": len(extremes),
        "value": encode_fraction(exact_value),
        "strict": strict,
        "nature_support": support,
        "passed": passed,
    }
    serialized = {
        "coordinates": encode_points(coordinates),
        "components": [
            [[encode_fraction(value) for value in action] for action in component]
            for component in components
        ],
        "nature": [encode_fraction(value) for value in plan.nature_probabilities],
        "value": encode_fraction(exact_value),
        "passed": passed,
    }
    return record, serialized


def dense_interventions():
    rng = random.Random(SEED + 1)
    records = []
    serialized = []
    for vertices in range(5, 9):
        for case_index in range(10):
            points = make_coordinates(vertices, vertices, rng)
            numerators = tuple(rng.randrange(1, 20) for _ in points)
            total = sum(numerators)
            dense = tuple(Fraction(value, total) for value in numerators)
            compressed = compress_rank_three_nature_certificate(points, dense)
            before = tuple(
                sum((dense[index] * point[axis]
                     for index, point in enumerate(points)), Fraction(0))
                for axis in range(3)
            )
            after = tuple(
                sum((compressed[index] * point[axis]
                     for index, point in enumerate(points)), Fraction(0))
                for axis in range(3)
            )
            support = sum(weight > 0 for weight in compressed)
            passed = (
                before == after
                and sum(compressed, Fraction(0)) == 1
                and all(weight >= 0 for weight in compressed)
                and support <= 4
                and sum(weight > 0 for weight in dense) == vertices
            )
            records.append({
                "vertices": vertices,
                "case_index": case_index,
                "compressed_support": support,
                "passed": passed,
            })
            serialized.append({
                "points": encode_points(points),
                "dense": [encode_fraction(value) for value in dense],
                "compressed": [encode_fraction(value) for value in compressed],
                "passed": passed,
            })
    return records, serialized


def tightness_witness():
    actions = (
        (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(0), Fraction(1)),
    )
    plan = synthesize_rank_three_scenario_polytope_plan(
        (actions,),
        payoff_additive_certified=True,
    )
    support = sum(weight > 0 for weight in plan.nature_probabilities)
    return {
        "value": encode_fraction(plan.minimax_value),
        "support": support,
        "uniform": all(weight == Fraction(1, 4)
                       for weight in plan.nature_probabilities),
        "passed": plan.certificate_valid
            and plan.minimax_value == Fraction(1, 4)
            and support == 4,
    }


def rank_four_attacks():
    rejected = 0
    for index in range(40):
        scale = 1 + index % 11
        attack = (((0, scale, 0, 0, 0), (0, 0, scale, 0, 0),
                   (0, 0, 0, scale, 0), (0, 0, 0, 0, scale)),)
        try:
            synthesize_rank_three_scenario_polytope_plan(
                attack,
                payoff_additive_certified=True,
            )
        except ValueError as error:
            rejected += int("above three" in str(error))
    return rejected


def digest(payload):
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def main():
    opened = [evaluate(case) for case in opened_cases()]
    holdouts = [evaluate(case) for case in holdout_cases()]
    dense, dense_serialized = dense_interventions()
    tight = tightness_witness()
    rejected = rank_four_attacks()
    opened_records = [record for record, _ in opened]
    holdout_records = [record for record, _ in holdouts]
    checks = {
        "opened_exact": len(opened) == 80
            and all(record["passed"] for record in opened_records),
        "holdouts_exact": len(holdouts) == 30
            and all(record["passed"] for record in holdout_records),
        "dense_interventions": len(dense) == 40
            and all(record["passed"] for record in dense),
        "tight_bound": tight["passed"],
        "rank_four_rejected": rejected == 40,
    }
    cases = {
        "schema": "rank-three-nature-support-cases-v1",
        "seed": SEED,
        "holdouts": [serialized for _, serialized in holdouts],
        "dense_interventions": dense_serialized,
        "tightness": tight,
    }
    report = {
        "schema": "rank-three-nature-support-v1",
        "seed": SEED,
        "opened": {
            "cases": len(opened),
            "max_support": max(record["nature_support"]
                               for record in opened_records),
            "digest": digest(opened_records),
        },
        "holdouts": {
            "cases": len(holdouts),
            "max_support": max(record["nature_support"]
                               for record in holdout_records),
            "digest": digest(holdout_records),
        },
        "dense_interventions": {
            "cases": len(dense),
            "max_support": max(record["compressed_support"] for record in dense),
            "digest": digest(dense),
        },
        "tightness": tight,
        "rank_four_attacks": 40,
        "rank_four_rejections": rejected,
        "checks": checks,
        "passed": all(checks.values()),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CASES_OUT.write_text(json.dumps(cases, indent=2, sort_keys=True) + "\n")
    PRIMARY_OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
