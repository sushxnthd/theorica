#!/usr/bin/env python3
"""Test the preregistered cost cone of the three minimal ternary obstructions."""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations, product
from math import gcd
from pathlib import Path

from theorica.agents.corruption_resilient_features import (
    plan_adaptive_decision_queries_with_weighted_faults,
    qary_prefix_query_costs,
    qary_prefix_query_library,
)

OUT = Path("results/qary_ternary_minimal_obstruction_cost_cone/results.json")
BASE = tuple(product(range(2), repeat=3))
FIBER = ((2, 0, 0), (2, 1, 0), (2, 2, 0))
PAIRS = tuple(combinations(FIBER, 2))
FACES = (
    (1, 5, 1),
    (2, 3, 4),
    (2, 4, 3),
    (3, 3, 3),
    (3, 4, 1),
    (4, 2, 1),
)
NEW_FACE = (2, 5, 1)
HOLDOUTS = (
    (1, 5, 1), (2, 5, 2), (1, 4, 2), (2, 7, 1),
    (3, 8, 2), (2, 9, 3), (3, 10, 3), (4, 11, 2),
    (5, 13, 4), (7, 19, 5), (11, 29, 7), (13, 34, 9),
)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def predicted(costs):
    binary = max(dot(face, costs) for face in FACES)
    extra = dot(NEW_FACE, costs)
    return max(binary, extra), binary, extra


def games(count):
    return tuple(
        (
            (1 - (p := Fraction(index + 1, count + 1)), p - 1),
            (-p, p),
        )
        for index in range(count)
    )


def exact_case(costs, pair, role):
    words = (*BASE, *pair)
    bound, binary, extra = predicted(costs)
    rows = qary_prefix_query_library(3, 3, copies=4)
    word_indices = tuple(sum(symbol * 3 ** (2 - i) for i, symbol in enumerate(word)) for word in words)
    restricted_rows = tuple(tuple(row[index] for index in word_indices) for row in rows)
    plan = plan_adaptive_decision_queries_with_weighted_faults(
        games(len(words)),
        restricted_rows,
        query_costs=qary_prefix_query_costs(3, 3, copies=4, level_costs=costs),
        corruption_budget=1,
        erasure_budget=1,
        allowed_initial_query_indices=range(4, 16),
        known_feasible_cost_upper_bound=bound,
    )
    return {
        "role": role,
        "level_costs": list(costs),
        "pair": [list(word) for word in pair],
        "binary_six_face_cost": binary,
        "new_face_cost": extra,
        "predicted_cost": bound,
        "exact_cost": plan.worst_case_cost,
        "new_face_strictly_active": extra > binary,
        "new_face_tied": extra == binary,
        "states_solved": plan.states_solved,
        "compatibility_states_solved": plan.compatibility_states_solved,
        "matched": plan.certificate_valid and plan.worst_case_cost == bound,
    }


def main():
    discovery = tuple(
        costs
        for costs in product(range(1, 5), repeat=3)
        if gcd(gcd(costs[0], costs[1]), costs[2]) == 1
    )
    cases = []
    first_mismatch = None
    for role, triples in (("discovery", discovery), ("prospective_holdout", HOLDOUTS)):
        if first_mismatch is not None:
            break
        for costs in triples:
            for pair in PAIRS:
                try:
                    row = exact_case(costs, pair, role)
                except ValueError as exc:
                    row = {
                        "role": role,
                        "level_costs": list(costs),
                        "pair": [list(word) for word in pair],
                        "predicted_cost": predicted(costs)[0],
                        "matched": False,
                        "error": str(exc),
                    }
                cases.append(row)
                if not row["matched"]:
                    first_mismatch = row
                    break
            if first_mismatch is not None:
                break

    summary = {
        "discovery_triples": len(discovery),
        "prospective_holdout_triples": len(HOLDOUTS),
        "obstruction_pairs": len(PAIRS),
        "cases_run": len(cases),
        "cases_matched": sum(row["matched"] for row in cases),
        "new_face_strict_cases": sum(row.get("new_face_strictly_active", False) for row in cases),
        "new_face_tie_cases": sum(row.get("new_face_tied", False) for row in cases),
        "binary_face_cases": sum(
            not row.get("new_face_strictly_active", False)
            and not row.get("new_face_tied", False)
            for row in cases
        ),
        "total_states_solved": sum(row.get("states_solved", 0) for row in cases),
        "first_mismatch": first_mismatch,
    }
    expected = (len(discovery) + len(HOLDOUTS)) * len(PAIRS)
    summary["candidate_supported"] = first_mismatch is None and len(cases) == expected
    summary["candidate_falsified"] = first_mismatch is not None
    summary["experiment_completed"] = (
        summary["candidate_supported"] or summary["candidate_falsified"]
    )
    summary["passed"] = summary["experiment_completed"]
    result = {
        "schema": "theorica.ternary-minimal-obstruction-cost-cone/1",
        "candidate_faces": [list(face) for face in (*FACES, NEW_FACE)],
        "discovery_costs": [list(costs) for costs in discovery],
        "prospective_holdouts": [list(costs) for costs in HOLDOUTS],
        "cases": cases,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
