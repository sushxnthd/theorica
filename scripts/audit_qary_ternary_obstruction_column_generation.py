#!/usr/bin/env python3
"""Independent zero-THEORICA-import audit of column-generation falsification."""

from __future__ import annotations

import hashlib
import json
from functools import cache
from itertools import product
from pathlib import Path

SOURCE = Path("results/qary_ternary_obstruction_column_generation/results.json")
PREDICTIONS = Path("results/qary_ternary_obstruction_column_generation/predictions.json")
OUT = Path("results/qary_ternary_obstruction_column_generation/audit.json")
BASE = tuple(product(range(2), repeat=3))


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def groups(words, costs):
    answer = []
    for level in range(3):
        for prefix in product(range(3), repeat=level):
            row = tuple(word[level] if word[:level] == prefix else 0 for word in words)
            answer.append((row, costs[level]))
    return tuple(answer)


def exact_boundary(words, costs, bound):
    query_groups = groups(words, costs)
    alphabets = tuple(tuple(sorted(set(row))) for row, _ in query_groups)
    initial_remaining = (4,) * len(query_groups)
    initial_counts = (0,) * len(words)
    states = 0

    @cache
    def feasible(counts, erased, remaining, budget, initial):
        nonlocal states
        states += 1
        live = tuple(index for index, count in enumerate(counts) if count <= 1)
        if len(live) <= 1:
            return True
        for group, multiplicity in enumerate(remaining):
            row, cost = query_groups[group]
            if multiplicity == 0 or cost > budget or (initial and group not in range(1, 4)):
                continue
            if len({row[index] for index in live}) < 2:
                continue
            rest = tuple(value - (index == group) for index, value in enumerate(remaining))
            children = []
            for observed in alphabets[group]:
                child = tuple(
                    min(2, count + (row[index] != observed))
                    for index, count in enumerate(counts)
                )
                if any(value <= 1 for value in child):
                    children.append((child, erased))
            if erased == 0:
                children.append((counts, 1))
            if children and all(
                feasible(child, child_erased, rest, budget - cost, False)
                for child, child_erased in children
            ):
                return True
        return False

    at_bound = feasible(initial_counts, 0, initial_remaining, bound, True)
    below = feasible(initial_counts, 0, initial_remaining, bound - 1, True)
    return at_bound, below, states


def policy_cost(column, costs):
    return max(dot(exposure, costs) for exposure in column["exposures"])


def main():
    raw = SOURCE.read_bytes()
    source = json.loads(raw)
    frozen = json.loads(PREDICTIONS.read_text(encoding="utf-8"))
    prospective = source["prospective"]
    if len(prospective) != 1:
        raise RuntimeError("fail-fast prefix is not exactly one case")
    row = prospective[0]
    costs = tuple(row["level_costs"])
    pair = tuple(tuple(word) for word in row["pair"])
    fan = source["fans"][row["pair_index"]]
    recomputed = min(policy_cost(column, costs) for column in fan)
    feasible, below, states = exact_boundary((*BASE, *pair), costs, row["exact_cost"])
    added = source["additions"]
    expected_antichain = [
        [1, 5, 1], [3, 3, 5], [3, 4, 3], [3, 5, 0],
        [4, 2, 2], [4, 3, 1], [4, 4, 0],
    ]
    summary = {
        "zero_theorica_imports": True,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "calibration_cases": len(source["calibration"]),
        "calibration_matches": sum(row["matched"] for row in source["calibration"]),
        "columns_added": len(added),
        "added_antichain_exact": len(added) == 1 and added[0]["exposures"] == expected_antichain,
        "frozen_predictions": len(frozen["predictions"]),
        "fail_fast_cases": len(prospective),
        "fan_prediction_recomputed": recomputed,
        "recorded_prediction": row["predicted_cost"],
        "recorded_exact": row["exact_cost"],
        "feasible_at_exact": feasible,
        "infeasible_one_below": not below,
        "independent_states": states,
    }
    summary["passed"] = (
        summary["calibration_cases"] == summary["calibration_matches"] == 181
        and summary["added_antichain_exact"]
        and summary["frozen_predictions"] == 20
        and summary["fail_fast_cases"] == 1
        and recomputed == row["predicted_cost"] == 52
        and row["exact_cost"] == 51
        and feasible
        and not below
        and source["summary"]["column_fan_falsified"]
    )
    OUT.write_text(
        json.dumps(
            {
                "schema": "theorica.ternary-obstruction-column-generation-audit/1",
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
