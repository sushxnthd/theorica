#!/usr/bin/env python3
"""Synthesize and prospectively test the frozen finite policy fan."""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations, product
from math import gcd
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

PRIOR = Path("results/qary_ternary_minimal_obstruction_cost_cone/results.json")
OUT = Path("results/qary_ternary_minimal_obstruction_policy_fan/results.json")
PREDICTIONS = Path("results/qary_ternary_minimal_obstruction_policy_fan/predictions.json")
BASE = tuple(product(range(2), repeat=3))
FIBER = ((2, 0, 0), (2, 1, 0), (2, 2, 0))
PAIRS = tuple(combinations(FIBER, 2))
DISCOVERY = tuple(
    costs
    for costs in product(range(1, 5), repeat=3)
    if gcd(gcd(costs[0], costs[1]), costs[2]) == 1
)
UNOPENED = (
    (3, 10, 3),
    (4, 11, 2),
    (5, 13, 4),
    (7, 19, 5),
    (11, 29, 7),
    (13, 34, 9),
)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def games(count):
    return tuple(
        (
            (1 - (p := Fraction(index + 1, count + 1)), p - 1),
            (-p, p),
        )
        for index in range(count)
    )


def pair_key(pair):
    return tuple(tuple(word) for word in pair)


def level(index):
    if index < 4:
        return 0
    if index < 16:
        return 1
    return 2


def pareto_exposures(root):
    terminal = []

    def walk(node, exposure):
        if node.query_index is None:
            terminal.append(exposure)
            return
        next_exposure = list(exposure)
        next_exposure[level(node.query_index)] += 1
        for _, child in node.children:
            walk(child, tuple(next_exposure))

    walk(root, (0, 0, 0))
    unique = set(terminal)
    return tuple(
        sorted(
            point
            for point in unique
            if not any(
                other != point and all(x >= y for x, y in zip(other, point))
                for other in unique
            )
        )
    )


def problem(pair):
    words = (*BASE, *pair)
    indices = tuple(
        sum(symbol * 3 ** (2 - i) for i, symbol in enumerate(word))
        for word in words
    )
    rows = qary_prefix_query_library(3, 3, copies=4)
    return tuple(tuple(row[index] for index in indices) for row in rows)


def solve(costs, pair, upper_bound):
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(10),
        problem(pair),
        query_costs=qary_prefix_query_costs(
            3, 3, copies=4, level_costs=costs
        ),
        corruption_budget=1,
        erasure_budget=1,
        allowed_initial_query_indices=range(4, 16),
        known_feasible_cost_upper_bound=upper_bound,
    )
    return plan


def fan_prediction(fan, costs):
    ranked = sorted(
        (
            max(dot(exposure, costs) for exposure in item["exposures"]),
            tuple(item["source_costs"]),
            item,
        )
        for item in fan
    )
    return ranked[0][0], ranked[0][2]


