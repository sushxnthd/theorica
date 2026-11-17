#!/usr/bin/env python3
"""Zero-production-import audit of the complete obstruction quotient."""
from __future__ import annotations

import hashlib
import json
from itertools import combinations, product
from pathlib import Path

SOURCE = Path("results/qary_ternary_explicit_sentinel_orbit_quotient/results.json")
OUT = Path("results/qary_ternary_explicit_sentinel_orbit_quotient/audit.json")


def rows(words):
    result = []
    for level in range(3):
        for prefix in product(range(3), repeat=level):
            result.append(
                tuple(word[level] if word[:level] == prefix else -1 for word in words)
            )
    return tuple(result)


def validate_map(source, target, compact):
    source_rows = rows(source)
    target_rows = rows(target)
    completion_map = compact["completions"]
    query_map = compact["queries"]
    if sorted(completion_map) != list(range(10)) or sorted(query_map) != list(range(13)):
        return False
    for query, source_row in enumerate(source_rows):
        target_query = query_map[query]
        for answer in set(source_row):
            mapped_answer = compact["cells"][f"{query}:{answer}"]
            if any(
                (value == answer)
                != (target_rows[target_query][completion_map[index]] == mapped_answer)
                for index, value in enumerate(source_row)
            ):
                return False
    return True


def root_check(row):
    actions = {int(group): action for group, action in row["root_actions"].items()}
    minimum = min(action["action_value"] for action in actions.values())
    optima = sorted(
        group for group, action in actions.items() if action["action_value"] == minimum
    )
    return (
        minimum == row["exact_value"]
        == row["exact"]["exact_lower_bound"]
        == row["exact"]["constructive_upper_bound"]
        and optima == row["optimal_groups"]
    )


def main():
    raw = SOURCE.read_bytes()
    result = json.loads(raw)
    base = tuple(product(range(2), repeat=3))
    fibre = tuple((2, x, y) for x, y in product(range(3), repeat=2))
    expected_pairs = {
        tuple(pair) for pair in combinations(fibre, 2)
    }
    observed_pairs = {
        tuple(tuple(word) for word in row["pair"]) for row in result["catalogue"]
    }
    map_checks = []
    same = 0
    different = 0
    for row in result["catalogue"]:
        pair = tuple(tuple(word) for word in row["pair"])
        class_name = row["class"]
        representative_pair = tuple(
            tuple(word)
            for word in result["class_results"][class_name]["representative_pair"]
        )
        map_checks.append(
            validate_map(
                (*base, *representative_pair),
                (*base, *pair),
                row["isomorphism"],
            )
        )
        if pair[0][1] == pair[1][1]:
            same += 1
            assert class_name == "same_middle"
        else:
            different += 1
            assert class_name == "different_middle"

    exact_rows = []
    holdout_maps = []
    for class_result in result["class_results"].values():
        exact_rows.extend(class_result["representative_integer_sweep"])
        exact_rows.extend(class_result["holdout_endpoints"])
        representative_pair = tuple(
            tuple(word) for word in class_result["representative_pair"]
        )
        holdout_pair = tuple(tuple(word) for word in class_result["holdout_pair"])
        holdout_maps.append(
            validate_map(
                (*base, *representative_pair),
                (*base, *holdout_pair),
                class_result["holdout_isomorphism"],
            )
        )

    passed = (
        observed_pairs == expected_pairs
        and same == 9
        and different == 27
        and all(map_checks)
        and all(holdout_maps)
        and all(root_check(row) for row in exact_rows)
        and result["representative_solve_reduction"] == 18
        and result["summary"]["all_frozen_holdouts_passed"] is True
        and result["summary"]["post_holdout_chamber_laws_passed"] is True
    )
    report = {
        "schema": "theorica.ternary-explicit-sentinel-orbit-quotient-audit/1",
        "production_imports": 0,
        "results_sha256": hashlib.sha256(raw).hexdigest(),
        "families_reconstructed": len(observed_pairs),
        "same_middle_families": same,
        "different_middle_families": different,
        "edge_maps_independently_checked": sum(map_checks) + sum(holdout_maps),
        "exact_root_minima_reconstructed": len(exact_rows),
        "representative_solve_reduction": result["representative_solve_reduction"],
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
