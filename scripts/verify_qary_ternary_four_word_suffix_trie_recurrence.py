#!/usr/bin/env python3
"""Exhaustive q=3,d=4,k=4 suffix-trie recurrence experiment."""
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

OUT = Path("results/qary_ternary_four_word_suffix_trie_recurrence/results.json")
Q, D, K = 3, 4, 4
SUFFIXES = tuple(product(range(Q), repeat=D - 1))
FROZEN_COUNTS = {
    "0": 81,
    "1": 2916,
    "2": 243,
    "3": 243,
    "4": 1458,
    "5": 2187,
    "6": 54,
    "7": 162,
    "8": 2187,
    "9": 6561,
    "10": 1458,
}
FROZEN_HOLDOUTS = (
    ((2, 1, 1), (2, 1, 2), (2, 2, 1), (2, 2, 2)),
    ((1, 2, 2), (2, 1, 2), (2, 2, 1), (2, 2, 2)),
    ((2, 0, 2), (2, 1, 2), (2, 2, 1), (2, 2, 2)),
    ((1, 2, 1), (1, 2, 2), (2, 2, 1), (2, 2, 2)),
    ((1, 2, 1), (1, 2, 2), (2, 1, 2), (2, 2, 2)),
    ((0, 2, 2), (1, 2, 2), (2, 2, 1), (2, 2, 2)),
    ((2, 1, 2), (2, 2, 0), (2, 2, 1), (2, 2, 2)),
    ((1, 2, 2), (2, 2, 0), (2, 2, 1), (2, 2, 2)),
    ((1, 1, 2), (1, 2, 2), (2, 1, 2), (2, 2, 2)),
    ((0, 2, 2), (1, 2, 2), (2, 1, 2), (2, 2, 2)),
    ((1, 2, 2), (2, 0, 2), (2, 1, 2), (2, 2, 2)),
)


@cache
def leaf_count(shape):
    return 1 if not shape else sum(leaf_count(child) for child in shape)


@cache
def recurrence_shapes(height, leaves, q):
    if height == 0:
        return ((),) if leaves == 1 else ()
    pool = sorted(
        {
            shape
            for size in range(1, leaves + 1)
            for shape in recurrence_shapes(height - 1, size, q)
        },
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
    denominator = 1
    for child in set(shape):
        denominator *= factorial(shape.count(child))
    falling = factorial(q) // factorial(q - len(shape))
    children = 1
    for child in shape:
        children *= recurrence_embedding_count(child, q)
    return falling // denominator * children


def family_id(family):
    return "|".join("".join(map(str, word)) for word in family)


def main():
    predicted_shapes = recurrence_shapes(D - 1, K, Q)
    predicted_counts = {
        str(index): recurrence_embedding_count(shape, Q)
        for index, shape in enumerate(predicted_shapes)
    }
    if predicted_counts != FROZEN_COUNTS:
        raise RuntimeError("recurrence differs from frozen class counts")

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
        cross[f"{left}:{right}"] = {
            "isomorphic": mapping is not None,
            "certificate": certificate,
        }

    class_sizes = {str(i): len(grouped[shape]) for i, shape in enumerate(shapes)}
    recursive_sizes = {str(i): S.embedding_count(shape, Q) for i, shape in enumerate(shapes)}
    q4_shapes = recurrence_shapes(D - 1, K, 4)
    q4_counts = [recurrence_embedding_count(shape, 4) for shape in q4_shapes]
    q4_identity = sum(q4_counts) == comb(4 ** (D - 1), K) == 635376
    passed = (
        class_sizes == recursive_sizes == predicted_counts == FROZEN_COUNTS
        and sum(class_sizes.values()) == comb(len(SUFFIXES), K) == transport_checks == 17550
        and len(holdout_rows) == 11
        and len(cross) == 55
        and all(not row["isomorphic"] for row in cross.values())
        and len(q4_shapes) == 14
        and q4_identity
    )
    report = {
        "schema": "theorica.ternary-four-word-suffix-trie-recurrence/1",
        "alphabet_size": Q,
        "depth": D,
        "added_words": K,
        "family_count": transport_checks,
        "class_count": len(shapes),
        "class_sizes": class_sizes,
        "frozen_counts": FROZEN_COUNTS,
        "recurrence_counts": predicted_counts,
        "embedding_formula_counts": recursive_sizes,
        "q4_symbolic_identity": {
            "class_count": len(q4_shapes),
            "class_sizes": q4_counts,
            "sum": sum(q4_counts),
            "target": comb(4 ** (D - 1), K),
            "passed": q4_identity,
        },
        "representative_solve_reduction": {"from": 17550, "to": 11, "ratio": "17550/11"},
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
            "all_17550_families_classified": transport_checks == 17550,
            "all_17550_transports_edge_checked": transport_checks == 17550,
            "all_11_frozen_holdouts_passed": len(holdout_rows) == 11,
            "all_55_cross_classes_separated": len(cross) == 55
            and all(not row["isomorphic"] for row in cross.values()),
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
