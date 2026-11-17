#!/usr/bin/env python3
"""Independent zero-THEORICA-import audit of the P0/P2 boundary profiles."""

from __future__ import annotations

import hashlib
import json
from functools import cache
from itertools import product
from pathlib import Path

SOURCE = Path("results/qary_ternary_nonisomorphic_scalar_boundary/results.json")
OUT = SOURCE.with_name("audit.json")
COSTS = (2, 9, 3)


def rows(words):
    return tuple(
        tuple(word[level] if word[:level] == prefix else 0 for word in words)
        for level in range(3)
        for prefix in product(range(3), repeat=level)
    )


def query_level(query):
    return 0 if query < 1 else 1 if query < 4 else 2


def exact_boundary(words, bound, initial_logical_query=None):
    groups = tuple(
        (row, COSTS[query_level(query)]) for query, row in enumerate(rows(words))
    )
    alphabets = tuple(tuple(sorted(set(row))) for row, _ in groups)
    allowed_initial = (
        frozenset(range(1, 4))
        if initial_logical_query is None
        else frozenset((initial_logical_query,))
    )
    states = 0

    @cache
    def feasible(counts, erased, remaining, budget, initial):
        nonlocal states
        states += 1
        live = tuple(index for index, count in enumerate(counts) if count <= 1)
        if len(live) <= 1:
            return True
        for query, multiplicity in enumerate(remaining):
            row, cost = groups[query]
            if (
                multiplicity == 0
                or cost > budget
                or (initial and query not in allowed_initial)
                or len({row[index] for index in live}) < 2
            ):
                continue
            rest = tuple(
                value - (index == query) for index, value in enumerate(remaining)
            )
            children = []
            for answer in alphabets[query]:
                child = tuple(
                    min(2, count + (row[index] != answer))
                    for index, count in enumerate(counts)
                )
                if any(value <= 1 for value in child):
                    children.append((child, erased))
            if erased == 0:
                children.append((counts, 1))
            if children and all(
                feasible(child, child_erased, rest, budget - cost, False)
                for child, child_erased in children
            ):
                return True
        return False

    initial = (0,) * 10
    remaining = (4,) * 13
    at_bound = feasible(initial, 0, remaining, bound, True)
    below = feasible(initial, 0, remaining, bound - 1, True)
    return at_bound, below, states


def main():
    raw = SOURCE.read_bytes()
    source = json.loads(raw)
    checks = []
    for family in source["families"]:
        words = tuple(tuple(word) for word in family["words"])
        cases = [(None, family["unrestricted_exact_cost"])] + [
            (row["logical_middle_query"], row["exact_cost"])
            for row in family["middle_roots"]
        ]
        for initial_query, exact in cases:
            at_bound, below, states = exact_boundary(words, exact, initial_query)
            checks.append(
                {
                    "family": family["name"],
                    "initial_logical_query": initial_query,
                    "recorded_exact_cost": exact,
                    "feasible_at_exact": at_bound,
                    "infeasible_one_below": not below,
                    "states": states,
                    "passed": at_bound and not below,
                }
            )
    p0, p2 = source["families"]
    canonical_antichains_equal = p0["unrestricted_exposure_antichain"] == p2[
        "unrestricted_exposure_antichain"
    ] and [row["exposure_antichain"] for row in p0["middle_roots"]] == [
        row["exposure_antichain"] for row in p2["middle_roots"]
    ]
    summary = {
        "zero_theorica_imports": True,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "boundaries_checked": len(checks),
        "boundaries_passed": sum(row["passed"] for row in checks),
        "independent_states": sum(row["states"] for row in checks),
        "scalar_costs_equal": p0["unrestricted_exact_cost"]
        == p2["unrestricted_exact_cost"]
        == 51,
        "middle_root_profiles_equal": p0["sorted_middle_root_cost_profile"]
        == p2["sorted_middle_root_cost_profile"]
        == [51, 51, 52],
        "canonical_antichains_equal": canonical_antichains_equal,
    }
    summary["passed"] = (
        len(checks) == 8
        and all(row["passed"] for row in checks)
        and summary["scalar_costs_equal"]
        and summary["middle_root_profiles_equal"]
        and canonical_antichains_equal
        and source["summary"]["classification"] == "unresolved_finer_boundary"
        and not source["summary"]["prediction_supported"]
    )
    OUT.write_text(
        json.dumps(
            {
                "schema": "theorica.ternary-nonisomorphic-scalar-boundary-audit/1",
                "checks": checks,
                "summary": summary,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
