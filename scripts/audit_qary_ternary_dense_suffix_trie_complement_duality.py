#!/usr/bin/env python3
"""Zero-production-import audit of dense suffix-trie complement duality."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from itertools import combinations, product
from math import comb, factorial
from pathlib import Path

AUDIT_SPEC = importlib.util.spec_from_file_location(
    "independent_sparse_audit",
    Path("scripts/audit_qary_ternary_five_word_suffix_trie_generating_law.py"),
)
assert AUDIT_SPEC and AUDIT_SPEC.loader
AUDIT = importlib.util.module_from_spec(AUDIT_SPEC)
AUDIT_SPEC.loader.exec_module(AUDIT)

SOURCE = Path("results/qary_ternary_dense_suffix_trie_complement_duality/results.json")
OUT = Path("results/qary_ternary_dense_suffix_trie_complement_duality/audit.json")
Q, H, K = 3, 3, 5
UNIVERSE = tuple(product(range(Q), repeat=H))
PERMUTATIONS = (
    {0: 1, 1: 2, 2: 0},
    {0: 2, 1: 1, 2: 0},
    {0: 0, 1: 2, 2: 1},
)


def complement(family):
    chosen = set(family)
    return tuple(word for word in UNIVERSE if word not in chosen)


def transform(family):
    return tuple(
        sorted(
            tuple(PERMUTATIONS[index][symbol] for index, symbol in enumerate(word))
            for word in family
        )
    )


def family_id(family):
    return "|".join("".join(map(str, word)) for word in family)


def group_order(q, height):
    order = 1
    for _ in range(height):
        order = factorial(q) * order**q
    return order


def colored_graph(words):
    rows = AUDIT.A.rows(words)
    colors, adjacent = {}, {}
    for index in range(len(words)):
        node = f"c:{index}"
        colors[node] = "c"
        adjacent[node] = set()
    for query, row in enumerate(rows):
        query_node = f"q:{query}"
        colors[query_node] = f"q:{AUDIT.A.query_level(query)}"
        adjacent[query_node] = set()
        for answer in sorted(set(row)):
            response = f"r:{query}:{answer}"
            colors[response] = f"r:{AUDIT.A.query_level(query)}"
            adjacent[response] = {query_node}
            adjacent[query_node].add(response)
            for index, value in enumerate(row):
                if value == answer:
                    completion = f"c:{index}"
                    adjacent[response].add(completion)
                    adjacent[completion].add(response)
    return colors, adjacent


def refinement_signature(words):
    colors, adjacent = colored_graph(words)
    for _ in range(len(colors)):
        keys = {
            node: (colors[node], tuple(sorted(colors[other] for other in adjacent[node])))
            for node in colors
        }
        palette = {key: str(index) for index, key in enumerate(sorted(set(keys.values()), key=repr))}
        updated = {node: palette[key] for node, key in keys.items()}
        if updated == colors:
            break
        colors = updated
    histogram = sorted(Counter(colors.values()).items())
    return hashlib.sha256(json.dumps(histogram).encode()).hexdigest()


def main():
    raw = SOURCE.read_bytes()
    result = json.loads(raw)
    reported_classes = {int(key): value for key, value in result["classes"].items()}
    reported_representatives = {
        class_id: tuple(tuple(word) for word in row["representative_suffixes"])
        for class_id, row in reported_classes.items()
    }

    generating = (1, *AUDIT.independent_generating_coefficients(H))
    sparse_groups = defaultdict(list)
    dense_groups = defaultdict(list)
    complement_shape_map = {}
    for sparse_family in combinations(UNIVERSE, K):
        sparse_shape = AUDIT.A.trie_shape(sparse_family)
        dense_family = complement(sparse_family)
        dense_shape = AUDIT.A.trie_shape(dense_family)
        sparse_groups[sparse_shape].append(sparse_family)
        dense_groups[dense_shape].append(dense_family)
        old = complement_shape_map.setdefault(sparse_shape, dense_shape)
        assert old == dense_shape

    sparse_shapes = tuple(sorted(sparse_groups, key=repr))
    dense_shapes = tuple(sorted(dense_groups, key=repr))
    dense_class = {shape: index for index, shape in enumerate(dense_shapes)}
    mapping = {
        sparse_id: dense_class[complement_shape_map[shape]]
        for sparse_id, shape in enumerate(sparse_shapes)
    }
    sparse_representatives = {
        index: sparse_groups[shape][0] for index, shape in enumerate(sparse_shapes)
    }
    dense_representatives = {
        index: dense_groups[shape][0] for index, shape in enumerate(dense_shapes)
    }
    assert dense_representatives == reported_representatives

    counts = Counter()
    aggregate = hashlib.sha256()
    class_aggregates = {index: hashlib.sha256() for index in dense_representatives}
    transport_checks = 0
    for sparse_family in combinations(UNIVERSE, K):
        dense_family = complement(sparse_family)
        class_id = dense_class[AUDIT.A.trie_shape(dense_family)]
        _, digest = AUDIT.A.transport(dense_representatives[class_id], dense_family)
        row = f"{family_id(dense_family)}|{class_id}|{digest}\n".encode()
        aggregate.update(row)
        class_aggregates[class_id].update(row)
        counts[class_id] += 1
        transport_checks += 1

    holdout_checks = []
    for sparse_id, sparse_family in sparse_representatives.items():
        dense_id = mapping[sparse_id]
        family = complement(transform(sparse_family))
        compact, digest = AUDIT.A.transport(dense_representatives[dense_id], family)
        reported = result["holdouts"][str(sparse_id)]
        holdout_checks.append(
            dense_id == reported["dense_class"]
            and [list(word) for word in family] == reported["suffixes"]
            and compact == reported["transport"]
            and digest == reported["transport_sha256"]
        )

    dense_sizes = [counts[index] for index in range(len(dense_shapes))]
    sparse_sizes = [len(sparse_groups[shape]) for shape in sparse_shapes]
    order = group_order(Q, H)
    stabilizers_ok = all(
        sparse_sizes[sparse_id] == dense_sizes[dense_id]
        and order // sparse_sizes[sparse_id] == order // dense_sizes[dense_id]
        for sparse_id, dense_id in mapping.items()
    )
    streams_ok = aggregate.hexdigest() == result["all_family_transport_stream_sha256"]
    class_streams = sum(
        class_aggregates[index].hexdigest()
        == reported_classes[index]["transport_stream_sha256"]
        for index in dense_representatives
    )
    signatures = {
        index: refinement_signature(
            (*AUDIT.A.BASE, *((2, *suffix) for suffix in family))
        )
        for index, family in dense_representatives.items()
    }
    separated = len(set(signatures.values())) == len(signatures) == 18
    q4_shapes = AUDIT.generated_shapes(H, K, 4)
    q4_sum = sum(AUDIT.embeddings(shape, 4) for shape in q4_shapes)
    q4_ok = len(q4_shapes) == 24 and q4_sum == comb(64, 5) == comb(64, 59)
    passed = (
        generating == tuple(result["orbit_polynomial_coefficients_including_empty"])
        and generating == generating[::-1]
        and len(sparse_shapes) == len(dense_shapes) == 18
        and len(set(mapping.values())) == 18
        and sorted(sparse_sizes) == sorted(dense_sizes)
        and dense_sizes == result["class_sizes"]
        and transport_checks == comb(27, 22) == 80730
        and stabilizers_ok
        and streams_ok
        and class_streams == 18
        and len(holdout_checks) == 18
        and all(holdout_checks)
        and separated
        and q4_ok
    )
    report = {
        "schema": "theorica.ternary-dense-suffix-trie-complement-duality-audit/1",
        "production_imports": 0,
        "results_sha256": hashlib.sha256(raw).hexdigest(),
        "palindromic_coefficients_reproduced": generating == generating[::-1],
        "sparse_classes_reconstructed": len(sparse_shapes),
        "dense_classes_reconstructed": len(dense_shapes),
        "complement_class_bijection_reconstructed": len(set(mapping.values())) == 18,
        "families_reconstructed": transport_checks,
        "transport_digests_reproduced": transport_checks,
        "aggregate_transport_stream_reproduced": streams_ok,
        "class_transport_streams_reproduced": class_streams,
        "holdout_maps_reproduced": sum(holdout_checks),
        "orbit_sizes_and_stabilizers_reproduced": stabilizers_ok,
        "independent_refinement_signatures": signatures,
        "cross_classes_separated": separated,
        "q4_sparse_dense_class_count": len(q4_shapes),
        "q4_sparse_dense_orbit_sum": q4_sum,
        "passed": passed,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
