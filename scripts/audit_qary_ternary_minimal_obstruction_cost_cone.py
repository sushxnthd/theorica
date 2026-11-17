#!/usr/bin/env python3
"""Independent stdlib-only audit of the minimal-obstruction cost cone."""

from __future__ import annotations

import json
from functools import cache
from itertools import combinations, product
from math import gcd
from pathlib import Path

SOURCE = Path("results/qary_ternary_minimal_obstruction_cost_cone/results.json")
OUT = Path("results/qary_ternary_minimal_obstruction_cost_cone/audit.json")
BASE = tuple(product(range(2), repeat=3))
FIBER = ((2, 0, 0), (2, 1, 0), (2, 2, 0))
PAIRS = tuple(combinations(FIBER, 2))
FACES = ((1, 5, 1), (2, 3, 4), (2, 4, 3), (3, 3, 3), (3, 4, 1), (4, 2, 1))
NEW_FACE = (2, 5, 1)
HOLDOUTS = (
    (1, 5, 1), (2, 5, 2), (1, 4, 2), (2, 7, 1),
    (3, 8, 2), (2, 9, 3), (3, 10, 3), (4, 11, 2),
    (5, 13, 4), (7, 19, 5), (11, 29, 7), (13, 34, 9),
)


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
    terminal_cache = {}
    states = 0

    def terminal(counts):
        live = tuple(index for index, count in enumerate(counts) if count <= 1)
        if live not in terminal_cache:
            # The synthetic games have distinct robust values; one live word is terminal.
            terminal_cache[live] = len(live) <= 1
        return terminal_cache[live]

    @cache
    def feasible(counts, erased, remaining, budget, initial):
        nonlocal states
        states += 1
        if terminal(counts):
            return True
        for group, multiplicity in enumerate(remaining):
            row, cost = query_groups[group]
            if multiplicity == 0 or cost > budget or (initial and group not in range(1, 4)):
                continue
            live = tuple(index for index, count in enumerate(counts) if count <= 1)
            if len({row[index] for index in live}) < 2:
                continue
            rest = tuple(value - (index == group) for index, value in enumerate(remaining))
            children = []
            for observed in alphabets[group]:
                child = tuple(min(2, count + (row[index] != observed)) for index, count in enumerate(counts))
                if any(value <= 1 for value in child):
                    children.append((child, erased))
            if erased == 0:
                children.append((counts, 1))
            if children and all(feasible(child, child_erased, rest, budget - cost, False) for child, child_erased in children):
                return True
        return False

    at_bound = feasible(initial_counts, 0, initial_remaining, bound, True)
    below = feasible(initial_counts, 0, initial_remaining, bound - 1, True)
    return at_bound, below, states


def main():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    expected_discovery = tuple(
        costs for costs in product(range(1, 5), repeat=3)
        if gcd(gcd(costs[0], costs[1]), costs[2]) == 1
    )
    rows = []
    for case in source["cases"]:
        costs = tuple(case["level_costs"])
        pair = tuple(tuple(word) for word in case["pair"])
        candidate = max(*(dot(face, costs) for face in FACES), dot(NEW_FACE, costs))
        exact = case["exact_cost"]
        feasible, below, states = exact_boundary((*BASE, *pair), costs, exact)
        rows.append({
            "role": case["role"],
            "level_costs": list(costs),
            "pair": [list(word) for word in pair],
            "candidate_cost": candidate,
            "recorded_exact_cost": exact,
            "feasible_at_recorded_exact": feasible,
            "infeasible_below_recorded_exact": not below,
            "candidate_matched": exact == candidate,
            "states": states,
        })
    expected_order = [
        (role, costs, pair)
        for role, triples in (("discovery", expected_discovery), ("prospective_holdout", HOLDOUTS))
        for costs in triples
        for pair in PAIRS
    ]
    actual_order = [
        (row["role"], tuple(row["level_costs"]), tuple(tuple(word) for word in row["pair"]))
        for row in source["cases"]
    ]
    mismatches = [row for row in rows if not row["candidate_matched"]]
    summary = {
        "zero_theorica_imports": True,
        "full_matrix_cases": len(expected_order),
        "audited_cases": len(rows),
        "fail_fast_prefix_exact": actual_order == expected_order[: len(actual_order)],
        "feasible_at_recorded_exact": sum(row["feasible_at_recorded_exact"] for row in rows),
        "infeasible_below_recorded_exact": sum(row["infeasible_below_recorded_exact"] for row in rows),
        "candidate_mismatches": len(mismatches),
        "mismatch_is_final_case": bool(mismatches) and mismatches == rows[-1:],
        "independent_states": sum(row["states"] for row in rows),
    }
    summary["passed"] = (
        summary["fail_fast_prefix_exact"]
        and summary["feasible_at_recorded_exact"] == summary["audited_cases"]
        and summary["infeasible_below_recorded_exact"] == summary["audited_cases"]
        and summary["candidate_mismatches"] == 1
        and summary["mismatch_is_final_case"]
        and source["summary"]["candidate_falsified"]
    )
    result = {"schema": "theorica.ternary-minimal-obstruction-cost-cone-audit/1", "cases": rows, "summary": summary}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
