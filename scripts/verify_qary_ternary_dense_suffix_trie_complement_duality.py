#!/usr/bin/env python3
"""Exhaustive complement-duality test for q=3,h=3,k=22 suffix families."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import defaultdict
from itertools import combinations, product
from math import comb, factorial
from pathlib import Path

SPARSE_SPEC = importlib.util.spec_from_file_location(
    "sparse_law",
    Path("scripts/verify_qary_ternary_five_word_suffix_trie_generating_law.py"),
)
assert SPARSE_SPEC and SPARSE_SPEC.loader
K5 = importlib.util.module_from_spec(SPARSE_SPEC)
SPARSE_SPEC.loader.exec_module(K5)

OUT = Path("results/qary_ternary_dense_suffix_trie_complement_duality/results.json")
SPARSE_RESULT = Path(
    "results/qary_ternary_five_word_suffix_trie_generating_law/results.json"
)
Q, H, SPARSE_K = 3, 3, 5
UNIVERSE = tuple(product(range(Q), repeat=H))
DENSE_K = len(UNIVERSE) - SPARSE_K
PERMUTATIONS = (
    {0: 1, 1: 2, 2: 0},
    {0: 2, 1: 1, 2: 0},
    {0: 0, 1: 2, 2: 1},
)


def complement(family):
    selected = set(family)
    return tuple(word for word in UNIVERSE if word not in selected)


def transform(family):
    return tuple(
        sorted(
            tuple(PERMUTATIONS[index][symbol] for index, symbol in enumerate(word))
            for word in family
        )
    )


def family_id(family):
    return "|".join("".join(map(str, word)) for word in family)


def automorphism_group_order(q, height):
    order = 1
    for _ in range(height):
        order = factorial(q) * order**q
    return order


def main():
    sparse_result = json.loads(SPARSE_RESULT.read_text())
    sparse_classes = {
        int(key): value for key, value in sparse_result["classes"].items()
    }
    sparse_representatives = {
        class_id: tuple(tuple(word) for word in row["representative_suffixes"])
        for class_id, row in sparse_classes.items()
    }

    generating = (1, *K5.ternary_generating_polynomial(H)[1:])
    palindromic = generating == generating[::-1]

    grouped = defaultdict(list)
    sparse_shape_to_dense_shape = {}
    for sparse_family in combinations(UNIVERSE, SPARSE_K):
        dense_family = complement(sparse_family)
        dense_shape = K5.S.trie_shape(dense_family)
        sparse_shape = K5.S.trie_shape(sparse_family)
        grouped[dense_shape].append(dense_family)
        previous = sparse_shape_to_dense_shape.setdefault(sparse_shape, dense_shape)
        if previous != dense_shape:
            raise RuntimeError("complement did not induce a sparse-to-dense class map")

    dense_shapes = tuple(sorted(grouped, key=repr))
    dense_class = {shape: index for index, shape in enumerate(dense_shapes)}
    sparse_shapes = tuple(
        K5.S.trie_shape(sparse_representatives[index])
        for index in sorted(sparse_representatives)
    )
    sparse_to_dense = {
        sparse_id: dense_class[sparse_shape_to_dense_shape[sparse_shape]]
        for sparse_id, sparse_shape in enumerate(sparse_shapes)
    }
    if len(set(sparse_to_dense.values())) != len(sparse_to_dense) != 0:
        raise RuntimeError("complement class map is not bijective")

    representatives = {
        class_id: grouped[shape][0] for class_id, shape in enumerate(dense_shapes)
    }
    class_sizes = tuple(len(grouped[shape]) for shape in dense_shapes)
    sparse_sizes = tuple(sparse_result["class_sizes"])
    group_order = automorphism_group_order(Q, H)
    paired_rows = {}
    for sparse_id, dense_id in sparse_to_dense.items():
        sparse_size = sparse_sizes[sparse_id]
        dense_size = class_sizes[dense_id]
        paired_rows[str(sparse_id)] = {
            "dense_class": dense_id,
            "sparse_orbit_size": sparse_size,
            "dense_orbit_size": dense_size,
            "sparse_stabilizer_order": group_order // sparse_size,
            "dense_stabilizer_order": group_order // dense_size,
        }

    aggregate = hashlib.sha256()
    class_aggregates = {index: hashlib.sha256() for index in representatives}
    transport_checks = 0
    for sparse_family in combinations(UNIVERSE, SPARSE_K):
        dense_family = complement(sparse_family)
        class_id = dense_class[K5.S.trie_shape(dense_family)]
        _, digest = K5.S.constructive_transport(
            representatives[class_id], dense_family
        )
        row = f"{family_id(dense_family)}|{class_id}|{digest}\n".encode()
        aggregate.update(row)
        class_aggregates[class_id].update(row)
        transport_checks += 1

    holdouts = {}
    for sparse_id, sparse_family in sparse_representatives.items():
        dense_family = complement(transform(sparse_family))
        dense_id = sparse_to_dense[sparse_id]
        if K5.S.trie_shape(dense_family) != dense_shapes[dense_id]:
            raise RuntimeError("frozen dense holdout changed class")
        compact, digest = K5.S.constructive_transport(
            representatives[dense_id], dense_family
        )
        holdouts[str(sparse_id)] = {
            "dense_class": dense_id,
            "suffixes": [list(word) for word in dense_family],
            "transport": compact,
            "transport_sha256": digest,
        }

    graphs = {
        class_id: K5.S.graph(
            (*K5.S.BASE, *((2, *suffix) for suffix in family))
        )
        for class_id, family in representatives.items()
    }
    cross = {}
    for left, right in combinations(representatives, 2):
        mapping, certificate = K5.S.H.isomorphism(graphs[left], graphs[right])
        cross[f"{left}:{right}"] = {
            "isomorphic": mapping is not None,
            "certificate": certificate,
        }

    q4_sparse_shapes = K5.recurrence_shapes(H, SPARSE_K, 4)
    q4_sizes = tuple(K5.recurrence_embedding_count(shape, 4) for shape in q4_sparse_shapes)
    q4_identity = len(q4_sparse_shapes) == 24 and sum(q4_sizes) == comb(64, 5)
    paired_ok = all(
        row["sparse_orbit_size"] == row["dense_orbit_size"]
        and row["sparse_stabilizer_order"] == row["dense_stabilizer_order"]
        for row in paired_rows.values()
    )
    passed = (
        palindromic
        and len(dense_shapes) == 18
        and sorted(class_sizes) == sorted(sparse_sizes)
        and sum(class_sizes) == comb(27, 22) == transport_checks
        and len(sparse_to_dense) == len(set(sparse_to_dense.values())) == 18
        and paired_ok
        and len(holdouts) == 18
        and len(cross) == 153
        and all(not row["isomorphic"] for row in cross.values())
        and q4_identity
    )
    report = {
        "schema": "theorica.ternary-dense-suffix-trie-complement-duality/1",
        "alphabet_size": Q,
        "suffix_height": H,
        "sparse_size": SPARSE_K,
        "dense_size": DENSE_K,
        "orbit_polynomial_coefficients_including_empty": list(generating),
        "orbit_polynomial_palindromic": palindromic,
        "automorphism_group_order": group_order,
        "family_count": transport_checks,
        "class_count": len(dense_shapes),
        "class_sizes": list(class_sizes),
        "sparse_class_sizes": list(sparse_sizes),
        "sparse_to_dense_class": paired_rows,
        "classes": {
            str(index): {
                "shape": K5.S.shape_json(shape),
                "representative_suffixes": [list(word) for word in representatives[index]],
                "transport_stream_sha256": class_aggregates[index].hexdigest(),
            }
            for index, shape in enumerate(dense_shapes)
        },
        "all_family_transport_stream_sha256": aggregate.hexdigest(),
        "holdouts": holdouts,
        "cross_representative_nonisomorphism": cross,
        "q4_symbolic_complement_identity": {
            "sparse_size": 5,
            "dense_size": 59,
            "class_count_each": len(q4_sparse_shapes),
            "orbit_sizes_each": list(q4_sizes),
            "sum_each": sum(q4_sizes),
            "passed": q4_identity,
        },
        "summary": {
            "palindromic_orbit_polynomial": palindromic,
            "all_80730_dense_families_classified": transport_checks == 80730,
            "all_80730_dense_transports_edge_checked": transport_checks == 80730,
            "complement_class_map_bijective": len(set(sparse_to_dense.values())) == 18,
            "all_orbit_sizes_and_stabilizers_preserved": paired_ok,
            "all_18_frozen_dense_holdouts_passed": len(holdouts) == 18,
            "all_153_dense_cross_classes_separated": len(cross) == 153 and all(
                not row["isomorphic"] for row in cross.values()
            ),
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
