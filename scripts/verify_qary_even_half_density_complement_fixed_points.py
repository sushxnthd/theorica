#!/usr/bin/env python3
"""Exact complement fixed-point law for even half-density suffix tries."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import combinations_with_replacement
from math import comb, factorial
from pathlib import Path

OUT = Path("results/qary_even_half_density_complement_fixed_points/results.json")


def multiset_count(n: int, r: int) -> int:
    if r == 0:
        return 1
    if n == 0:
        return 0
    return comb(n + r - 1, r)


def total_shape_count(q: int, height: int) -> int:
    total = 2
    for _ in range(height):
        total = comb(total + q - 1, q)
    return total


def fixed_shape_count(q: int, height: int) -> int:
    total, fixed = 2, 0
    for _ in range(height):
        pairs = (total - fixed) // 2
        fixed = sum(
            multiset_count(pairs, j) * multiset_count(fixed, q - 2 * j)
            for j in range(q // 2 + 1)
        )
        total = comb(total + q - 1, q)
    return fixed


def canonical_complement(shape: tuple[int, ...], q: int) -> tuple[int, ...]:
    return tuple(sorted(q - child for child in shape))


def child_bijection(shape: tuple[int, ...], q: int) -> tuple[int, ...]:
    """Return an involutive index map sending each child to its complement."""
    buckets = {
        value: [i for i, child in enumerate(shape) if child == value]
        for value in range(q + 1)
    }
    mapping = [-1] * q
    for value in range((q // 2) + 1):
        other = q - value
        left, right = buckets[value], buckets[other]
        if value == other:
            for index in left:
                mapping[index] = index
        else:
            if len(left) != len(right):
                raise ValueError("shape is not complement-fixed")
            for source, target in zip(left, right, strict=True):
                mapping[source] = target
                mapping[target] = source
    if sorted(mapping) != list(range(q)):
        raise ValueError("child map is not bijective")
    if any(shape[mapping[i]] != q - shape[i] for i in range(q)):
        raise ValueError("child map does not realize complement")
    if any(mapping[mapping[i]] != i for i in range(q)):
        raise ValueError("child map is not involutive")
    return tuple(mapping)


def partitions(n: int, minimum: int = 1):
    if n == 0:
        yield ()
        return
    for first in range(minimum, n + 1):
        for rest in partitions(n - first, first):
            yield (first, *rest)


def poly_mul(left: list[int], right: list[int], limit: int) -> list[int]:
    out = [0] * (limit + 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right[: limit + 1 - i]):
            out[i + j] += a * b
    return out


def poly_pow(poly: list[int], exponent: int, limit: int) -> list[int]:
    out = [1] + [0] * limit
    for _ in range(exponent):
        out = poly_mul(out, poly, limit)
    return out


def poly_substitute(poly: list[int], stride: int, limit: int) -> list[int]:
    out = [0] * (limit + 1)
    for degree, coefficient in enumerate(poly):
        if degree * stride <= limit:
            out[degree * stride] = coefficient
    return out


def cycle_index_step(poly: list[int], q: int, limit: int) -> list[int]:
    numerator = [0] * (limit + 1)
    for partition in partitions(q):
        multiplicities = Counter(partition)
        z = 1
        term = [1] + [0] * limit
        for cycle, count in multiplicities.items():
            z *= cycle**count * factorial(count)
            term = poly_mul(
                term,
                poly_pow(poly_substitute(poly, cycle, limit), count, limit),
                limit,
            )
        multiplier = factorial(q) // z
        for degree, coefficient in enumerate(term):
            numerator[degree] += multiplier * coefficient
    denominator = factorial(q)
    if any(value % denominator for value in numerator):
        raise ArithmeticError("cycle-index coefficients are not integral")
    return [value // denominator for value in numerator]


def orbit_polynomial(q: int, height: int) -> list[int]:
    poly = [1, 1]
    for level in range(1, height + 1):
        poly = cycle_index_step(poly, q, q**level)
    return poly


def shape_id(shape: tuple[int, ...]) -> str:
    return ",".join(map(str, shape))


def main() -> None:
    q, height, half = 6, 2, 18
    shapes = tuple(combinations_with_replacement(range(q + 1), q))
    by_size = Counter(sum(shape) for shape in shapes)
    half_shapes = tuple(shape for shape in shapes if sum(shape) == half)
    complement = {shape: canonical_complement(shape, q) for shape in half_shapes}
    fixed = tuple(shape for shape in half_shapes if complement[shape] == shape)
    pair_representatives = tuple(
        shape for shape in half_shapes if shape < complement[shape]
    )
    maps = {shape_id(shape): list(child_bijection(shape, q)) for shape in fixed}
    polynomial = orbit_polynomial(q, height)

    q4_poly = orbit_polynomial(4, 3)
    q4_fixed = fixed_shape_count(4, 3)
    passed = (
        len(shapes) == total_shape_count(q, height) == 924
        and [by_size[k] for k in range(15, 22)] == [51, 55, 55, 58, 55, 55, 51]
        and len(half_shapes) == polynomial[half] == 58
        and len(fixed) == fixed_shape_count(q, height) == 20
        and len(pair_representatives) == 19
        and all(canonical_complement(complement[shape], q) == shape for shape in half_shapes)
        and len(maps) == 20
        and sum(polynomial) == 924
        and polynomial == polynomial[::-1]
        and q4_poly[32] == 60802
        and q4_fixed == 1326
        and (q4_poly[32] - q4_fixed) // 2 == 29738
    )
    report = {
        "schema": "theorica.even-half-density-complement-fixed-points/1",
        "theorem": {
            "total_recurrence": "T(q,h)=binom(T(q,h-1)+q-1,q)",
            "fixed_recurrence": "[t^q](1-t)^(-F)(1-t^2)^(-(T-F)/2)",
        },
        "q6_h2_holdout": {
            "labelled_family_count": comb(36, 18),
            "total_orbit_classes": len(shapes),
            "orbit_polynomial": polynomial,
            "coefficient_window_15_21": [by_size[k] for k in range(15, 22)],
            "half_density_classes": len(half_shapes),
            "self_complementary_classes": len(fixed),
            "nonfixed_complement_pairs": len(pair_representatives),
            "fixed_shapes": [list(shape) for shape in fixed],
            "fixed_child_bijections": maps,
            "pair_representatives": [
                {"left": list(shape), "right": list(complement[shape])}
                for shape in pair_representatives
            ],
        },
        "q4_h3_theorem_check": {
            "total_orbit_classes": total_shape_count(4, 3),
            "half_density_classes": q4_poly[32],
            "self_complementary_classes": q4_fixed,
            "nonfixed_complement_pairs": (q4_poly[32] - q4_fixed) // 2,
        },
        "summary": {
            "all_924_orbit_representatives_enumerated": len(shapes) == 924,
            "all_58_half_density_classes_classified": len(half_shapes) == 58,
            "all_20_fixed_classes_constructively_mapped": len(maps) == 20,
            "all_19_nonfixed_pairs_identified": len(pair_representatives) == 19,
            "overall_passed": passed,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
