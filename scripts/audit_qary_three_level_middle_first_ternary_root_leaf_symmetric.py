#!/usr/bin/env python3
"""Independent stdlib-only audit of the ternary (1,3,1) counterexample."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

SOURCE = Path(
    "results/qary_three_level_middle_first_ternary_root_leaf_symmetric/results.json"
)
OUT = Path(
    "results/qary_three_level_middle_first_ternary_root_leaf_symmetric/audit.json"
)
ARITY = 3
LEVEL_COSTS = (1, 3, 1)


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


def exact_weighted_boundary():
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
        for group, count in enumerate(remaining):
            if count == 0 or (initial and group not in range(1, ARITY + 1)):
                continue
            row, level, _ = query_groups[group]
            cost = LEVEL_COSTS[level]
            if cost > budget or len({row[index] for index in live}) < 2:
                continue
            descendants = children(counts, erased, remaining, group)
            if descendants and all(
                feasible(*child, budget - cost, False) for child in descendants
            ):
                return True
        return False

    initial = ((0,) * (ARITY**3), 0, (4,) * len(query_groups))
    lower_feasible = feasible(*initial, 17, True)
    upper_feasible = feasible(*initial, 18, True)
    return lower_feasible, upper_feasible, states


def main():
    primary = json.loads(SOURCE.read_text(encoding="utf-8"))
    lower, upper, states = exact_weighted_boundary()
    candidate_values = (2 + 5 * 3, 5 + 4 * 3, 6 + 3 * 3)
    report = {
        "production_module_imports": 0,
        "independent_cost_17_feasible": lower,
        "independent_cost_18_feasible": upper,
        "independent_states_solved": states,
        "independent_candidate_face_values": list(candidate_values),
        "independent_candidate_value": max(candidate_values),
        "primary_exact_value": primary["counterexample"]["exact_value"],
        "primary_states_solved": primary["states_solved"],
    }
    report["passed"] = (
        not lower
        and upper
        and report["independent_candidate_value"] == 17
        and report["primary_exact_value"] == 18
        and primary["passed"]
    )
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
