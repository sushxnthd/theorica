#!/usr/bin/env python3
"""Prove the frozen positive-leaf-cost chamber by monotonicity sandwich."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HELPER_SPEC = importlib.util.spec_from_file_location(
    "helper", Path("scripts/verify_qary_ternary_obstruction_transfer_boundary.py")
)
assert HELPER_SPEC and HELPER_SPEC.loader
H = importlib.util.module_from_spec(HELPER_SPEC)
HELPER_SPEC.loader.exec_module(H)

SOLVER_SPEC = importlib.util.spec_from_file_location(
    "clean_solver", Path("scripts/verify_qary_ternary_clean_separator.py")
)
assert SOLVER_SPEC and SOLVER_SPEC.loader
S = importlib.util.module_from_spec(SOLVER_SPEC)
SOLVER_SPEC.loader.exec_module(S)

PARTITION_SPEC = importlib.util.spec_from_file_location(
    "no_clean_solver", Path("scripts/verify_qary_ternary_no_clean_separator.py")
)
assert PARTITION_SPEC and PARTITION_SPEC.loader
N = importlib.util.module_from_spec(PARTITION_SPEC)
PARTITION_SPEC.loader.exec_module(N)

OUT = Path("results/qary_ternary_positive_leaf_cost_chamber/results.json")
ENDPOINT_COSTS = (4, 11, 1)
FORMULAS = {"P2": 33, "P0": 37}


def family_result(name, words):
    state = S.witness_state()
    rows = H.rows(words)
    partitions = N.middle_partitions(rows, state)
    endpoint = S.exact_value(words, ENDPOINT_COSTS, state)
    restricted = S.exact_value(
        words, ENDPOINT_COSTS, state, allowed_levels=(0, 1)
    )
    formula = FORMULAS[name]
    clean = any(row["clean_separator"] for row in partitions)
    endpoint_formula_holds = (
        endpoint["exact_lower_bound"]
        == endpoint["constructive_upper_bound"]
        == formula
    )
    restricted_feasible = restricted["exact_lower_bound"] < S.INF
    supported = (
        endpoint_formula_holds
        and restricted["exact_lower_bound"]
        == restricted["constructive_upper_bound"]
        == formula
        and restricted["allowed_query_levels"] == [0, 1]
    )
    return {
        "family": name,
        "words": [list(word) for word in words],
        "clean_separator_present": clean,
        "middle_partitions": partitions,
        "formula_value": formula,
        "endpoint_c1": endpoint,
        "root_middle_only_upper_bound": restricted,
        "leaf_free_policy_exists": restricted_feasible,
        "sandwich": {
            "lower_bound_for_all_c_ge_1": endpoint["exact_lower_bound"],
            "upper_bound_for_all_c_ge_1": (
                restricted["constructive_upper_bound"]
                if restricted_feasible
                else None
            ),
            "closed": supported,
        },
        "falsification": {
            "endpoint_formula_holds": endpoint_formula_holds,
            "root_middle_only_policy_infeasible": not restricted_feasible,
            "every_winning_policy_requires_a_leaf_query": not restricted_feasible,
            "constant_unbounded_leaf_cost_chamber_impossible": (
                endpoint_formula_holds and not restricted_feasible
            ),
            "necessary_leaf_lower_bound": "V(c) >= c",
            "constant_formula_must_fail_for_c_greater_than": formula,
        },
    }


def main():
    p2 = family_result("P2", (*H.BASE, *H.PAIRS[2]))
    p0 = family_result("P0", (*H.BASE, *H.PAIRS[0]))
    gap = p0["formula_value"] - p2["formula_value"]
    supported = (
        p2["clean_separator_present"]
        and not p0["clean_separator_present"]
        and p2["sandwich"]["closed"]
        and p0["sandwich"]["closed"]
        and gap == ENDPOINT_COSTS[0]
    )
    leaf_necessity_falsifies = all(
        family["falsification"]["constant_unbounded_leaf_cost_chamber_impossible"]
        for family in (p2, p0)
    )
    report = {
        "schema": "theorica.ternary-positive-leaf-cost-chamber/1",
        "fixed_root_middle_costs": list(ENDPOINT_COSTS[:2]),
        "leaf_cost_domain": {"minimum": 1, "unbounded_above": True},
        "proof_rule": {
            "lower": "query-cost monotonicity from exact c=1 endpoint",
            "upper": "exact root-middle-only policy independent of leaf cost",
        },
        "families": [p2, p0],
        "exact_P0_minus_P2_gap_for_all_c_ge_1": gap,
        "cumulative_opened_reserved_cases": 6,
        "remaining_reserved_cases": 12,
        "summary": {
            "prediction_supported": supported,
            "classification": (
                "positive_leaf_cost_chamber_proved"
                if supported
                else (
                    "leaf_query_necessity_falsifies_unbounded_chamber"
                    if leaf_necessity_falsifies
                    else "positive_leaf_cost_chamber_falsified"
                )
            ),
            "leaf_query_necessity_falsification": leaf_necessity_falsifies,
            "passed": True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
