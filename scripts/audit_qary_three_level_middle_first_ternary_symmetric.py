#!/usr/bin/env python3
"""Independent stdlib-only depth audit of the ternary symmetric theorem."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

SOURCE = Path("results/qary_three_level_middle_first_ternary_symmetric/results.json")
OUT = Path("results/qary_three_level_middle_first_ternary_symmetric/audit.json")
ARITY = 3


def groups():
    words = tuple(
        (root, middle, leaf)
        for root in range(ARITY)
        for middle in range(ARITY)
        for leaf in range(ARITY)
    )
    answer = []
    for level in range(3):
        for prefix in sorted({word[:level] for word in words}):
            row = tuple(
                word[level] if word[:level] == prefix else 0 for word in words
            )
            answer.append((row, level, 4))
    return tuple(answer)


def exact_depth():
    query_groups = groups()
    alphabets = tuple(tuple(sorted(set(row))) for row, _, _ in query_groups)
    states = 0

    def children(counts, erased, remaining, group):
        row, _, _ = query_groups[group]
        rest = tuple(
            count - (index == group) for index, count in enumerate(remaining)
        )
        answer = []
        for observed in alphabets[group]:
            child = tuple(
                min(2, count + (row[index] != observed))
                for index, count in enumerate(counts)
            )
            if any(count <= 1 for count in child):
                answer.append((child, erased, rest))
        if erased == 0:
            answer.append((counts, 1, rest))
        return tuple(answer)

    @cache
    def feasible(counts, erased, remaining, budget, initial):
        nonlocal states
        states += 1
        live = tuple(index for index, count in enumerate(counts) if count <= 1)
        if len(live) <= 1:
            return True
        if budget == 0:
            return False
        for group, count in enumerate(remaining):
            if count == 0 or (initial and group not in range(1, ARITY + 1)):
                continue
            row, _, _ = query_groups[group]
            if len({row[index] for index in live}) < 2:
                continue
            descendants = children(counts, erased, remaining, group)
            if descendants and all(
                feasible(*child, budget - 1, False) for child in descendants
            ):
                return True
        return False

    initial = ((0,) * (ARITY**3), 0, (4,) * len(query_groups))
    lower_feasible = feasible(*initial, 8, True)
    upper_feasible = feasible(*initial, 9, True)
    return lower_feasible, upper_feasible, states


def main():
    primary = json.loads(SOURCE.read_text(encoding="utf-8"))
    lower, upper, states = exact_depth()
    report = {
        "production_module_imports": 0,
        "independent_depth_8_feasible": lower,
        "independent_depth_9_feasible": upper,
        "independent_states_solved": states,
        "primary_exact_unit_cost": primary["exact_unit_cost"],
        "binary_embedding_lower_bound": primary["binary_embedding_lower_bound"],
        "scale_checks": sum(
            row["predicted_exact_cost"] == 9 * row["level_cost"]
            for row in primary["prospective_scales"]
        ),
        "scale_total": len(primary["prospective_scales"]),
    }
    report["passed"] = (
        not lower
        and upper
        and report["primary_exact_unit_cost"] == 9
        and report["binary_embedding_lower_bound"] == 9
        and report["scale_checks"] == report["scale_total"] == 6
    )
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
