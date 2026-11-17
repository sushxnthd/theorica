#!/usr/bin/env python3
"""Prospective exact test of the explicit-sentinel P2 policy reversal."""
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

OUT = Path("results/qary_ternary_explicit_sentinel_p2_policy_reversal/results.json")
PREDICTIONS = {
    11: {
        "value": 37,
        "source_optimal": [0, 3, 11, 12],
        "target_optimal": [0, 1, 4, 5],
        "group0": [22, 22, 33],
        "group3": [26, 22, 22],
        "group11": [26, 22],
    },
    12: {
        "value": 39,
        "source_optimal": [3],
        "target_optimal": [1],
        "group0": [23, 23, 36],
        "group3": [28, 24, 24],
        "group11": [28, 24],
    },
}


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
    target = tuple(P.swap_zero_two(word) for word in source)
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
            "source_value_and_optima": (
                left["exact_value"] == expected["value"]
                and left["optimal_groups"] == expected["source_optimal"]
            ),
            "source_group0_children": left["root_actions"][0]["child_values"] == expected["group0"],
            "source_group3_children": left["root_actions"][3]["child_values"] == expected["group3"],
            "source_group11_children": left["root_actions"][11]["child_values"] == expected["group11"],
            "target_value_and_optima": (
                right["exact_value"] == expected["value"]
                and right["optimal_groups"] == expected["target_optimal"]
            ),
            "transported_group0_signature": sorted(right["root_actions"][0]["child_values"])
            == sorted(expected["group0"]),
            "transported_group3_signature": sorted(right["root_actions"][1]["child_values"])
            == sorted(expected["group3"]),
            "transported_group11_signature": sorted(right["root_actions"][5]["child_values"])
            == sorted(expected["group11"]),
            "bounds_equal": all(
                row["exact"]["exact_lower_bound"] == row["exact"]["constructive_upper_bound"]
                for row in (left, right)
            ),
            "search_counts_equal": all(
                left["exact"][key] == right["exact"][key]
                for key in ("states_solved", "actions_evaluated", "compatibility_states")
            ),
        }

    frozen_predictions_passed = (
        compact is not None
        and compact["queries"][3] == 1
        and compact["queries"][11] == 5
        and compact["queries"][12] == 4
        and all(all(row.values()) for row in checks.values())
    )
    collision_prediction_passed = all(checks["11"].values())
    reversal_prediction_passed = all(checks["12"].values())
    actual_covariance_passed = (
        compact is not None
        and all(
            left["exact_value"] == right["exact_value"]
            and sorted(compact["queries"][group] for group in left["optimal_groups"])
            == right["optimal_groups"]
            and all(
                left["exact"][key] == right["exact"][key]
                for key in ("states_solved", "actions_evaluated", "compatibility_states")
            )
            for left, right in zip(source_rows, target_rows)
        )
    )
    diagnostic_rows = [endpoint(source, c) for c in (9, 10)]
    report = {
        "schema": "theorica.ternary-explicit-sentinel-p2-policy-reversal/1",
        "outside_response": -1,
        "fixed_root_middle_costs": [4, 11],
        "candidate_branches": {"root_leaf": "4+3c", "clean_middle": "15+2c"},
        "source_words": [list(word) for word in source],
        "target_words": [list(word) for word in target],
        "isomorphism": compact,
        "isomorphism_certificate": certificate,
        "source_endpoints": source_rows,
        "target_endpoints": target_rows,
        "post_falsification_diagnostic_endpoints": diagnostic_rows,
        "checks": checks,
        "summary": {
            "all_frozen_predictions_passed": frozen_predictions_passed,
            "collision_prediction_passed": collision_prediction_passed,
            "reversal_prediction_passed": reversal_prediction_passed,
            "classification": "collision_confirmed_reversal_falsified",
            "collision_cost": 11 if collision_prediction_passed else None,
            "observed_c12_value": source_rows[1]["exact_value"],
            "observed_c12_optimal_groups": source_rows[1]["optimal_groups"],
            "aliased_handoff_direction": "group3_to_group0",
            "sentinel_handoff_direction": "four_way_tie_to_group0",
            "exploratory_law_c9_c10": "V=4+3c",
            "sentinel_advantage_closes_at_c11": collision_prediction_passed,
            "unseen_family_transport_passed": actual_covariance_passed,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(
        0
        if collision_prediction_passed
        and not reversal_prediction_passed
        and actual_covariance_passed
        else 1
    )


if __name__ == "__main__":
    main()
