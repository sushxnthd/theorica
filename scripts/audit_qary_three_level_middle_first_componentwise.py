#!/usr/bin/env python3
"""Independent zero-import audit of the componentwise-proof falsification."""

from __future__ import annotations

import json
import sys
from functools import cache
from pathlib import Path

PRIMARY = Path("results/qary_three_level_middle_first_proof/results.json")
OUT = Path("results/qary_three_level_middle_first_proof/independent_audit.json")
FACES = (
    (1, 5, 1),
    (2, 3, 4),
    (2, 4, 3),
    (3, 3, 3),
    (3, 4, 1),
    (4, 2, 1),
)
TARGET = (3, 4, 1)


def pareto(points):
    points = set(points)
    return frozenset(
        point
        for point in points
        if not any(
            point != other
            and all(x <= y for x, y in zip(point, other))
            for other in points
        )
    )


def audit_guarantees():
    worlds = tuple(
        (x, y, z) for x in range(2) for y in range(2) for z in range(2)
    )
    queries = []
    for depth in range(3):
        for stem in sorted({world[:depth] for world in worlds}):
            queries.append(
                (
                    tuple(
                        world[depth] if world[:depth] == stem else 0
                        for world in worlds
                    ),
                    depth,
                )
            )
    answers = tuple(tuple(sorted(set(row))) for row, _ in queries)

    def successors(scores, erased, stock, query):
        row, _ = queries[query]
        rest = tuple(n - (index == query) for index, n in enumerate(stock))
        out = []
        for answer in answers[query]:
            child = tuple(
                min(2, score + (row[index] != answer))
                for index, score in enumerate(scores)
            )
            if any(score <= 1 for score in child):
                out.append((child, erased, rest))
        if erased == 0:
            out.append((scores, 1, rest))
        return tuple(out)

    @cache
    def force(scores, erased, stock, first):
        live = tuple(index for index, score in enumerate(scores) if score <= 1)
        if len(live) <= 1:
            return frozenset({(0, 0, 0)})
        per_query = []
        for query, count in enumerate(stock):
            if count == 0 or (first and query not in (1, 2)):
                continue
            row, level = queries[query]
            if len({row[index] for index in live}) < 2:
                continue
            choices = set()
            for child in successors(scores, erased, stock, query):
                choices.update(
                    tuple(value + (axis == level) for axis, value in enumerate(p))
                    for p in force(*child, False)
                )
            per_query.append(pareto(choices))
        if not per_query:
            return frozenset({(0, 0, 0)})
        current = per_query[0]
        for option in per_query[1:]:
            current = pareto(
                tuple(min(x, y) for x, y in zip(a, b))
                for a in current
                for b in option
            )
        return current

    return force((0,) * 8, 0, (4,) * 7, True)


def main():
    before = {name for name in sys.modules if name.startswith("theorica")}
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    guarantees = audit_guarantees()
    imports = len({name for name in sys.modules if name.startswith("theorica")} - before)
    expected = {face for face in FACES if face != TARGET}
    exposure = {tuple(row) for row in primary["avoidance_policy"]["maximal_exposures"]}
    costs = tuple(primary["witness_costs"])
    audit = {
        "schema": "theorica.middle-first-componentwise-audit/1",
        "production_imports": imports,
        "maximal_componentwise_guarantees": [
            list(vector) for vector in sorted(guarantees)
        ],
        "missing_target": list(TARGET),
        "avoidance_exposure_worst_cost": max(
            sum(x * y for x, y in zip(vector, costs)) for vector in exposure
        ),
        "avoidance_target_dominated": any(
            all(x >= y for x, y in zip(vector, TARGET)) for vector in exposure
        ),
    }
    audit["passed"] = (
        imports == 0
        and guarantees == expected
        and audit["avoidance_exposure_worst_cost"] == 554
        and not audit["avoidance_target_dominated"]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2, sort_keys=True))
    raise SystemExit(0 if audit["passed"] else 1)


if __name__ == "__main__":
    main()
