#!/usr/bin/env python3
"""Exhaustive q=3,d=4,k=5 test of the suffix-trie generating law."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import defaultdict
from functools import cache
from itertools import combinations, combinations_with_replacement, product
from math import comb, factorial
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "suffix_trie",
    Path("scripts/verify_qary_depth4_explicit_sentinel_suffix_trie_quotient.py"),
)
assert SPEC and SPEC.loader
S = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(S)

OUT = Path("results/qary_ternary_five_word_suffix_trie_generating_law/results.json")
Q, D, K = 3, 4, 5
SUFFIXES = tuple(product(range(Q), repeat=D - 1))
FROZEN_GENERATING_COUNTS = (
    1, 3, 6, 11, 18, 31, 44, 63, 84, 104, 122, 138, 144, 144,
    138, 122, 104, 84, 63, 44, 31, 18, 11, 6, 3, 1, 1,
)
FROZEN_COUNTS = (
    1458, 243, 54, 2916, 8748, 13122, 4374, 2187, 162,
    13122, 1458, 972, 81, 486, 729, 19683, 4374, 6561,
)
FROZEN_Q4_COUNTS = (
    41472, 6912, 1152, 82944, 331776, 884736, 221184, 6144,
    110592, 4608, 884736, 73728, 393216, 36864, 3072, 18432,
    49152, 192, 768, 1769472, 294912, 1572864, 786432, 49152,
)
FROZEN_HOLDOUTS = (
    ((1, 2, 2), (2, 1, 1), (2, 1, 2), (2, 2, 1), (2, 2, 2)),
    ((2, 0, 2), (2, 1, 1), (2, 1, 2), (2, 2, 1), (2, 2, 2)),
    ((2, 1, 1), (2, 1, 2), (2, 2, 0), (2, 2, 1), (2, 2, 2)),
    ((1, 2, 1), (1, 2, 2), (2, 1, 2), (2, 2, 1), (2, 2, 2)),
    ((1, 1, 2), (1, 2, 2), (2, 1, 2), (2, 2, 1), (2, 2, 2)),
    ((0, 2, 2), (1, 2, 2), (2, 1, 2), (2, 2, 1), (2, 2, 2)),
    ((1, 2, 2), (2, 0, 2), (2, 1, 2), (2, 2, 1), (2, 2, 2)),
    ((0, 2, 2), (1, 2, 1), (1, 2, 2), (2, 2, 1), (2, 2, 2)),
    ((1, 2, 1), (1, 2, 2), (2, 2, 0), (2, 2, 1), (2, 2, 2)),
    ((0, 2, 2), (1, 2, 1), (1, 2, 2), (2, 1, 2), (2, 2, 2)),
    ((1, 2, 1), (1, 2, 2), (2, 0, 2), (2, 1, 2), (2, 2, 2)),
    ((1, 2, 2), (2, 1, 2), (2, 2, 0), (2, 2, 1), (2, 2, 2)),
    ((2, 0, 2), (2, 1, 2), (2, 2, 0), (2, 2, 1), (2, 2, 2)),
    ((1, 2, 0), (1, 2, 1), (1, 2, 2), (2, 1, 2), (2, 2, 2)),
    ((0, 2, 2), (1, 2, 2), (2, 2, 0), (2, 2, 1), (2, 2, 2)),
    ((0, 2, 2), (1, 1, 2), (1, 2, 2), (2, 1, 2), (2, 2, 2)),
    ((1, 1, 2), (1, 2, 2), (2, 0, 2), (2, 1, 2), (2, 2, 2)),
    ((0, 2, 2), (1, 2, 2), (2, 0, 2), (2, 1, 2), (2, 2, 2)),
)


def poly_add(*polys):
    size = max(map(len, polys))
    return tuple(sum(poly[i] if i < len(poly) else 0 for poly in polys) for i in range(size))


def poly_mul(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return tuple(result)


def poly_scale(poly, factor):
    return tuple(factor * value for value in poly)


def poly_substitute(poly, power):
    result = [0] * ((len(poly) - 1) * power + 1)
    for degree, value in enumerate(poly):
        result[degree * power] = value
    return tuple(result)


def ternary_cycle_step(a):
    a2 = poly_substitute(a, 2)
    a3 = poly_substitute(a, 3)
    numerator = poly_add(
        poly_scale(a, 6),
        poly_scale(poly_mul(a, a), 3),
        poly_scale(a2, 3),
        poly_mul(poly_mul(a, a), a),
        poly_scale(poly_mul(a, a2), 3),
        poly_scale(a3, 2),
    )
    if any(value % 6 for value in numerator):
        raise RuntimeError("cycle-index recurrence lost integrality")
    return tuple(value // 6 for value in numerator)


def ternary_generating_polynomial(height):
    poly = (0, 1)
    for _ in range(height):
        poly = ternary_cycle_step(poly)
    return poly


@cache
def leaf_count(shape):
    return 1 if not shape else sum(leaf_count(child) for child in shape)


@cache
def recurrence_shapes(height, leaves, q):
    if height == 0:
        return ((),) if leaves == 1 else ()
    pool = sorted(
        {shape for size in range(1, leaves + 1) for shape in recurrence_shapes(height - 1, size, q)},
        key=repr,
    )
    output = set()
    for arity in range(1, min(q, leaves) + 1):
        for children in combinations_with_replacement(pool, arity):
            if sum(leaf_count(child) for child in children) == leaves:
                output.add(tuple(sorted(children, key=repr)))
    return tuple(sorted(output, key=repr))


@cache
def recurrence_embedding_count(shape, q):
    if not shape:
        return 1
    symmetry = 1
    for child in set(shape):
        symmetry *= factorial(shape.count(child))
    falling = factorial(q) // factorial(q - len(shape))
    return falling // symmetry * product_int(recurrence_embedding_count(child, q) for child in shape)


def product_int(values):
    result = 1
    for value in values:
        result *= value
    return result


def family_id(family):
    return "|".join("".join(map(str, word)) for word in family)


def main():
    generating = ternary_generating_polynomial(D - 1)
    generating_counts = tuple(generating[1:])
    if generating_counts != FROZEN_GENERATING_COUNTS:
        raise RuntimeError("generating polynomial differs from frozen protocol")

    predicted_shapes = recurrence_shapes(D - 1, K, Q)
    predicted_counts = tuple(recurrence_embedding_count(shape, Q) for shape in predicted_shapes)
    if predicted_counts != FROZEN_COUNTS:
        raise RuntimeError("k=5 recurrence differs from frozen class counts")
    low_degree_shape_counts = tuple(len(recurrence_shapes(D - 1, k, Q)) for k in range(1, K + 1))
    if low_degree_shape_counts != generating_counts[:K]:
        raise RuntimeError("shape enumerator disagrees with generating polynomial")

    grouped = defaultdict(list)
    for family in combinations(SUFFIXES, K):
        grouped[S.trie_shape(family)].append(family)
    shapes = tuple(sorted(grouped, key=repr))
    if shapes != predicted_shapes:
        raise RuntimeError("enumerated shapes differ from recurrence")
    representatives = {index: grouped[shape][0] for index, shape in enumerate(shapes)}
    holdouts = {index: grouped[shape][-1] for index, shape in enumerate(shapes)}
    if tuple(holdouts.values()) != FROZEN_HOLDOUTS:
        raise RuntimeError("holdouts differ from frozen protocol")
    shape_class = {shape: index for index, shape in enumerate(shapes)}

    aggregate = hashlib.sha256()
    class_aggregates = {index: hashlib.sha256() for index in representatives}
    transport_checks = 0
    for family in combinations(SUFFIXES, K):
        class_id = shape_class[S.trie_shape(family)]
        _, digest = S.constructive_transport(representatives[class_id], family)
        row = f"{family_id(family)}|{class_id}|{digest}\n".encode()
        aggregate.update(row)
        class_aggregates[class_id].update(row)
        transport_checks += 1

    holdout_rows = {}
    for class_id, family in holdouts.items():
        compact, digest = S.constructive_transport(representatives[class_id], family)
        holdout_rows[str(class_id)] = {
            "suffixes": [list(word) for word in family],
            "transport": compact,
            "transport_sha256": digest,
        }

    graphs = {
        class_id: S.graph((*S.BASE, *((2, *suffix) for suffix in family)))
        for class_id, family in representatives.items()
    }
    cross = {}
    for left, right in combinations(representatives, 2):
        mapping, certificate = S.H.isomorphism(graphs[left], graphs[right])
        cross[f"{left}:{right}"] = {"isomorphic": mapping is not None, "certificate": certificate}

    class_sizes = tuple(len(grouped[shape]) for shape in shapes)
    recursive_sizes = tuple(S.embedding_count(shape, Q) for shape in shapes)
    q4_shapes = recurrence_shapes(D - 1, K, 4)
    q4_counts = tuple(recurrence_embedding_count(shape, 4) for shape in q4_shapes)
    q4_identity = q4_counts == FROZEN_Q4_COUNTS and sum(q4_counts) == comb(64, K)
    passed = (
        class_sizes == recursive_sizes == predicted_counts == FROZEN_COUNTS
        and sum(class_sizes) == comb(len(SUFFIXES), K) == transport_checks == 80730
        and len(holdout_rows) == 18
        and len(cross) == 153
        and all(not row["isomorphic"] for row in cross.values())
        and len(q4_shapes) == 24
        and q4_identity
    )
    report = {
        "schema": "theorica.ternary-five-word-suffix-trie-generating-law/1",
        "alphabet_size": Q,
        "depth": D,
        "added_words": K,
        "generating_polynomial_coefficients": list(generating_counts),
        "family_count": transport_checks,
        "class_count": len(shapes),
        "class_sizes": list(class_sizes),
        "frozen_counts": list(FROZEN_COUNTS),
        "recurrence_counts": list(predicted_counts),
        "embedding_formula_counts": list(recursive_sizes),
        "q4_symbolic_identity": {
            "class_count": len(q4_shapes),
            "class_sizes": list(q4_counts),
            "sum": sum(q4_counts),
            "target": comb(64, K),
            "passed": q4_identity,
        },
        "representative_solve_reduction": {"from": 80730, "to": 18, "ratio": "80730/18"},
        "classes": {
            str(i): {
                "shape": S.shape_json(shape),
                "representative_suffixes": [list(word) for word in representatives[i]],
                "holdout_suffixes": [list(word) for word in holdouts[i]],
                "transport_stream_sha256": class_aggregates[i].hexdigest(),
            }
            for i, shape in enumerate(shapes)
        },
        "all_family_transport_stream_sha256": aggregate.hexdigest(),
        "holdouts": holdout_rows,
        "cross_representative_nonisomorphism": cross,
        "summary": {
            "all_80730_families_classified": transport_checks == 80730,
            "all_80730_transports_edge_checked": transport_checks == 80730,
            "all_18_frozen_holdouts_passed": len(holdout_rows) == 18,
            "all_153_cross_classes_separated": len(cross) == 153 and all(not row["isomorphic"] for row in cross.values()),
            "all_27_generating_coefficients_exact": generating_counts == FROZEN_GENERATING_COUNTS,
            "recurrence_exact": class_sizes == predicted_counts,
            "q4_symbolic_identity_passed": q4_identity,
            "overall_passed": passed,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
