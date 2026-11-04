#!/usr/bin/env python3
"""Run the frozen counterexample-guided policy-column experiment."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

FAN_SOURCE = Path("results/qary_ternary_minimal_obstruction_policy_fan/results.json")
PRIOR = Path("results/qary_ternary_minimal_obstruction_cost_cone/results.json")
OUT = Path("results/qary_ternary_obstruction_column_generation/results.json")
PREDICTIONS = Path("results/qary_ternary_obstruction_column_generation/predictions.json")
HELPER_PATH = Path("scripts/verify_qary_ternary_minimal_obstruction_policy_fan.py")

SPEC = importlib.util.spec_from_file_location("policy_fan_helper", HELPER_PATH)
assert SPEC is not None and SPEC.loader is not None
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)

PAIRS = HELPER.PAIRS
UNOPENED_COSTS = (
    (3, 10, 3),
    (4, 11, 2),
    (5, 13, 4),
    (7, 19, 5),
    (11, 29, 7),
    (13, 34, 9),
)


def pair_key(pair):
    return tuple(tuple(word) for word in pair)


def prediction(fan, costs):
    value, witness = HELPER.fan_prediction(fan, costs)
    return value, witness


def replay(fans, opened_rows):
    rows = []
    first_mismatch = None
    pair_keys = tuple(map(pair_key, PAIRS))
    for index, row in enumerate(opened_rows):
        costs = tuple(row["level_costs"])
        pair_index = pair_keys.index(pair_key(row["pair"]))
        predicted, witness = prediction(fans[pair_index], costs)
        record = {
            "case_index": index,
            "level_costs": list(costs),
            "pair_index": pair_index,
            "exact_cost": row["exact_cost"],
            "predicted_cost": predicted,
            "source_costs": witness["source_costs"],
            "matched": predicted == row["exact_cost"],
        }
        rows.append(record)
        if not record["matched"] and first_mismatch is None:
            first_mismatch = record
    return rows, first_mismatch


def main():
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    opened_rows = [row for row in prior["cases"] if "exact_cost" in row]
    source = json.loads(FAN_SOURCE.read_text(encoding="utf-8"))
    fans = [[dict(column) for column in fan] for fan in source["fans"]]
    initial_counts = [len(fan) for fan in fans]
    additions = []
    synthesis_states = 0

    while True:
        calibration, mismatch = replay(fans, opened_rows)
        if mismatch is None:
            break
        pair_index = mismatch["pair_index"]
        costs = tuple(mismatch["level_costs"])
        plan = HELPER.solve(costs, PAIRS[pair_index], mismatch["exact_cost"])
        antichain = HELPER.pareto_exposures(plan.root)
        serialized = [list(row) for row in antichain]
        if any(column["exposures"] == serialized for column in fans[pair_index]):
            raise RuntimeError("calibration mismatch produced no new policy column")
        column = {
            "source_costs": list(costs),
            "exposures": serialized,
            "source_role": "opened_calibration_counterexample",
        }
        fans[pair_index].append(column)
        additions.append(
            {
                "iteration": len(additions) + 1,
                "pair_index": pair_index,
                "level_costs": list(costs),
                "exact_cost": plan.worst_case_cost,
                "states_solved": plan.states_solved,
                "exposures": serialized,
            }
        )
        synthesis_states += plan.states_solved

    if len(calibration) != 181 or not all(row["matched"] for row in calibration):
        raise RuntimeError("calibration closure invariant failed")

    prospective_order = [
        ((2, 9, 3), pair_index) for pair_index in (1, 2)
    ] + [
        (costs, pair_index)
        for costs in UNOPENED_COSTS
        for pair_index in range(len(PAIRS))
    ]
    frozen = []
    for costs, pair_index in prospective_order:
        predicted, witness = prediction(fans[pair_index], costs)
        frozen.append(
            {
                "level_costs": list(costs),
                "pair_index": pair_index,
                "pair": [list(word) for word in PAIRS[pair_index]],
                "predicted_cost": predicted,
                "source_costs": witness["source_costs"],
                "source_role": witness.get("source_role", "discovery_policy"),
                "exposures": witness["exposures"],
            }
        )
    PREDICTIONS.parent.mkdir(parents=True, exist_ok=True)
    PREDICTIONS.write_text(
        json.dumps(
            {
                "schema": "theorica.ternary-obstruction-column-predictions/1",
                "calibration_closed": True,
                "predictions": frozen,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    prospective = []
    first_mismatch = None
    for item in frozen:
        if first_mismatch is not None:
            break
        pair_index = item["pair_index"]
        costs = tuple(item["level_costs"])
        plan = HELPER.solve(costs, PAIRS[pair_index], item["predicted_cost"])
        row = {
            **item,
            "exact_cost": plan.worst_case_cost,
            "states_solved": plan.states_solved,
            "certificate_valid": plan.certificate_valid,
            "matched": plan.certificate_valid
            and plan.worst_case_cost == item["predicted_cost"],
        }
        prospective.append(row)
        if not row["matched"]:
            first_mismatch = row

    summary = {
        "initial_columns_by_pair": initial_counts,
        "columns_added": len(additions),
        "final_columns_by_pair": [len(fan) for fan in fans],
        "calibration_cases": len(calibration),
        "calibration_matches": sum(row["matched"] for row in calibration),
        "column_synthesis_states": synthesis_states,
        "prospective_cases_planned": len(frozen),
        "prospective_cases_run": len(prospective),
        "prospective_matches": sum(row["matched"] for row in prospective),
        "prospective_states_solved": sum(row["states_solved"] for row in prospective),
        "first_mismatch": first_mismatch,
        "column_fan_supported": first_mismatch is None
        and len(prospective) == len(frozen),
        "column_fan_falsified": first_mismatch is not None,
    }
    summary["experiment_completed"] = (
        summary["column_fan_supported"] or summary["column_fan_falsified"]
    )
    summary["passed"] = summary["experiment_completed"]
    OUT.write_text(
        json.dumps(
            {
                "schema": "theorica.ternary-obstruction-column-generation/1",
                "additions": additions,
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
