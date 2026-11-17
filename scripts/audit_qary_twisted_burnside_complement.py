#!/usr/bin/env python3
"""Independent wreath-recurrence audit of the twisted Burnside holdout."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path

SOURCE = Path("results/qary_twisted_burnside_complement/results.json")
OUT = Path("results/qary_twisted_burnside_complement/audit.json")


def wreath_cycle_distribution(height: int) -> Counter[tuple[int, ...]]:
    """Derive cycle types without constructing any leaf permutation."""
    distribution: Counter[tuple[int, ...]] = Counter({(1,): 1})
    group_order = 1
    for _ in range(height):
        previous = distribution
        distribution = Counter()
        # No root swap: two independent actions on the two halves.
        for left_type, left_count in previous.items():
            for right_type, right_count in previous.items():
                distribution[tuple(sorted(left_type + right_type))] += (
                    left_count * right_count
                )
        # Root swap: cycles of the cross-half composition have doubled length.
        for child_type, child_count in previous.items():
            doubled = tuple(sorted(2 * length for length in child_type))
            distribution[doubled] += group_order * child_count
        group_order = 2 * group_order * group_order
    return distribution


def even_cycle_weight(cycles: tuple[int, ...]) -> int:
    return 0 if any(length & 1 for length in cycles) else 2 ** len(cycles)


def independent_shape_counts(height: int) -> tuple[int, int, int]:
    """Count canonical shapes using integer IDs and a complement table."""
    weights = {0: 0, 1: 1}
    complements = {0: 1, 1: 0}
    shapes = (0, 1)
    for _ in range(height):
        pairs = tuple(combinations_with_replacement(shapes, 2))
        ids = {pair: index for index, pair in enumerate(pairs)}
        next_weights = {
            ids[pair]: weights[pair[0]] + weights[pair[1]] for pair in pairs
        }
        next_complements = {
            ids[pair]: ids[
                tuple(sorted((complements[pair[0]], complements[pair[1]])))
            ]
            for pair in pairs
        }
        shapes = tuple(range(len(pairs)))
        weights = next_weights
        complements = next_complements
    half = 1 << (height - 1)
    half_shapes = tuple(shape for shape in shapes if weights[shape] == half)
    fixed = sum(complements[shape] == shape for shape in half_shapes)
    return len(shapes), len(half_shapes), fixed


def encoded_distribution(
    distribution: Counter[tuple[int, ...]],
) -> list[dict[str, int | list[int]]]:
    return [
        {
            "cycle_type": list(cycles),
            "automorphisms": count,
            "alternating_weight_each": even_cycle_weight(cycles),
            "alternating_weight_total": count * even_cycle_weight(cycles),
        }
        for cycles, count in sorted(distribution.items())
    ]


def main() -> None:
    raw = SOURCE.read_bytes()
    source = json.loads(raw)
    reported = source["q2_h4_holdout"]
    distribution = wreath_cycle_distribution(4)
    rows = encoded_distribution(distribution)
    rows_stream = "\n".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows
    )
    weight_sum = sum(count * even_cycle_weight(cycles) for cycles, count in distribution.items())
    eligible = sum(
        count for cycles, count in distribution.items() if even_cycle_weight(cycles)
    )
    shape_count, half_shape_count, fixed_shape_count = independent_shape_counts(4)
    passed = (
        sum(distribution.values()) == 32768
        and rows == reported["cycle_type_distribution"]
        and hashlib.sha256(rows_stream.encode()).hexdigest()
        == reported["cycle_type_distribution_sha256"]
        and eligible == reported["eligible_even_cycle_automorphisms"]
        and weight_sum == reported["twisted_weight_sum"] == 753664
        and weight_sum // 32768 == fixed_shape_count == 23
        and shape_count == reported["suffix_shape_classes"] == 231
        and half_shape_count == reported["half_density_shape_classes"]
        and source["summary"]["overall_passed"] is True
    )
    report = {
        "schema": "theorica.twisted-burnside-complement-audit/1",
        "production_imports": 0,
        "independent_method": "binary wreath-product cycle recurrence plus integer-ID shape recurrence",
        "results_sha256": hashlib.sha256(raw).hexdigest(),
        "group_order_reconstructed": sum(distribution.values()),
        "distinct_cycle_types_reconstructed": len(distribution),
        "eligible_even_cycle_automorphisms_reconstructed": eligible,
        "twisted_weight_sum_reconstructed": weight_sum,
        "twisted_orbit_count_reconstructed": weight_sum // 32768,
        "suffix_shape_classes_reconstructed": shape_count,
        "half_density_shape_classes_reconstructed": half_shape_count,
        "fixed_shape_classes_reconstructed": fixed_shape_count,
        "cycle_type_distribution_sha256": hashlib.sha256(
            rows_stream.encode()
        ).hexdigest(),
        "passed": passed,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
