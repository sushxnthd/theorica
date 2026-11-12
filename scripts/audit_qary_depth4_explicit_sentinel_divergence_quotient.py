#!/usr/bin/env python3
"""Zero-production-import audit of the depth-four divergence quotient."""
from __future__ import annotations

import hashlib
import json
from itertools import combinations, product
from math import comb
from pathlib import Path

SOURCE = Path("results/qary_depth4_explicit_sentinel_divergence_quotient/results.json")
OUT = Path("results/qary_depth4_explicit_sentinel_divergence_quotient/audit.json")
Q = 3
D = 4
BASE = tuple(product(range(2), repeat=D))


def rows(words):
    return tuple(
        tuple(word[level] if word[:level] == prefix else -1 for word in words)
        for level in range(D)
        for prefix in product(range(Q), repeat=level)
    )


def divergence_class(pair):
    return next(
        index
        for index, (left, right) in enumerate(zip(pair[0][1:], pair[1][1:]))
        if left != right
    )


def validate_map(source, target, mapping):
    source_rows, target_rows = rows(source), rows(target)
    completions, queries = mapping["completions"], mapping["queries"]
    if sorted(completions) != list(range(18)) or sorted(queries) != list(range(40)):
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


def count_identity(q, depth):
    counts = [
        comb(q, 2) * q**r * q ** (2 * (depth - r - 2))
        for r in range(depth - 1)
    ]
    return sum(counts) == comb(q ** (depth - 1), 2)


def main():
    raw = SOURCE.read_bytes()
    result = json.loads(raw)
    fibre = tuple((2, *suffix) for suffix in product(range(Q), repeat=D - 1))
    expected_pairs = set(combinations(fibre, 2))
    observed_pairs = {
        tuple(tuple(word) for word in row["pair"]) for row in result["catalogue"]
    }
    representatives = {
        0: ((2, 0, 0, 0), (2, 1, 0, 0)),
        1: ((2, 0, 0, 0), (2, 0, 1, 0)),
        2: ((2, 0, 0, 0), (2, 0, 0, 1)),
    }
    map_checks = []
    counts = {0: 0, 1: 0, 2: 0}
    for row in result["catalogue"]:
        pair = tuple(tuple(word) for word in row["pair"])
        r = divergence_class(pair)
        assert row["class"] == row["computed_common_suffix_prefix"] == r
        counts[r] += 1
        map_checks.append(
            validate_map((*BASE, *representatives[r]), (*BASE, *pair), row["isomorphism"])
        )

    holdout_checks = []
    for key, row in result["holdouts"].items():
        r = int(key)
        pair = tuple(tuple(word) for word in row["pair"])
        holdout_checks.append(
            divergence_class(pair) == r
            and validate_map(
                (*BASE, *representatives[r]), (*BASE, *pair), row["isomorphism"]
            )
        )
    formula_grid = {
        f"q={q},d={depth}": count_identity(q, depth)
        for q in range(3, 10)
        for depth in range(2, 8)
    }
    cross_separated = all(
        row["isomorphic"] is False
        and (
            row["certificate"].get("WL_multiplicity_separation") is True
            or row["certificate"].get("exhaustive_nonisomorphism") is True
        )
        for row in result["cross_representative_nonisomorphism"].values()
    )
    passed = (
        observed_pairs == expected_pairs
        and counts == {0: 243, 1: 81, 2: 27}
        and all(map_checks)
        and all(holdout_checks)
        and all(formula_grid.values())
        and cross_separated
        and result["representative_solve_reduction"] == 117
        and result["summary"]["overall_passed"] is True
    )
    report = {
        "schema": "theorica.depth4-explicit-sentinel-divergence-quotient-audit/1",
        "production_imports": 0,
        "results_sha256": hashlib.sha256(raw).hexdigest(),
        "families_reconstructed": len(observed_pairs),
        "class_sizes": {str(key): value for key, value in counts.items()},
        "edge_maps_independently_checked": sum(map_checks) + sum(holdout_checks),
        "cross_class_nonisomorphisms_checked": len(
            result["cross_representative_nonisomorphism"]
        ),
        "closed_form_identity_grid_checks": sum(formula_grid.values()),
        "representative_solve_reduction": result["representative_solve_reduction"],
        "passed": passed,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
