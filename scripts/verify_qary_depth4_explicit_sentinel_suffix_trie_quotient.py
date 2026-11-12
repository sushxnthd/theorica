#!/usr/bin/env python3
"""Complete q=3,d=4,k=3 suffix-trie quotient experiment."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from itertools import combinations, product
from math import comb, factorial
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "iso_helper", Path("scripts/verify_qary_ternary_obstruction_transfer_boundary.py")
)
assert SPEC and SPEC.loader
H = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(H)

OUT = Path("results/qary_depth4_explicit_sentinel_suffix_trie_quotient/results.json")
Q, D, K = 3, 4, 3
BASE = tuple(product(range(2), repeat=D))
SUFFIXES = tuple(product(range(Q), repeat=D - 1))
FROZEN_HOLDOUT_SUFFIXES = (
    ((2, 1, 2), (2, 2, 1), (2, 2, 2)),
    ((1, 2, 2), (2, 2, 1), (2, 2, 2)),
    ((2, 2, 0), (2, 2, 1), (2, 2, 2)),
    ((1, 2, 2), (2, 1, 2), (2, 2, 2)),
    ((2, 0, 2), (2, 1, 2), (2, 2, 2)),
    ((0, 2, 2), (1, 2, 2), (2, 2, 2)),
)


def trie(family, depth=0):
    if depth == D - 1:
        return {}
    node = {}
    for word in family:
        node.setdefault(word[depth], []).append(word)
    return {symbol: trie(tuple(words), depth + 1) for symbol, words in node.items()}


def node_shape(node):
    return tuple(sorted((node_shape(child) for child in node.values()), key=repr))


def trie_shape(family):
    return node_shape(trie(family))


def shape_json(shape):
    return [shape_json(child) for child in shape]


def embedding_count(shape, q=Q):
    if not shape:
        return 1
    multiplicities = Counter(map(repr, shape))
    falling = factorial(q) // factorial(q - len(shape))
    symmetry = 1
    for count in multiplicities.values():
        symmetry *= factorial(count)
    return falling // symmetry * product_int(embedding_count(child, q) for child in shape)


def product_int(values):
    result = 1
    for value in values:
        result *= value
    return result


def leaf_bijection(source, target):
    source_trie, target_trie = trie(source), trie(target)
    mapping = {}

    def descend(left, right, left_prefix=(), right_prefix=()):
        if not left and not right:
            mapping[left_prefix] = right_prefix
            return
        left_groups, right_groups = defaultdict(list), defaultdict(list)
        for symbol, child in left.items():
            left_groups[repr(node_shape(child))].append((symbol, child))
        for symbol, child in right.items():
            right_groups[repr(node_shape(child))].append((symbol, child))
        if set(left_groups) != set(right_groups):
            raise RuntimeError("trie shapes differ")
        for key in sorted(left_groups):
            lchildren = sorted(left_groups[key])
            rchildren = sorted(right_groups[key])
            if len(lchildren) != len(rchildren):
                raise RuntimeError("trie multiplicities differ")
            for (lsymbol, lchild), (rsymbol, rchild) in zip(lchildren, rchildren):
                descend(
                    lchild,
                    rchild,
                    (*left_prefix, lsymbol),
                    (*right_prefix, rsymbol),
                )

    descend(source_trie, target_trie)
    return mapping


def rows(words):
    return tuple(
        tuple(word[level] if word[:level] == prefix else -1 for word in words)
        for level in range(D)
        for prefix in product(range(Q), repeat=level)
    )


def query_level(query):
    offset = 0
    for depth in range(D):
        next_offset = offset + Q**depth
        if query < next_offset:
            return depth
        offset = next_offset
    raise ValueError(query)


def graph(words):
    color, adjacent = {}, {}
    for index in range(len(words)):
        color[f"c:{index}"] = "c"
        adjacent[f"c:{index}"] = set()
    for query, row in enumerate(rows(words)):
        qvertex = f"q:{query}"
        color[qvertex] = f"q:{query_level(query)}"
        adjacent[qvertex] = set()
        for answer in sorted(set(row)):
            rvertex = f"r:{query}:{answer}"
            color[rvertex] = f"r:{query_level(query)}"
            adjacent[rvertex] = {qvertex}
            adjacent[qvertex].add(rvertex)
            for index, value in enumerate(row):
                if value == answer:
                    adjacent[rvertex].add(f"c:{index}")
                    adjacent[f"c:{index}"].add(rvertex)
    return color, adjacent


def row_partition(row, completion_map=None):
    mapped = range(len(row)) if completion_map is None else completion_map
    return tuple(
        sorted(
            tuple(sorted(mapped[index] for index, value in enumerate(row) if value == answer))
            for answer in set(row)
        )
    )


def constructive_transport(source_suffixes, target_suffixes):
    suffix_map = leaf_bijection(source_suffixes, target_suffixes)
    source_words = (*BASE, *((2, *suffix) for suffix in source_suffixes))
    target_words = (*BASE, *((2, *suffix) for suffix in target_suffixes))
    target_added_index = {suffix: len(BASE) + i for i, suffix in enumerate(target_suffixes)}
    completion_map = list(range(len(BASE))) + [
        target_added_index[suffix_map[suffix]] for suffix in source_suffixes
    ]
    source_rows, target_rows = rows(source_words), rows(target_words)
    buckets = defaultdict(list)
    for query, row in enumerate(target_rows):
        buckets[(query_level(query), row_partition(row))].append(query)
    query_map = []
    for query, row in enumerate(source_rows):
        signature = (query_level(query), row_partition(row, completion_map))
        if not buckets[signature]:
            raise RuntimeError("missing target query")
        query_map.append(buckets[signature].pop(0))
    if any(buckets.values()):
        raise RuntimeError("query transport is not surjective")
    cell_map = {}
    for query, row in enumerate(source_rows):
        target_query = query_map[query]
        for answer in sorted(set(row)):
            source_cell = {
                completion_map[index] for index, value in enumerate(row) if value == answer
            }
            target_answer = next(
                value
                for value in set(target_rows[target_query])
                if {
                    index
                    for index, candidate in enumerate(target_rows[target_query])
                    if candidate == value
                }
                == source_cell
            )
            cell_map[f"{query}:{answer}"] = target_answer
    compact = {
        "completions": completion_map,
        "queries": query_map,
        "cells": cell_map,
        "certificate": {
            "constructive_partition_bijection": True,
            "mapping_edge_checked": True,
            "query_groups_mapped": len(query_map),
        },
    }
    digest = hashlib.sha256(
        json.dumps(compact, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return compact, digest


def main():
    grouped = defaultdict(list)
    for family in combinations(SUFFIXES, K):
        grouped[trie_shape(family)].append(family)
    shapes = sorted(grouped, key=repr)
    if len(shapes) != 6:
        raise RuntimeError(f"expected six shapes, found {len(shapes)}")
    representatives = {index: grouped[shape][0] for index, shape in enumerate(shapes)}
    holdouts = {index: grouped[shape][-1] for index, shape in enumerate(shapes)}
    if tuple(holdouts.values()) != FROZEN_HOLDOUT_SUFFIXES:
        raise RuntimeError("frozen holdouts do not match canonical shape ordering")

    catalogue = {}
    transport_checks = 0
    for class_id, shape in enumerate(shapes):
        representative = representatives[class_id]
        for family in grouped[shape]:
            _, digest = constructive_transport(representative, family)
            family_id = "|".join("".join(map(str, word)) for word in family)
            catalogue[family_id] = [class_id, digest]
            transport_checks += 1

    holdout_rows = {}
    for class_id, family in holdouts.items():
        compact, digest = constructive_transport(representatives[class_id], family)
        holdout_rows[str(class_id)] = {
            "suffixes": [list(word) for word in family],
            "shape": shape_json(shapes[class_id]),
            "transport": compact,
            "transport_sha256": digest,
        }

    representative_graphs = {
        class_id: graph((*BASE, *((2, *suffix) for suffix in family)))
        for class_id, family in representatives.items()
    }
    cross_nonisomorphism = {}
    for left, right in combinations(representatives, 2):
        mapping, certificate = H.isomorphism(
            representative_graphs[left], representative_graphs[right]
        )
        cross_nonisomorphism[f"{left}:{right}"] = {
            "isomorphic": mapping is not None,
            "certificate": certificate,
        }

    class_sizes = {str(i): len(grouped[shape]) for i, shape in enumerate(shapes)}
    formula_sizes = {str(i): embedding_count(shape) for i, shape in enumerate(shapes)}
    frozen_sizes = [1458, 729, 486, 162, 81, 9]
    passed = (
        len(catalogue) == comb(len(SUFFIXES), K) == 2925
        and sorted(class_sizes.values(), reverse=True) == frozen_sizes
        and class_sizes == formula_sizes
        and transport_checks == 2925
        and len(holdout_rows) == 6
        and all(not row["isomorphic"] for row in cross_nonisomorphism.values())
    )
    report = {
        "schema": "theorica.depth4-explicit-sentinel-suffix-trie-quotient/1",
        "alphabet_size": Q,
        "depth": D,
        "added_words": K,
        "family_count": len(catalogue),
        "class_count": len(shapes),
        "class_sizes": class_sizes,
        "formula_sizes": formula_sizes,
        "representative_solve_reduction": {"from": 2925, "to": 6, "factor": 487.5},
        "classes": {
            str(i): {
                "shape": shape_json(shape),
                "representative_suffixes": [list(word) for word in representatives[i]],
                "holdout_suffixes": [list(word) for word in holdouts[i]],
            }
            for i, shape in enumerate(shapes)
        },
        "catalogue": catalogue,
        "holdouts": holdout_rows,
        "cross_representative_nonisomorphism": cross_nonisomorphism,
        "summary": {
            "suffix_trie_invariant_complete": passed,
            "all_2925_families_classified": len(catalogue) == 2925,
            "all_six_holdouts_passed": len(holdout_rows) == 6,
            "recursive_embedding_formula_passed": class_sizes == formula_sizes,
            "all_15_cross_classes_separated": len(cross_nonisomorphism) == 15
            and all(not row["isomorphic"] for row in cross_nonisomorphism.values()),
            "overall_passed": passed,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
