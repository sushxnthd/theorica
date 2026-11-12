#!/usr/bin/env python3
"""Prospective exact test of the explicit-sentinel P2 second breakpoint."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "sentinel_p2", Path("scripts/verify_qary_ternary_explicit_sentinel_p2_invariance.py")
)
assert SPEC and SPEC.loader
P = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P)

OUT = Path("results/qary_ternary_explicit_sentinel_p2_second_breakpoint/results.json")
PREDICTIONS = {
    22: {"value": 37, "optimal": [0], "group0": [33, 33, 33]},
    23: {"value": 38, "optimal": [0], "group0": [34, 34, 33]},
}


def swap_zero_one(word):
    return tuple(1 if value == 0 else 0 if value == 1 else value for value in word)


def endpoint(words, c):
    exact = P.V.S.exact_value(words, (4, 11, c), P.V.S.witness_state())
    actions = {row["query_group"]: row for row in exact["root_actions"]}
    return {
        "leaf_cost": c,
        "exact_value": exact["exact_lower_bound"],
        "optimal_groups": sorted(group for group, row in actions.items() if row["optimal"]),
        "root_actions": actions,
        "exact": exact,
    }


def main():
    source = (*P.V.H.BASE, *P.V.H.PAIRS[2])
    target = tuple(swap_zero_one(word) for word in source)
    P.V.H.rows = P.V.sentinel_rows
    P.V.S.H.rows = P.V.sentinel_rows
    mapping, certificate = P.V.H.isomorphism(P.V.H.graph(source), P.V.H.graph(target))
    compact = None if mapping is None else P.V.H.compact(mapping, source, target)

    source_rows = [endpoint(source, c) for c in sorted(PREDICTIONS)]
    target_rows = [endpoint(target, c) for c in sorted(PREDICTIONS)]
    checks = {}
    for left, right in zip(source_rows, target_rows):
        c = left["leaf_cost"]
        expected = PREDICTIONS[c]
        checks[str(c)] = {
            "source_value": left["exact_value"] == expected["value"],
            "source_unique_root": left["optimal_groups"] == expected["optimal"],
            "source_root_children": left["root_actions"][0]["child_values"]
            == expected["group0"],
            "target_value": right["exact_value"] == expected["value"],
            "target_unique_root": right["optimal_groups"] == expected["optimal"],
            "transported_root_children": sorted(right["root_actions"][0]["child_values"])
            == sorted(expected["group0"]),
            "bounds_equal": all(
                row["exact"]["exact_lower_bound"]
                == row["exact"]["constructive_upper_bound"]
                for row in (left, right)
            ),
            "search_counts_equal": all(
                left["exact"][key] == right["exact"][key]
                for key in ("states_solved", "actions_evaluated", "compatibility_states")
            ),
        }

    passed = (
        compact is not None
        and compact["queries"][0] == 0
        and all(all(row.values()) for row in checks.values())
    )
    report = {
        "schema": "theorica.ternary-explicit-sentinel-p2-second-breakpoint/1",
        "outside_response": -1,
        "fixed_root_middle_costs": [4, 11],
        "candidate_root_action": "max(37,15+c)",
        "source_words": [list(word) for word in source],
        "target_words": [list(word) for word in target],
        "isomorphism": compact,
        "isomorphism_certificate": certificate,
        "source_endpoints": source_rows,
        "target_endpoints": target_rows,
        "checks": checks,
        "summary": {
            "all_frozen_predictions_passed": passed,
            "bounded_integer_law": {
                "1<=c<=10": "V=4+3c",
                "11<=c<=22": "V=37",
                "c=23": "V=38",
            },
            "first_post_collision_increase": 23 if passed else None,
            "unseen_zero_one_transport_passed": passed,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
