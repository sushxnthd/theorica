#!/usr/bin/env python3
"""Independent stdlib-only replay of middle-first conditioned holdouts."""

from __future__ import annotations

import json
import sys
from functools import cache
from pathlib import Path

PRIMARY = Path("results/qary_three_level_middle_first/results.json")
OUT = Path("results/qary_three_level_middle_first/independent_audit.json")
FACES = (
    (1, 5, 1),
    (2, 3, 4),
    (2, 4, 3),
    (3, 3, 3),
    (3, 4, 1),
    (4, 2, 1),
)


def groups_for(level_costs):
    words = tuple(
        (root, middle, leaf)
        for root in range(2)
        for middle in range(2)
        for leaf in range(2)
    )
    groups = []
    for level, cost in enumerate(level_costs):
        for prefix in sorted({word[:level] for word in words}):
            row = tuple(
                word[level] if word[:level] == prefix else 0
                for word in words
            )
            groups.append((row, cost, 4))
    return tuple(groups)


def candidate(level_costs):
    values = tuple(
        sum(coefficient * cost for coefficient, cost in zip(face, level_costs))
        for face in FACES
    )
    optimum = max(values)
    return optimum, tuple(face for face, value in zip(FACES, values) if value == optimum)


def exact_middle_first(level_costs):
    groups = groups_for(level_costs)
    alphabets = tuple(tuple(sorted(set(row))) for row, _, _ in groups)
    initial_remaining = tuple(copies for _, _, copies in groups)
    initial_counts = (0,) * 8

    @cache
    def search(counts, erased, remaining, limit):
        feasible = tuple(index for index, count in enumerate(counts) if count <= 1)
        if len(feasible) <= 1:
            return True
        initial_state = (
            counts == initial_counts and erased == 0 and remaining == initial_remaining
        )
        candidates = []
        for group, count in enumerate(remaining):
            row, cost, _ = groups[group]
            if count == 0 or cost > limit:
                continue
            if initial_state and group not in (1, 2):
                continue
            cells = {}
            for index in feasible:
                cells[row[index]] = cells.get(row[index], 0) + 1
            if len(cells) > 1:
                candidates.append((cost, max(cells.values()), group))
        for _, _, group in sorted(candidates):
            row, cost, _ = groups[group]
            next_remaining = tuple(
                count - (index == group) for index, count in enumerate(remaining)
            )
            children = []
            for answer in alphabets[group]:
                child = tuple(
                    min(2, count + (row[index] != answer))
                    for index, count in enumerate(counts)
                )
                if any(count <= 1 for count in child):
                    children.append((child, erased))
            if erased < 1:
                children.append((counts, erased + 1))
            if children and all(
                search(child, child_erased, next_remaining, limit - cost)
                for child, child_erased in children
            ):
                return True
        return False

    upper, _ = candidate(level_costs)
    if not search(initial_counts, 0, initial_remaining, upper):
        return None
    lower = -1
    while upper - lower > 1:
        middle = (lower + upper) // 2
        if search(initial_counts, 0, initial_remaining, middle):
            upper = middle
        else:
            lower = middle
    return upper


def main():
    before = {name for name in sys.modules if name.startswith("theorica")}
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    replays = []
    for item in primary["holdouts"]:
        costs = tuple(item["level_costs"])
        actual = exact_middle_first(costs)
        expected, active = candidate(costs)
        replays.append(
            {
                "level_costs": list(costs),
                "independent_exact_cost": actual,
                "production_exact_cost": item["exact_middle_first_cost"],
                "candidate_cost": expected,
                "active_faces": [list(face) for face in active],
                "matched": (
                    actual == item["exact_middle_first_cost"] == expected
                    and item["active_faces"] == [list(face) for face in active]
                ),
            }
        )
    result = {
        "schema": "theorica.qary-three-level-middle-first-audit/1",
        "production_imports": len(
            {name for name in sys.modules if name.startswith("theorica")} - before
        ),
        "case_total": len(replays),
        "cases_reproduced": sum(item["matched"] for item in replays),
        "replays": replays,
    }
    result["passed"] = (
        result["production_imports"] == 0
        and result["cases_reproduced"] == result["case_total"] == 12
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
