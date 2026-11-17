#!/usr/bin/env python3
"""Zero-production-import audit of the q=4 orbit transfer result."""
from __future__ import annotations

import hashlib
import json
from itertools import combinations, product
from pathlib import Path

SOURCE = Path("results/qary_quaternary_explicit_sentinel_orbit_transfer/results.json")
OUT = Path("results/qary_quaternary_explicit_sentinel_orbit_transfer/audit.json")
BASE = tuple(product(range(2), repeat=3))


def rows(words, q=4):
    return tuple(
        tuple(word[level] if word[:level] == prefix else -1 for word in words)
        for level in range(3)
        for prefix in product(range(q), repeat=level)
    )


def level(query, q):
    return 0 if query < 1 else 1 if query < 1 + q else 2


def partition(row):
    return tuple(sorted(tuple(i for i, value in enumerate(row) if value == answer) for answer in set(row)))


def active_signature(words, q):
    return tuple(
        sorted(
            (level(query, q), partition(row))
            for query, row in enumerate(rows(words, q))
            if len(set(row)) > 1
        )
    )


def validate_map(source, target, mapping):
    source_rows, target_rows = rows(source), rows(target)
    completions, queries = mapping["completions"], mapping["queries"]
    if sorted(completions) != list(range(10)) or sorted(queries) != list(range(21)):
        return False
    for query, source_row in enumerate(source_rows):
        target_query = queries[query]
        for answer in set(source_row):
            target_answer = mapping["cells"][f"{query}:{answer}"]
            if any(
                (value == answer)
                != (target_rows[target_query][completions[index]] == target_answer)
                for index, value in enumerate(source_row)
            ):
                return False
    return True


def root_check(endpoint):
    actions = endpoint["exact"]["root_actions"]
    minimum = min(row["action_value"] for row in actions)
    optima = sorted(row["query_group"] for row in actions if row["action_value"] == minimum)
    return (
        minimum
        == endpoint["exact_value"]
        == endpoint["exact"]["exact_lower_bound"]
        == endpoint["exact"]["constructive_upper_bound"]
        and optima == endpoint["optimal_groups"]
    )


def main():
    raw = SOURCE.read_bytes()
    result = json.loads(raw)
    fibre = tuple((2, x, y) for x, y in product(range(4), repeat=2))
    expected = set(combinations(fibre, 2))
    observed = {tuple(tuple(word) for word in row["pair"]) for row in result["catalogue"]}
    map_checks, same, different = [], 0, 0
    representatives = {
        name: tuple(tuple(word) for word in class_result["representative"])
        for name, class_result in result["class_results"].items()
    }
    for row in result["catalogue"]:
        pair = tuple(tuple(word) for word in row["pair"])
        name = row["class"]
        is_same = pair[0][1] == pair[1][1]
        same += is_same
        different += not is_same
        assert is_same == (name == "same_middle")
        map_checks.append(
            validate_map((*BASE, *representatives[name]), (*BASE, *pair), row["isomorphism"])
        )

    reduction_checks, holdout_maps, exact_checks = [], [], []
    for class_result in result["class_results"].values():
        representative = tuple(tuple(word) for word in class_result["representative"])
        holdout = tuple(tuple(word) for word in class_result["holdout"])
        reduction_checks.append(
            active_signature((*BASE, *representative), 3)
            == active_signature((*BASE, *representative), 4)
        )
        holdout_maps.append(
            validate_map(
                (*BASE, *representative),
                (*BASE, *holdout),
                class_result["holdout_transport"],
            )
        )
        for key in ("representative_endpoints", "holdout_endpoints"):
            exact_checks.extend(root_check(row) for row in class_result[key])

    passed = (
        observed == expected
        and same == 24
        and different == 96
        and all(map_checks)
        and all(reduction_checks)
        and all(holdout_maps)
        and all(exact_checks)
        and result["representative_solve_reduction"] == 60
        and result["summary"]["overall_passed"] is True
    )
    report = {
        "schema": "theorica.quaternary-explicit-sentinel-orbit-transfer-audit/1",
        "production_imports": 0,
        "results_sha256": hashlib.sha256(raw).hexdigest(),
        "families_reconstructed": len(observed),
        "same_middle_families": same,
        "different_middle_families": different,
        "edge_maps_independently_checked": sum(map_checks) + sum(holdout_maps),
        "active_row_reductions_checked": sum(reduction_checks),
        "exact_root_minima_reconstructed": sum(exact_checks),
        "representative_solve_reduction": result["representative_solve_reduction"],
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
