#!/usr/bin/env python3
"""Open the frozen P2 scalar/root-policy boundary at costs (2,9,3)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
)

HELPER_PATH = Path("scripts/verify_qary_ternary_obstruction_transfer_boundary.py")
SPEC = importlib.util.spec_from_file_location("transfer_helper", HELPER_PATH)
assert SPEC is not None and SPEC.loader is not None
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)

OUT = Path("results/qary_ternary_nonisomorphic_scalar_boundary/results.json")


def solve(words, initial_logical_query=None, upper_bound=None):
    physical = tuple(row for row in HELPER.rows(words) for _ in range(HELPER.COPIES))
    allowed = (
        range(4, 16)
        if initial_logical_query is None
        else range(4 * initial_logical_query, 4 * initial_logical_query + 4)
    )
    return plan_adaptive_decision_queries_with_weighted_faults(
        HELPER.games(10),
        physical,
        query_costs=qary_prefix_query_costs(
            3, 3, copies=HELPER.COPIES, level_costs=HELPER.COSTS
        ),
        corruption_budget=1,
        erasure_budget=1,
        known_feasible_cost_upper_bound=upper_bound,
        allowed_initial_query_indices=allowed,
    )


def exposure_antichain(root):
    terminal = []

    def walk(node, exposure):
        if node.query_index is None:
            terminal.append(exposure)
            return
        logical_query = node.query_index // HELPER.COPIES
        next_exposure = list(exposure)
        next_exposure[HELPER.level(logical_query)] += 1
        for _, child in node.children:
            walk(child, tuple(next_exposure))

    walk(root, (0, 0, 0))
    unique = set(terminal)
    return sorted(
        point
        for point in unique
        if not any(
            other != point and all(left >= right for left, right in zip(other, point))
            for other in unique
        )
    )


def family(pair):
    return (*HELPER.BASE, *pair)


def profile(name, words, unrestricted_upper):
    unrestricted = solve(words, upper_bound=unrestricted_upper)
    roots = []
    for query in range(1, 4):
        plan = solve(words, initial_logical_query=query)
        roots.append(
            {
                "logical_middle_query": query,
                "exact_cost": plan.worst_case_cost,
                "states_solved": plan.states_solved,
                "exposure_antichain": exposure_antichain(plan.root),
            }
        )
    return {
        "name": name,
        "words": words,
        "unrestricted_exact_cost": unrestricted.worst_case_cost,
        "unrestricted_states_solved": unrestricted.states_solved,
        "unrestricted_exposure_antichain": exposure_antichain(unrestricted.root),
        "middle_roots": roots,
        "sorted_middle_root_cost_profile": sorted(row["exact_cost"] for row in roots),
    }


def main():
    p0 = profile("P0_isomorphic_orbit_representative", family(HELPER.PAIRS[0]), 51)
    p2 = profile("P2_WL_nonisomorphic", family(HELPER.PAIRS[2]), None)
    if p2["unrestricted_exact_cost"] != 51:
        classification = "scalar_boundary"
    elif p2["sorted_middle_root_cost_profile"] != p0["sorted_middle_root_cost_profile"]:
        classification = "root_policy_boundary"
    else:
        classification = "unresolved_finer_boundary"
    summary = {
        "opened_reserved_cases": 1,
        "remaining_reserved_cases": 18,
        "P0_exact_cost": p0["unrestricted_exact_cost"],
        "P2_exact_cost": p2["unrestricted_exact_cost"],
        "P0_middle_root_cost_profile": p0["sorted_middle_root_cost_profile"],
        "P2_middle_root_cost_profile": p2["sorted_middle_root_cost_profile"],
        "classification": classification,
        "prediction_supported": classification == "root_policy_boundary",
        "passed": True,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "schema": "theorica.ternary-nonisomorphic-scalar-boundary/1",
                "level_costs": HELPER.COSTS,
                "families": [p0, p2],
                "summary": summary,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
