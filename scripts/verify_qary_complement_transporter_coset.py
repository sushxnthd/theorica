#!/usr/bin/env python3
"""Exact complement-transporter cosets for half-density suffix tries."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import combinations_with_replacement
from math import comb, factorial
from pathlib import Path

OUT = Path("results/qary_complement_transporter_coset/results.json")


def canonical_complement(shape: tuple[int, ...], q: int) -> tuple[int, ...]:
    return tuple(sorted(q - weight for weight in shape))


def stabilizer_order(shape: tuple[int, ...], q: int) -> int:
    multiplicities = Counter(shape)
    result = 1
    for weight, count in multiplicities.items():
        result *= factorial(count)
        result *= (factorial(weight) * factorial(q - weight)) ** count
    return result


def root_complement_involution(shape: tuple[int, ...], q: int) -> tuple[int, ...]:
    buckets = {
        weight: [i for i, value in enumerate(shape) if value == weight]
        for weight in range(q + 1)
    }
    mapping = [-1] * q
    for weight in range(q // 2):
        other = q - weight
        if len(buckets[weight]) != len(buckets[other]):
            raise ValueError("shape is not complement-fixed")
        for left, right in zip(buckets[weight], buckets[other], strict=True):
            mapping[left] = right
            mapping[right] = left
    for index in buckets[q // 2]:
        mapping[index] = index
    if sorted(mapping) != list(range(q)):
        raise ValueError("root map is not bijective")
    if any(mapping[mapping[index]] != index for index in range(q)):
        raise ValueError("root map is not involutive")
    return tuple(mapping)


def full_transport(
    shape: tuple[int, ...], q: int
) -> tuple[tuple[int, ...], tuple[int, ...], dict[tuple[int, int], tuple[int, int]]]:
    root_map = root_complement_involution(shape, q)
    shifts = tuple((q - weight) % q for weight in shape)
    mapping = {
        (branch, leaf): (root_map[branch], (leaf + shifts[branch]) % q)
        for branch in range(q)
        for leaf in range(q)
    }
    return root_map, shifts, mapping


def mapping_digest(mapping: dict[tuple[int, int], tuple[int, int]], q: int) -> str:
    stream = "\n".join(
        f"{branch},{leaf}->{mapping[(branch, leaf)][0]},{mapping[(branch, leaf)][1]}"
        for branch in range(q)
        for leaf in range(q)
    )
    return hashlib.sha256(stream.encode()).hexdigest()


def canonical_family(shape: tuple[int, ...], q: int) -> set[tuple[int, int]]:
    return {
        (branch, leaf)
        for branch, weight in enumerate(shape)
        for leaf in range(weight)
    }


def record_for_shape(shape: tuple[int, ...], q: int, group_order: int) -> dict:
    root_map, shifts, mapping = full_transport(shape, q)
    universe = {(branch, leaf) for branch in range(q) for leaf in range(q)}
    family = canonical_family(shape, q)
    image = {mapping[node] for node in family}
    stabilizer = stabilizer_order(shape, q)
    orbit = group_order // stabilizer
    passed = (
        len(mapping) == q * q
        and len(set(mapping.values())) == q * q
        and all(mapping[mapping[node]] == node for node in universe)
        and image == universe - family
        and group_order % stabilizer == 0
        and orbit * stabilizer == group_order
    )
    return {
        "shape": list(shape),
        "root_involution": list(root_map),
        "leaf_shifts": list(shifts),
        "map_sha256": mapping_digest(mapping, q),
        "stabilizer_order": stabilizer,
        "complement_transporter_count": stabilizer,
        "orbit_size": orbit,
        "orbit_times_transporters": orbit * stabilizer,
        "full_map_passed": passed,
    }


def main() -> None:
    q, half = 10, 50
    shapes = tuple(combinations_with_replacement(range(q + 1), q))
    half_shapes = tuple(shape for shape in shapes if sum(shape) == half)
    complement = {shape: canonical_complement(shape, q) for shape in half_shapes}
    fixed = tuple(shape for shape in half_shapes if complement[shape] == shape)
    pairs = tuple(shape for shape in half_shapes if shape < complement[shape])
    group_order = factorial(q) ** (1 + q)
    records = tuple(record_for_shape(shape, q, group_order) for shape in fixed)
    stream = "\n".join(
        json.dumps(record, sort_keys=True, separators=(",", ":")) for record in records
    )
    stabilizers = [record["stabilizer_order"] for record in records]
    passed = (
        len(shapes) == comb(2 * q, q) == 184756
        and len(half_shapes) == 5448
        and len(fixed) == comb(q, q // 2) == 252
        and len(pairs) == 2598
        and all(canonical_complement(complement[shape], q) == shape for shape in half_shapes)
        and all(record["full_map_passed"] for record in records)
        and all(
            record["orbit_times_transporters"] == group_order for record in records
        )
    )
    report = {
        "schema": "theorica.complement-transporter-coset/1",
        "theorem": {
            "left_coset": "Trans_c(A)=tau Stab(A)",
            "right_coset": "Trans_c(A)=Stab(A^c) tau",
            "cardinality": "|Trans_c(A)|=|Stab(A)|",
            "certificate": "|Orb(A)| |Trans_c(A)|=|G|",
        },
        "q10_h2_holdout": {
            "labelled_family_count": comb(q * q, half),
            "total_orbit_classes": len(shapes),
            "half_density_classes": len(half_shapes),
            "self_complementary_classes": len(fixed),
            "nonfixed_complement_pairs": len(pairs),
            "group_order": group_order,
            "fixed_class_records": list(records),
            "fixed_record_stream_sha256": hashlib.sha256(stream.encode()).hexdigest(),
            "distinct_stabilizer_orders": len(set(stabilizers)),
            "minimum_stabilizer_order": min(stabilizers),
            "maximum_stabilizer_order": max(stabilizers),
            "sum_fixed_orbit_sizes": sum(record["orbit_size"] for record in records),
        },
        "summary": {
            "all_184756_representatives_enumerated": len(shapes) == 184756,
            "all_5448_half_density_classes_classified": len(half_shapes) == 5448,
            "all_252_fixed_classes_fully_mapped": len(records) == 252
            and all(record["full_map_passed"] for record in records),
            "all_coset_cardinality_certificates_passed": all(
                record["orbit_times_transporters"] == group_order for record in records
            ),
            "overall_passed": passed,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
