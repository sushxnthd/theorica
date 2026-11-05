#!/usr/bin/env python3
"""Independent stdlib-only audit of the root-respecting recurrence."""

from __future__ import annotations

import hashlib
import json
import sys
from itertools import product
from pathlib import Path

PRIMARY = Path("results/qary_root_respecting_insurance/results.json")
OUT = Path("results/qary_root_respecting_insurance/independent_audit.json")


def faces(depth):
    result = []
    for hidden in range(depth):
        result.append((2,) * hidden + (4,) + (1,) * (depth - hidden - 1))
    for first in range(depth - 1):
        for second in range(depth - first - 1):
            result.append(
                (2,) * first
                + (3,)
                + (2,) * second
                + (3,)
                + (1,) * (depth - first - second - 2)
            )
    return tuple(result)


def recurrence(costs):
    no_fault = costs[-1]
    substitution = 3 * costs[-1]
    mixed = 4 * costs[-1]
    for cost in reversed(costs[:-1]):
        mixed = max(2 * cost + mixed, 3 * cost + substitution, 4 * cost + no_fault)
        substitution = max(2 * cost + substitution, 3 * cost + no_fault)
        no_fault = cost + no_fault
    return mixed


def evaluate(costs):
    vectors = faces(len(costs))
    face_maximum = max(
        sum(coefficient * cost for coefficient, cost in zip(vector, costs))
        for vector in vectors
    )
    return vectors, face_maximum, recurrence(costs)


def main():
    before = {name for name in sys.modules if name.startswith("theorica")}
    primary = json.loads(PRIMARY.read_text())
    replays = []
    for item in primary["holdouts"]:
        vectors, face_maximum, value = evaluate(tuple(item["level_costs"]))
        replays.append(
            {
                "arity": item["arity"],
                "depth": item["depth"],
                "face_count": len(vectors),
                "face_maximum": face_maximum,
                "recurrence_cost": value,
                "matched": (
                    [list(vector) for vector in vectors] == item["face_vectors"]
                    and face_maximum == value == item["exact_root_respecting_cost"]
                ),
            }
        )
    exhaustive = []
    for depth in range(1, 7):
        for costs in product((1, 2, 3), repeat=depth):
            vectors, face_maximum, value = evaluate(costs)
            exhaustive.append(
                {
                    "arity": 2 + sum(costs) % 4,
                    "depth": depth,
                    "level_costs": list(costs),
                    "face_count": len(vectors),
                    "value": value,
                    "matched": face_maximum == value,
                }
            )
    payload = json.dumps(exhaustive, sort_keys=True, separators=(",", ":"))
    imports = sorted(
        {name for name in sys.modules if name.startswith("theorica")} - before
    )
    result = {
        "schema": "theorica.qary-root-respecting-insurance-audit/1",
        "holdout_replays": sum(item["matched"] for item in replays),
        "holdout_total": len(replays),
        "exhaustive_replays": sum(item["matched"] for item in exhaustive),
        "exhaustive_total": len(exhaustive),
        "exhaustive_digest_reproduced": hashlib.sha256(payload.encode()).hexdigest()
        == primary["summary"]["exhaustive_digest"],
        "production_imports": imports,
        "replays": replays,
    }
    result["passed"] = (
        result["holdout_replays"] == result["holdout_total"] == 5
        and result["exhaustive_replays"] == result["exhaustive_total"] == 1092
        and result["exhaustive_digest_reproduced"]
        and not imports
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