def main():
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    opened_rows = [row for row in prior["cases"] if "exact_cost" in row]
    opened = {
        (tuple(row["level_costs"]), pair_key(row["pair"])): row["exact_cost"]
        for row in opened_rows
    }
    fans = []
    synthesis_states = 0
    for pair_index, pair in enumerate(PAIRS):
        distinct = {}
        for costs in DISCOVERY:
            exact = opened[(costs, pair_key(pair))]
            plan = solve(costs, pair, exact)
            if not plan.certificate_valid or plan.worst_case_cost != exact:
                raise RuntimeError(f"discovery synthesis failed: {pair=} {costs=}")
            exposures = pareto_exposures(plan.root)
            distinct.setdefault(exposures, costs)
            synthesis_states += plan.states_solved
        fan = [
            {"source_costs": list(source), "exposures": [list(row) for row in exposures]}
            for exposures, source in sorted(distinct.items())
        ]
        fans.append(fan)

    calibration = []
    for opened_row in opened_rows:
        costs = tuple(opened_row["level_costs"])
        pair = pair_key(opened_row["pair"])
        exact = opened_row["exact_cost"]
        pair_index = tuple(map(pair_key, PAIRS)).index(pair)
        predicted, witness = fan_prediction(fans[pair_index], costs)
        calibration.append(
            {
                "level_costs": list(costs),
                "pair_index": pair_index,
                "exact_cost": exact,
                "predicted_cost": predicted,
                "source_costs": witness["source_costs"],
                "matched": predicted == exact,
            }
        )
    calibration_passed = len(calibration) == 181 and all(
        row["matched"] for row in calibration
    )
    if not calibration_passed:
        first_mismatch = next(row for row in calibration if not row["matched"])
        summary = {
            "discovery_cases_synthesized": len(DISCOVERY) * len(PAIRS),
            "distinct_policies_by_pair": [len(fan) for fan in fans],
            "calibration_cases": len(calibration),
            "calibration_matches": sum(row["matched"] for row in calibration),
            "synthesis_states_solved": synthesis_states,
            "first_mismatch": first_mismatch,
            "fan_passed_calibration": False,
            "fan_falsified": True,
            "prospective_holdouts_opened": 0,
            "experiment_completed": True,
            "passed": True,
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(
            json.dumps(
                {
                    "schema": "theorica.ternary-minimal-obstruction-policy-fan/1",
                    "fans": fans,
                    "calibration": calibration,
                    "prospective": [],
                    "summary": summary,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return

    frozen_predictions = []
    for pair_index, pair in enumerate(PAIRS):
        costs_list = (((2, 9, 3),) if pair_index else ()) + UNOPENED
        for costs in costs_list:
            predicted, witness = fan_prediction(fans[pair_index], costs)
            frozen_predictions.append(
                {
                    "level_costs": list(costs),
                    "pair_index": pair_index,
                    "pair": [list(word) for word in pair],
                    "predicted_cost": predicted,
                    "source_costs": witness["source_costs"],
                    "exposures": witness["exposures"],
                }
            )
    PREDICTIONS.parent.mkdir(parents=True, exist_ok=True)
    PREDICTIONS.write_text(
        json.dumps(
            {
                "schema": "theorica.ternary-minimal-obstruction-policy-fan-predictions/1",
                "calibration_passed": True,
                "predictions": frozen_predictions,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    prospective = []
    first_mismatch = None
    for prediction in frozen_predictions:
        if first_mismatch is not None:
            break
        costs = tuple(prediction["level_costs"])
        pair = PAIRS[prediction["pair_index"]]
        plan = solve(costs, pair, prediction["predicted_cost"])
        row = {
            **prediction,
            "exact_cost": plan.worst_case_cost,
            "states_solved": plan.states_solved,
            "certificate_valid": plan.certificate_valid,
            "matched": plan.certificate_valid
            and plan.worst_case_cost == prediction["predicted_cost"],
        }
        prospective.append(row)
        if not row["matched"]:
            first_mismatch = row

    summary = {
        "discovery_cases_synthesized": len(DISCOVERY) * len(PAIRS),
        "distinct_policies_by_pair": [len(fan) for fan in fans],
        "calibration_cases": len(calibration),
        "calibration_matches": sum(row["matched"] for row in calibration),
        "prospective_cases_planned": len(frozen_predictions),
        "prospective_cases_run": len(prospective),
        "prospective_matches": sum(row["matched"] for row in prospective),
        "synthesis_states_solved": synthesis_states,
        "prospective_states_solved": sum(row["states_solved"] for row in prospective),
        "first_mismatch": first_mismatch,
        "fan_supported_on_holdouts": first_mismatch is None
        and len(prospective) == len(frozen_predictions),
        "fan_falsified": first_mismatch is not None,
    }
    summary["experiment_completed"] = (
        summary["fan_supported_on_holdouts"] or summary["fan_falsified"]
    )
    summary["passed"] = summary["experiment_completed"]
    OUT.write_text(
        json.dumps(
            {
                "schema": "theorica.ternary-minimal-obstruction-policy-fan/1",
                "fans": fans,
                "calibration": calibration,
                "prospective": prospective,
                "summary": summary,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
