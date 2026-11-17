#!/usr/bin/env python3
"""Prospective exact test of P2 invariance under an explicit outside token."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "sentinel_p2", Path("scripts/verify_qary_ternary_explicit_outside_sentinel.py")
)
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)

OUT = Path("results/qary_ternary_explicit_sentinel_p2_invariance/results.json")
PREDICTIONS = {
    7: {"value": 33, "source_group": 3, "target_group": 1, "children": [22, 22, 22]},
    8: {"value": 34, "source_group": 3, "target_group": 1, "children": [23, 22, 22]},
}


def swap_zero_two(word):
    return tuple(2 if x == 0 else 0 if x == 2 else x for x in word)


def endpoint(words, c, predicted_group):
    exact = V.S.exact_value(words, (4, 11, c), V.S.witness_state())
    action = next(
        row for row in exact["root_actions"] if row["query_group"] == predicted_group
    )
    return {
        "leaf_cost": c,
        "exact_value": exact["exact_lower_bound"],
        "optimal_groups": sorted(
            row["query_group"] for row in exact["root_actions"] if row["optimal"]
        ),
        "predicted_group_children": action["child_values"],
        "exact": exact,
    }


def main():
    source = (*V.H.BASE, *V.H.PAIRS[2])
    target = tuple(swap_zero_two(word) for word in source)
    V.H.rows = V.sentinel_rows
    V.S.H.rows = V.sentinel_rows

    mapping, certificate = V.H.isomorphism(V.H.graph(source), V.H.graph(target))
    compact = None if mapping is None else V.H.compact(mapping, source, target)

    source_endpoints = [
        endpoint(source, c, PREDICTIONS[c]["source_group"]) for c in sorted(PREDICTIONS)
    ]
    target_endpoints = [
        endpoint(target, c, PREDICTIONS[c]["target_group"]) for c in sorted(PREDICTIONS)
    ]

    checks = {}
    for source_row, target_row in zip(source_endpoints, target_endpoints):
        c = source_row["leaf_cost"]
        predicted = PREDICTIONS[c]
        checks[str(c)] = {
            "source_signature": (
                source_row["exact_value"] == predicted["value"]
                and source_row["optimal_groups"] == [predicted["source_group"]]
                and source_row["predicted_group_children"] == predicted["children"]
            ),
            "target_signature": (
                target_row["exact_value"] == predicted["value"]
                and target_row["optimal_groups"] == [predicted["target_group"]]
                and target_row["predicted_group_children"] == predicted["children"]
            ),
            "bounds_equal": all(
                row["exact"]["exact_lower_bound"]
                == row["exact"]["constructive_upper_bound"]
                for row in (source_row, target_row)
            ),
            "search_counts_equal": all(
                source_row["exact"][key] == target_row["exact"][key]
                for key in ("states_solved", "actions_evaluated", "compatibility_states")
            ),
        }

    predictions_passed = (
        compact is not None
        and compact["queries"][3] == 1
        and all(all(row.values()) for row in checks.values())
    )
    query_map = compact["queries"] if compact is not None else []
    actual_covariance_passed = (
        compact is not None
        and all(
            source_row["exact_value"] == target_row["exact_value"]
            and sorted(query_map[group] for group in source_row["optimal_groups"])
            == target_row["optimal_groups"]
            and all(
                source_row["exact"][key] == target_row["exact"][key]
                for key in ("states_solved", "actions_evaluated", "compatibility_states")
            )
            for source_row, target_row in zip(source_endpoints, target_endpoints)
        )
    )
    exploratory_sweep = []
    for c in range(1, 7):
        row = endpoint(source, c, 3)
        exploratory_sweep.append(
            {
                "leaf_cost": c,
                "exact_value": row["exact_value"],
                "optimal_groups": row["optimal_groups"],
                "optimal_actions": [
                    action
                    for action in row["exact"]["root_actions"]
                    if action["optimal"]
                ],
            }
        )
    exploratory_sweep.extend(
        {
            "leaf_cost": row["leaf_cost"],
            "exact_value": row["exact_value"],
            "optimal_groups": row["optimal_groups"],
            "optimal_actions": [
                action for action in row["exact"]["root_actions"] if action["optimal"]
            ],
        }
        for row in source_endpoints
    )
    report = {
        "schema": "theorica.ternary-explicit-sentinel-p2-invariance/1",
        "outside_response": -1,
        "alphabet_action": "swap_0_2_fix_outside_minus_1",
        "fixed_root_middle_costs": [4, 11],
        "candidate_root_branch": "max(33,26+c)",
        "certified_anchor": {"leaf_cost": 1, "exact_value": 33},
        "source_words": [list(word) for word in source],
        "target_words": [list(word) for word in target],
        "isomorphism": compact,
        "isomorphism_certificate": certificate,
        "source_endpoints": source_endpoints,
        "target_endpoints": target_endpoints,
        "post_falsification_exploratory_sweep": exploratory_sweep,
        "checks": checks,
        "summary": {
            "frozen_invariance_prediction_passed": predictions_passed,
            "classification": "boundary_invariance_falsified",
            "response_refinement_changes_p2_values": True,
            "observed_values_c7_c8": [
                source_endpoints[0]["exact_value"],
                source_endpoints[1]["exact_value"],
            ],
            "exploratory_integer_law_c1_c8": "V=4+3c",
            "unseen_family_covariance_passed": actual_covariance_passed,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if not predictions_passed and actual_covariance_passed else 1)


if __name__ == "__main__":
    main()
