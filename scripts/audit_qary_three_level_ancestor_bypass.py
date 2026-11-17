#!/usr/bin/env python3
"""Independent stdlib-only replay of conditioned ancestor-bypass costs."""

from __future__ import annotations

import json
import sys
from functools import cache
from pathlib import Path

PRIMARY = Path("results/qary_three_level_ancestor_bypass/results.json")
OUT = Path("results/qary_three_level_ancestor_bypass/independent_audit.json")
LEVEL_GROUPS = {
    "unrestricted": None,
    "root": frozenset((0,)),
    "middle": frozenset((1, 2)),
    "leaf": frozenset((3, 4, 5, 6)),
}


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


def six_face(level_costs):
    faces = (
        (2, 2, 4),
        (2, 3, 3),
        (2, 4, 1),
        (3, 2, 3),
        (3, 3, 1),
        (4, 1, 1),
    )
    return max(
        sum(coefficient * cost for coefficient, cost in zip(face, level_costs))
        for face in faces
    )


def exact_cost(level_costs, initial_groups):
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
            if initial_state and initial_groups is not None and group not in initial_groups:
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

    lower = -1
    upper = sum(cost * copies for _, cost, copies in groups)
    if not search(initial_counts, 0, initial_remaining, upper):
        return None
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
        conditioned = {
            level: exact_cost(costs, groups)
            for level, groups in LEVEL_GROUPS.items()
        }
        production = {
            level: record["exact_cost"]
            for level, record in item["conditioned"].items()
        }
        replays.append(
            {
                "level_costs": list(costs),
                "independent_conditioned_costs": conditioned,
                "production_conditioned_costs": production,
                "six_face_cost": six_face(costs),
                "matched": (
                    conditioned == production
                    and conditioned["unrestricted"]
                    == conditioned["root"]
                    == six_face(costs)
                ),
            }
        )
    result = {
        "schema": "theorica.qary-three-level-ancestor-bypass-audit/1",
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
