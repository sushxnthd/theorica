#!/usr/bin/env python3
"""Prospective exact test of explicit-sentinel P0/P1 structural transfer."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "sentinel", Path("scripts/verify_qary_ternary_explicit_outside_sentinel.py")
)
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)

OUT = Path("results/qary_ternary_explicit_sentinel_p1_transfer/results.json")
PREDICTIONS = {
    22: {"value": 37, "optimal": [0], "children": [33, 33, 33]},
    23: {"value": 38, "optimal": [0], "children": [34, 34, 33]},
}


def swap_zero_two(word):
    return tuple(2 if value == 0 else 0 if value == 2 else value for value in word)


def endpoint(words, c):
    exact = V.S.exact_value(words, (4, 11, c), V.S.witness_state())
    actions = {row["query_group"]: row for row in exact["root_actions"]}
    return {
        "leaf_cost": c,
        "exact_value": exact["exact_lower_bound"],
        "optimal_groups": sorted(
            group for group, row in actions.items() if row["optimal"]
        ),
        "root_actions": actions,
        "exact": exact,
    }


def main():
    p0 = (*V.H.BASE, *V.H.PAIRS[0])
    p1 = (*V.H.BASE, *V.H.PAIRS[1])
    target = tuple(swap_zero_two(word) for word in p1)
    V.H.rows = V.sentinel_rows
    V.S.H.rows = V.sentinel_rows

    p0_p1_map, p0_p1_certificate = V.H.isomorphism(
        V.H.graph(p0), V.H.graph(p1)
    )
    p1_target_map, p1_target_certificate = V.H.isomorphism(
        V.H.graph(p1), V.H.graph(target)
    )
    p0_p1 = (
        None if p0_p1_map is None else V.H.compact(p0_p1_map, p0, p1)
    )
    p1_target = (
        None
        if p1_target_map is None
        else V.H.compact(p1_target_map, p1, target)
    )

    source_rows = [endpoint(p1, c) for c in sorted(PREDICTIONS)]
    target_rows = [endpoint(target, c) for c in sorted(PREDICTIONS)]
    checks = {}
    for source, transported in zip(source_rows, target_rows):
        c = source["leaf_cost"]
        expected = PREDICTIONS[c]
        transported_root = p1_target["queries"][0] if p1_target else None
        checks[str(c)] = {
            "source_value": source["exact_value"] == expected["value"],
            "source_unique_root": source["optimal_groups"] == expected["optimal"],
            "source_ordered_children": source["root_actions"][0]["child_values"]
            == expected["children"],
            "source_bounds_equal": source["exact"]["exact_lower_bound"]
            == source["exact"]["constructive_upper_bound"],
            "target_value": transported["exact_value"] == expected["value"],
            "target_unique_transported_root": transported["optimal_groups"]
            == [transported_root],
            "target_child_multiset": sorted(
                transported["root_actions"][transported_root]["child_values"]
            )
            == sorted(expected["children"]),
            "target_bounds_equal": transported["exact"]["exact_lower_bound"]
            == transported["exact"]["constructive_upper_bound"],
            "search_counts_equal": all(
                source["exact"][key] == transported["exact"][key]
                for key in (
                    "states_solved",
                    "actions_evaluated",
                    "compatibility_states",
                )
            ),
        }

    structural_pass = (
        p0_p1 is not None
        and p0_p1_certificate["mapping_edge_checked"]
        and p0_p1["queries"][0] == 0
        and p0_p1["queries"][11] == 12
        and p0_p1["queries"][12] == 11
        and p1_target is not None
        and p1_target_certificate["mapping_edge_checked"]
    )
    passed = structural_pass and all(
        all(endpoint_checks.values()) for endpoint_checks in checks.values()
    )
    report = {
        "schema": "theorica.ternary-explicit-sentinel-p1-transfer/1",
        "outside_response": -1,
        "fixed_root_middle_costs": [4, 11],
        "p0_words": [list(word) for word in p0],
        "p1_words": [list(word) for word in p1],
        "unseen_target_words": [list(word) for word in target],
        "p0_p1_isomorphism": p0_p1,
        "p0_p1_certificate": p0_p1_certificate,
        "p1_target_isomorphism": p1_target,
        "p1_target_certificate": p1_target_certificate,
        "source_endpoints": source_rows,
        "target_endpoints": target_rows,
        "checks": checks,
        "summary": {
            "all_frozen_predictions_passed": passed,
            "structural_transfer_passed": structural_pass,
            "p1_bounded_integer_law": {
                "1<=c<=22": "V=37",
                "c=23": "V=38",
            }
            if passed
            else None,
            "unseen_composed_transport_passed": passed,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
