#!/usr/bin/env python3
"""Independent stdlib-only replay of decision corruption-radius evidence."""

from __future__ import annotations

import hashlib
import json
import sys
from itertools import product
from pathlib import Path

SOURCE = Path("results/decision_corruption_radius/results.json")
OUT = Path("results/decision_corruption_radius/independent_audit.json")


def hamming(left, right):
    return sum(a != b for a, b in zip(left, right))


def exact_radius(words):
    alphabets = [sorted({word[index] for word in words})
                 for index in range(len(words[0]))]
    return min(
        max(hamming(center, word) for word in words)
        for center in product(*alphabets)
    )


def main():
    production_before = {name for name in sys.modules if name.startswith("theorica")}
    primary = json.loads(SOURCE.read_text(encoding="utf-8"))
    cases = []
    for actions in range(3, 7):
        unit = tuple(
            tuple(int(completion == coordinate) for coordinate in range(actions))
            for completion in range(actions)
        )
        tripled = tuple(
            tuple(value for value in word for _ in range(3)) for word in unit
        )
        cases.append({
            "family": "higher-order-unit-code",
            "actions": actions,
            "radius": exact_radius(unit),
            "passed": exact_radius(unit) == 1,
        })
        cases.append({
            "family": "higher-order-tripled-unit-code",
            "actions": actions,
            "radius": exact_radius(tripled),
            "passed": exact_radius(tripled) == 3,
        })

    for distance in range(1, 19):
        first = (0,) * distance
        second = (1,) * distance
        observed = exact_radius((first, second))
        cases.append({
            "family": "pair-radius",
            "distance": distance,
            "radius": observed,
            "passed": observed == (distance + 1) // 2,
        })

    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":"))
    result = {
        "schema": "theorica.decision-corruption-radius-audit/1",
        "cases_passed": sum(case["passed"] for case in cases),
        "cases_total": len(cases),
        "primary_passed": primary["summary"]["passed"],
        "production_imports": len(
            {name for name in sys.modules if name.startswith("theorica")}
            - production_before
        ),
        "audit_digest": hashlib.sha256(canonical.encode()).hexdigest(),
    }
    result["passed"] = (
        result["cases_passed"] == result["cases_total"]
        and result["primary_passed"]
        and result["production_imports"] == 0
    )
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
