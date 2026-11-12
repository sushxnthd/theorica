#!/usr/bin/env python3
"""Test whether an explicit outside-prefix token restores symbol covariance."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HELPER_SPEC = importlib.util.spec_from_file_location(
    "helper_sentinel", Path("scripts/verify_qary_ternary_obstruction_transfer_boundary.py")
)
assert HELPER_SPEC and HELPER_SPEC.loader
H = importlib.util.module_from_spec(HELPER_SPEC)
HELPER_SPEC.loader.exec_module(H)

SOLVER_SPEC = importlib.util.spec_from_file_location(
    "solver_sentinel", Path("scripts/verify_qary_ternary_clean_separator.py")
)
assert SOLVER_SPEC and SOLVER_SPEC.loader
S = importlib.util.module_from_spec(SOLVER_SPEC)
SOLVER_SPEC.loader.exec_module(S)

OUT = Path("results/qary_ternary_explicit_outside_sentinel/results.json")
FROZEN = {
    18: {"value": 37, "optimal_groups": [0], "children": [33, 33, 33]},
    19: {"value": 38, "optimal_groups": [0], "children": [34, 34, 33]},
}


def sentinel_rows(words):
    """Prefix rows with -1 outside a prefix and 0/1/2 as observed symbols."""
    rows = []
    for level in range(3):
        for prefix in range(3**level):
            prefix_digits = tuple(
                (prefix // (3 ** (level - i - 1))) % 3 for i in range(level)
            )
            rows.append(
                tuple(word[level] if word[:level] == prefix_digits else -1 for word in words)
            )
    return tuple(rows)


def swap_zero_one(word):
    return tuple(1 if x == 0 else 0 if x == 1 else x for x in word)


def endpoint(words, c):
    exact = S.exact_value(words, (4, 11, c), S.witness_state())
    group0 = next(row for row in exact["root_actions"] if row["query_group"] == 0)
    return {
        "leaf_cost": c,
        "exact_value": exact["exact_lower_bound"],
        "optimal_groups": sorted(
            row["query_group"] for row in exact["root_actions"] if row["optimal"]
        ),
        "group0_children": group0["child_values"],
        "exact": exact,
    }


def main():
    source = (*H.BASE, *H.PAIRS[0])
    target = tuple(swap_zero_one(word) for word in source)
    # Both graph construction and exact enumeration consume the changed encoding.
    H.rows = sentinel_rows
    S.H.rows = sentinel_rows
    mapping, certificate = H.isomorphism(H.graph(source), H.graph(target))
    compact = None if mapping is None else H.compact(mapping, source, target)
    source_endpoints = [endpoint(source, c) for c in sorted(FROZEN)]
    target_endpoints = [endpoint(target, c) for c in sorted(FROZEN)]
    pair_equal = all(
        (s["exact_value"], s["optimal_groups"], s["group0_children"])
        == (t["exact_value"], t["optimal_groups"], t["group0_children"])
        for s, t in zip(source_endpoints, target_endpoints)
    )
    search_equal = all(
        s["exact"]["states_solved"] == t["exact"]["states_solved"]
        and s["exact"]["actions_evaluated"] == t["exact"]["actions_evaluated"]
        and s["exact"]["compatibility_states"]
        == t["exact"]["compatibility_states"]
        for s, t in zip(source_endpoints, target_endpoints)
    )
    frozen_endpoint_predictions = all(
        {
            "value": row["exact_value"],
            "optimal_groups": row["optimal_groups"],
            "children": row["group0_children"],
        }
        == FROZEN[row["leaf_cost"]]
        for row in source_endpoints + target_endpoints
    )
    report = {
        "schema": "theorica.ternary-explicit-outside-sentinel/1",
        "outside_response": -1,
        "alphabet_action": "swap_0_1_fix_outside_minus_1",
        "source_words": [list(w) for w in source],
        "target_words": [list(w) for w in target],
        "isomorphism": compact,
        "isomorphism_certificate": certificate,
        "source_endpoints": source_endpoints,
        "target_endpoints": target_endpoints,
        "summary": {
            "structural_covariance_restored": compact is not None,
            "endpoint_and_root_signatures_equal": pair_equal,
            "search_counts_equal": search_equal,
            "frozen_numeric_predictions_passed": frozen_endpoint_predictions,
            "overall_covariance_claim_passed": compact is not None and pair_equal and search_equal,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if report["summary"]["overall_covariance_claim_passed"] else 1)


if __name__ == "__main__":
    main()
