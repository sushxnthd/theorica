#!/usr/bin/env python3
"""Independent stdlib-only audit of policy-fan arithmetic and fail-closed order."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

SOURCE = Path("results/qary_ternary_minimal_obstruction_policy_fan/results.json")
PRIOR = Path("results/qary_ternary_minimal_obstruction_cost_cone/results.json")
PREDICTIONS = Path("results/qary_ternary_minimal_obstruction_policy_fan/predictions.json")
OUT = Path("results/qary_ternary_minimal_obstruction_policy_fan/audit.json")


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def key(pair):
    return tuple(tuple(word) for word in pair)


def predict(fan, costs):
    return min(
        (
            max(dot(exposure, costs) for exposure in item["exposures"]),
            tuple(item["source_costs"]),
        )
        for item in fan
    )


def main():
    raw = SOURCE.read_bytes()
    source = json.loads(raw)
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    pairs = []
    for row in prior["cases"]:
        candidate = key(row["pair"])
        if candidate not in pairs:
            pairs.append(candidate)

    antichain_checks = []
    source_cost_checks = []
    for fan in source["fans"]:
        for item in fan:
            exposures = [tuple(row) for row in item["exposures"]]
            antichain_checks.append(
                len(exposures) == len(set(exposures))
                and all(
                    not any(
                        other != point
                        and all(x >= y for x, y in zip(other, point))
                        for other in exposures
                    )
                    for point in exposures
                )
            )
            source_cost_checks.append(
                all(1 <= value <= 4 for value in item["source_costs"])
            )

    replay = []
    for row, recorded in zip(prior["cases"], source["calibration"], strict=True):
        pair_index = pairs.index(key(row["pair"]))
        costs = tuple(row["level_costs"])
        prediction, source_costs = predict(source["fans"][pair_index], costs)
        replay.append(
            recorded["pair_index"] == pair_index
            and recorded["level_costs"] == list(costs)
            and recorded["exact_cost"] == row["exact_cost"]
            and recorded["predicted_cost"] == prediction
            and recorded["source_costs"] == list(source_costs)
            and recorded["matched"] == (prediction == row["exact_cost"])
        )

    mismatches = [row for row in source["calibration"] if not row["matched"]]
    expected_failure = len(mismatches) == 1 and mismatches[0] == {
        "exact_cost": 51,
        "level_costs": [2, 9, 3],
        "matched": False,
        "pair_index": 0,
        "predicted_cost": 52,
        "source_costs": [1, 1, 1],
    }
    summary = {
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "fans": len(source["fans"]),
        "policies_checked": sum(len(fan) for fan in source["fans"]),
        "antichains_valid": sum(antichain_checks),
        "antichains_total": len(antichain_checks),
        "source_costs_valid": sum(source_cost_checks),
        "source_costs_total": len(source_cost_checks),
        "calibration_replays_passed": sum(replay),
        "calibration_replays_total": len(replay),
        "expected_unique_failure": expected_failure,
        "prospective_rows_absent": source["prospective"] == [],
        "prediction_snapshot_absent": not PREDICTIONS.exists(),
    }
    summary["passed"] = (
        len(source["fans"]) == 3
        and all(antichain_checks)
        and all(source_cost_checks)
        and len(replay) == 181
        and all(replay)
        and expected_failure
        and summary["prospective_rows_absent"]
        and summary["prediction_snapshot_absent"]
    )
    OUT.write_text(
        json.dumps(
            {
                "schema": "theorica.ternary-minimal-obstruction-policy-fan-audit/1",
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
