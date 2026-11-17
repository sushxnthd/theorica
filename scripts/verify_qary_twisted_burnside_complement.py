#!/usr/bin/env python3
"""Exact twisted-Burnside complement count for depth-four binary trees."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import combinations_with_replacement
from math import comb
from pathlib import Path

OUT = Path("results/qary_twisted_burnside_complement/results.json")
HEIGHT = 4
LEAVES = 1 << HEIGHT
INTERNAL_NODES = LEAVES - 1
GROUP_ORDER = 1 << INTERNAL_NODES

Shape = int | tuple["Shape", "Shape"]


def leaf_permutation(mask: int, height: int = HEIGHT) -> tuple[int, ...]:
    """Return the leaf permutation induced by heap-indexed local swaps."""
    permutation = []
    for leaf in range(1 << height):
        source_node = 1
        target = 0
        for level in range(height):
            source_bit = (leaf >> (height - level - 1)) & 1
            swap = (mask >> (source_node - 1)) & 1
            target = (target << 1) | (source_bit ^ swap)
            source_node = (source_node << 1) | source_bit
        permutation.append(target)
    if sorted(permutation) != list(range(1 << height)):
        raise AssertionError("local swaps did not induce a permutation")
    return tuple(permutation)


def cycle_type(permutation: tuple[int, ...]) -> tuple[int, ...]:
    seen: set[int] = set()
    lengths = []
    for start in range(len(permutation)):
        if start in seen:
            continue
        node = start
        length = 0
        while node not in seen:
            seen.add(node)
            length += 1
            node = permutation[node]
        lengths.append(length)
    return tuple(sorted(lengths))


def alternating_weight(cycles: tuple[int, ...]) -> int:
    """Count A with gA=A^c from the leaf-cycle type of g."""
    return 0 if any(length % 2 for length in cycles) else 1 << len(cycles)


def enumerate_group() -> tuple[Counter[tuple[int, ...]], int, int, str]:
    distribution: Counter[tuple[int, ...]] = Counter()
    eligible = 0
    weight_sum = 0
    digest = hashlib.sha256()
    for mask in range(GROUP_ORDER):
        permutation = leaf_permutation(mask)
        cycles = cycle_type(permutation)
        weight = alternating_weight(cycles)
        distribution[cycles] += 1
        eligible += weight > 0
        weight_sum += weight
        line = (
            f"{mask:05d}|{','.join(map(str, permutation))}|"
            f"{','.join(map(str, cycles))}|{weight}\n"
        )
        digest.update(line.encode())
    return distribution, eligible, weight_sum, digest.hexdigest()


def canonical_pair(left: Shape, right: Shape) -> tuple[Shape, Shape]:
    return tuple(sorted((left, right), key=repr))  # type: ignore[return-value]


def complement(shape: Shape) -> Shape:
    if isinstance(shape, int):
        return 1 - shape
    return canonical_pair(complement(shape[0]), complement(shape[1]))


def family_size(shape: Shape) -> int:
    if isinstance(shape, int):
        return shape
    return family_size(shape[0]) + family_size(shape[1])


def enumerate_shapes(height: int = HEIGHT) -> tuple[Shape, ...]:
    shapes: tuple[Shape, ...] = (0, 1)
    for _ in range(height):
        shapes = tuple(
            canonical_pair(left, right)
            for left, right in combinations_with_replacement(shapes, 2)
        )
    return shapes


def encoded_distribution(
    distribution: Counter[tuple[int, ...]],
) -> list[dict[str, int | list[int]]]:
    return [
        {
            "cycle_type": list(cycles),
            "automorphisms": count,
            "alternating_weight_each": alternating_weight(cycles),
            "alternating_weight_total": count * alternating_weight(cycles),
        }
        for cycles, count in sorted(distribution.items())
    ]


def main() -> None:
    distribution, eligible, weight_sum, stream_sha256 = enumerate_group()
    shapes = enumerate_shapes()
    half_shapes = tuple(shape for shape in shapes if family_size(shape) == LEAVES // 2)
    fixed_shapes = tuple(shape for shape in half_shapes if complement(shape) == shape)
    rows = encoded_distribution(distribution)
    rows_stream = "\n".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows
    )
    passed = (
        sum(distribution.values()) == GROUP_ORDER
        and len(shapes) == 231
        and len(fixed_shapes) == 23
        and weight_sum == 753664
        and weight_sum // GROUP_ORDER == len(fixed_shapes)
        and weight_sum % GROUP_ORDER == 0
        and sum(comb(LEAVES, size) for size in range(LEAVES + 1)) == 1 << LEAVES
    )
    report = {
        "schema": "theorica.twisted-burnside-complement/1",
        "theorem": {
            "orbit_trace": "F=|G|^-1 sum_g |Fix(Cg)|",
            "cycle_obstruction": "an odd leaf cycle implies |Fix(Cg)|=0",
            "even_cycle_count": "all cycles even implies |Fix(Cg)|=2^c(g)",
        },
        "q2_h4_holdout": {
            "height": HEIGHT,
            "leaf_count": LEAVES,
            "internal_node_count": INTERNAL_NODES,
            "group_order": GROUP_ORDER,
            "labelled_half_density_families": comb(LEAVES, LEAVES // 2),
            "suffix_shape_classes": len(shapes),
            "half_density_shape_classes": len(half_shapes),
            "complement_fixed_shape_classes": len(fixed_shapes),
            "eligible_even_cycle_automorphisms": eligible,
            "twisted_weight_sum": weight_sum,
            "twisted_orbit_count": weight_sum // GROUP_ORDER,
            "distinct_cycle_types": len(distribution),
            "cycle_type_distribution": rows,
            "cycle_type_distribution_sha256": hashlib.sha256(
                rows_stream.encode()
            ).hexdigest(),
            "explicit_group_stream_sha256": stream_sha256,
        },
        "summary": {
            "all_32768_automorphisms_enumerated": sum(distribution.values())
            == GROUP_ORDER,
            "all_induced_leaf_maps_are_permutations": True,
            "odd_cycle_types_rejected": all(
                alternating_weight(cycles) == 0
                for cycles in distribution
                if any(length % 2 for length in cycles)
            ),
            "twisted_sum_matches_frozen_prediction": weight_sum == 753664,
            "twisted_orbit_count_matches_shape_enumeration": weight_sum // GROUP_ORDER
            == len(fixed_shapes)
            == 23,
            "overall_passed": passed,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
